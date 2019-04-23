from bs4 import BeautifulSoup as BS
import json
import math
import pprint
import re
import sys
import operator
import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def write_tracklist(decades):
    conn = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    for decade in decades:
        #decade_text = 
        
        with open("decades/{}/best_selling_albums.json".format(decade)) as fh:
            best_selling = json.loads(fh.read())
        
        tracklist = {}
        for album in best_selling:
            r = conn.request("GET", "https://en.wikipedia.org/{}".format(best_selling[album]["link"]))
            soup = BS(r.data, "lxml")
            seen_side_A = False
            tracklist_tables = soup.find_all("table", class_="tracklist")

            try:
                duration = soup.find("span", class_="duration")
                total_length = int(duration.find("span", class_="min").text) * 60 + int(duration.find("span", class_="s").text)
            except:
                total_length = 10000

            tracklist[album] = {}
            curr_length = 0

            #print(album, len(tracklist_tables))
            if len(tracklist_tables) == 0 or 'floatright' in tracklist_tables[0].get('class'): #no table
                try:
                    tracklist_span = soup.find("span", id="Track_listing").parent
                except:
                    continue

                for idx, el in enumerate(tracklist_span.next_elements):
                    #print(idx, el)
                    if el.name == "ol":
                        li = el.find_all("li")
                        for song in li:
                            if song.get('class') and 'mw-empty-elt' in song.get('class'):
                                continue                            
                            if curr_length + 60 > total_length:
                                break
                            link = ""
                            try:
                                title = song.find("a").text
                                link = song.find("a").get("href")
                                if link.find("cite_note") != -1:
                                    title = song.text.rstrip()[:-3]
                                    link = ""
                            except:
                                title = song.text.rstrip()

                            if title in ['^', 'a']:
                                continue
                            title = title.replace("\"", "")
                            try:
                                if title.find(" - ") != -1:
                                    length = song.text.split(" - ")[-1]
                                elif title.find(u"\u2013") != -1:
                                    arr = title.split(" \u2013 ")
                                    title = arr[0].replace("\"", "")
                                    if title.find("\xa0") != -1:
                                        arr = title.split("\xa0\u2013 ")
                                        title = arr[0]      

                                    #print(arr, title.split("\xa0"))
                                    length = arr[1]
                                elif title.find("\xa0") != -1:
                                    sp = title.split("\xa0")
                                    title = sp[0]
                                    length = sp[1]
                            except:
                                continue

                            #print(length)
                            if not length:
                                continue
                            if length[-1] == ']':
                                length = length[:-3]
                            if length.find("(") != -1:
                                length = length.split(" (")[0]

                            if length.find(" or ") != -1:
                                length = length.split(" or ")[0]

                            try:
                                length_arr = map(int, length.split(":"))
                                tracklist[album][title] = {"length": length, "link": link}
                                curr_length += (length_arr[0] * 60 + length_arr[1])
                            except:
                                pass

            for table in tracklist_tables:
                if 'collapsed' in table.get('class'):
                    continue
                rows = table.find_all("tr")
                for row in rows:
                    if curr_length + 60 > total_length:
                        break
                    headers = row.find_all("th")
                    if len(headers) == 1:
                        which_side = headers[0].text.rstrip() # Side A or Side B
                        if which_side.lower() == "side a" or which_side.lower() == "side one":
                            if seen_side_A:
                                break
                            seen_side_A = True
                    elif len(headers) == 0:
                        # tracks
                        tds = row.find_all("td")
                        length = tds[-1].text

                        if length[-1] == ']':
                            length = length[:-3]

                        link = ""
                        if tds[-2].text.rstrip() != "Total length:":
                            try:
                                title = tds[1].find("a").text
                                link = tds[1].find("a").get("href")
                                if link.find("cite_note") != -1:
                                    title = tds[1].text.rstrip()[:-3]
                                    link = ""
                            except:
                                title = tds[1].text.rstrip()[1:-1]

                            if title[-1] == ']':
                                title = title[:-3]
                            try:
                                m = re.search(r'"(.*)"', tds[1].text)
                                title = m.group(0).replace("\"", "")
                            except:
                                continue

                            if title.find(u"\u2013") != -1:
                                sp = title.split(" \u2013 ")
                                title = sp[0].replace("\"", "")
                                #print(song.text.split(" \u2013 "))
                                length = sp[1]                        
                            try:
                                minutes, seconds = map(int, length.split(":"))
                                curr_length += (minutes * 60 + seconds)
                                tracklist[album][title] = {"length": length, "link": link}
                            except:
                                pass

        with open("decades/{}/tracklist.json".format(decade), "w") as fh:
            json.dump(tracklist, fh, indent=4)


def write_album_lengths(decades):
    for decade in decades:
        with open("decades/{}/best_selling_albums.json".format(decade)) as fh:
            best_selling_albums = json.loads(fh.read())
        with open("decades/{}/tracklist.json".format(decade)) as fh:
            tracklist = json.loads(fh.read())

        song_lengths = {}
        for album in tracklist:
            total_minutes = 0
            total_seconds = 0
            total_songs = len(tracklist[album])
            length_arr = []

            for song in tracklist[album]:
                minutes, seconds = map(int, tracklist[album][song]["length"].split(":"))
                total_minutes += minutes
                total_seconds += seconds
                length_arr.append(seconds + (minutes * 60))
            
            extra_minutes = math.floor(total_seconds / 60)
            total_minutes += extra_minutes
            total_seconds -= (extra_minutes * 60)
            
            song_lengths[album] = {
                "total_songs": total_songs,
                "minutes": total_minutes,
                "seconds": total_seconds,
                "length_arr": length_arr
            }
            
        with open("decades/{}/album_length.json".format(decade), "w") as fh:
            json.dump(song_lengths, fh, indent=4)
      
def format_seconds(sec):
    minutes = int(sec) / 60
    seconds = sec - minutes * 60
    return "{}:{}".format(minutes, int(seconds))

def sort_albums_by_year(band, all_lengths):
    with open("decades/{}/best_selling_albums.json".format(band)) as fh:
        album_years = json.loads(fh.read())
    sorted_albums = []
    for album in album_years:
        mo, day, year = map(int, album_years[album]["date"].split("-"))
        sec = (datetime.datetime(year, mo, day) - datetime.datetime(1970,1,1)).total_seconds()
        sorted_albums.append({"sec": sec, "album": album})
    sorted_albums = sorted(sorted_albums, key=operator.itemgetter("sec"))
    albums = []
    for album in sorted_albums:
        albums.append(album["album"])
    return albums

def print_album_length(album, length_arr):
    total_seconds = 0
    for song_length in length_arr:
        total_seconds += song_length
    song_length = sorted(length_arr)
    if len(song_length) % 2 == 1:
        median = song_length[len(song_length) / 2]
    else:
        median = 0.5 * song_length[len(song_length) / 2 - 1] + song_length[len(song_length) / 2]

    mean = round(total_seconds / float(len(length_arr)), 2)
    #mean = format_seconds(mean)
    #median = format_seconds(median)
    print("{}\n\tmean: {}, median = {}".format(album, mean, median))
    return mean, median

def read_album_lengths(decades):
    for decade in decades:
        with open("decades/{}/album_length.json".format(decade)) as fh:
            album_lengths = json.loads(fh.read())

        total_songs = 0
        total_seconds = 0
        all_lengths = []
        sorted_albums = sort_albums_by_year(decade, album_lengths)
        all_stats = []
        for album in sorted_albums:
            total_songs += album_lengths[album]["total_songs"]
            total_seconds += (album_lengths[album]["minutes"] * 60) + album_lengths[album]["seconds"]
            all_lengths += album_lengths[album]["length_arr"]
            mean, median = print_album_length(album, album_lengths[album]["length_arr"])
            all_stats.append({"album": album, "median": median, "mean": mean})

        all_lengths = sorted(all_lengths)
        if len(all_lengths) % 2 == 1:
            median = all_lengths[len(all_lengths) / 2]
        else:
            median = 0.5 * all_lengths[len(all_lengths) / 2 - 1] + all_lengths[len(all_lengths) / 2]

        print("{} averaged {} seconds per song ; median = {}".format(decade, format_seconds(total_seconds / float(total_songs)), format_seconds(median)))
    return all_stats



if __name__ == '__main__':
    decades = ["Led_Zeppelin"]
    decades = ["Red_Hot_Chili_Peppers"]
    decades = ["John_Frusciante"]

    #decades = ["1960s", "1970s", "1980s", "1990s", "2000s", "2010s"]

    if len(sys.argv) > 1:
        decades = [ sys.argv[1] ]
    #write_tracklist(decades)
    write_album_lengths(decades)
    #read_album_lengths(decades)

    





            

