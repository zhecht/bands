
from bs4 import BeautifulSoup as BS
import urllib
import json
import operator
import string
import sys
import pprint
import datetime
from selenium import webdriver

def format_url(song, artist):
    artist = '-'.join(artist.lower().replace("\"", "").replace(",", "").replace("(", "").replace(")", "").replace("'", "").replace(".", "").replace("-", "").replace("?", "").replace("!", "").replace("_", "-").split())
    song = '-'.join(song.lower().replace("\"", "").replace(",", "").replace("(", "").replace(")", "").replace("'", "").replace(".", "").replace("-", "").replace("?", "").replace("!", "").split())
    return "http://www.metrolyrics.com/"+song+"-lyrics-"+artist+".html"

#http://www.metrolyrics.com/search.html?search=search
def write_lyrics(decades):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options, executable_path='/Users/zhecht/Downloads/chromedriver')
    for decade in decades:
        with open("decades/{}/tracklist.json".format(decade)) as fh:
            tracklist = json.loads(fh.read())

        lyric_links = {}
        #tracklist = {"Stadium Arcadium": {"She's Only 18": {"length": "3:44", "link": ""}}}
        for album in tracklist:
            all_songs = tracklist[album]
            for song in all_songs:
                href = None
                if all_songs[song]["link"]:
                    soup = BS(urllib.urlopen("https://en.wikipedia.org/{}".format(all_songs[song]["link"])).read(), "lxml")
                    external_links = soup.find_all("a", class_="external")                    
                    for link in external_links:
                        if link.text == "Lyrics of this song":
                            href = link.get("href")
                if not href:
                    #url = "http://www.metrolyrics.com/search.html?search={} - {}".format(song, decade)
                    #url = url.replace(" &", "")
                    #driver.get(url)
                    #html = driver.page_source
                    #soup = BS(html, "lxml")
                    #links = soup.find("div", class_="content").find_all("a")
                    #if len(links) > 0:
                    #    href = links[0].get("href")
                    href = format_url(song, decade)
                if href:
                    #print(song, href)
                    lyric_links[song] = href
        song_lyrics = {}

        print("Starting to write")
        for idx, song in enumerate(lyric_links):
            soup = BS(urllib.urlopen(lyric_links[song]).read(), "lxml")
            verses = [ v.text for v in soup.find_all("p", class_="verse") ]
            song_lyrics[song] = "\n\n".join(verses)

            if 0 and idx >= 10 and idx % 5 == 0:
                with open("decades/{}/lyrics.json".format(decade), "w") as fh:
                    json.dump(song_lyrics, fh, indent=4)

        with open("decades/{}/lyrics.json".format(decade), "w") as fh:
            json.dump(song_lyrics, fh, indent=4)

def read_stop_words():
    f = open("stop_words")
    #f = open("stop_words.txt")
    stop_words = {}
    for line in f:
        stop_words[line.rstrip()] = 1
    stop_words[""] = 1
    return stop_words

def write_word_counts(decades):
    stop_words = read_stop_words()
    
    for decade in decades:
        with open("decades/{}/lyrics.json".format(decade)) as fh:
            all_lyrics = json.loads(fh.read())
        decade_stats = {"total": {}, "unique": {}}
        for song in all_lyrics:
            song_words = []
            all_words = ' '.join(all_lyrics[song].split("\n")).lower().replace("\"", "").replace(",", "").replace("(", "").replace(")", "").replace("'", "").replace(".", "").replace("-", "").replace("?", "").replace("!", "").split(" ")
            for word in all_words:
                if len(word) <= 3 or word in stop_words:
                    continue
                if word not in decade_stats["total"]:
                    decade_stats["total"][word] = 0
                    decade_stats["unique"][word] = 0

                decade_stats["total"][word] += 1
                if word not in song_words:
                    decade_stats["unique"][word] += 1
                song_words.append(word)

        with open("decades/{}/word_count.json".format(decade), "w") as fh:
            json.dump(decade_stats, fh, indent=4)

def read_word_counts(decades):
    stop_words = read_stop_words()

    total_word_counts = {"unique": {}, "total": {}}
    for decade in decades:
        with open("decades/{}/word_count.json".format(decade)) as fh:
            word_counts = json.loads(fh.read())
        for word in word_counts["unique"]:
            if len(word) <= 3 or word in stop_words:
                continue
            if word not in total_word_counts["unique"]:
                total_word_counts["unique"][word] = 0
                total_word_counts["total"][word] = 0

            total_word_counts["unique"][word] += word_counts["unique"][word]
            total_word_counts["total"][word] += word_counts["total"][word]
        #print(decade, sorted(word_counts["unique"].items(), key=operator.itemgetter(1), reverse=True)[:10])
    
    print("TOTAL", sorted(total_word_counts["unique"].items(), key=operator.itemgetter(1), reverse=True)[:20])

def write_word_counts_by_song(decades):
    stop_words = read_stop_words()
    for decade in decades:
        all_stats = {}
        word_hash = {}
        unique_words = {}
        with open("decades/{}/lyrics.json".format(decade)) as fh:
            all_lyrics = json.loads(fh.read())
        with open("decades/{}/tracklist.json".format(decade)) as fh:
            tracklist = json.loads(fh.read())

        for album in tracklist:
            all_songs = tracklist[album]
            all_stats[album] = {}
            unique_words[album] = {}
            for song in all_songs:
                if song not in all_lyrics:
                    continue
                all_words = ' '.join(all_lyrics[song].split("\n")).lower().replace("\"", "").replace(",", "").replace("(", "").replace(")", "").replace("'", "").replace(".", "").replace("-", "").replace("?", "").replace("!", "").split(" ")
                duplicate_words = {}
                for word in all_words:
                    if not word:
                        continue
                    if word not in all_stats[album]:
                        all_stats[album][word] = 0
                        unique_words[album][word] = 0
                    if word not in word_hash:
                        word_hash[word] = 0
                    if word not in duplicate_words:
                        unique_words[album][word] += 1
                    all_stats[album][word] += 1                    
                    word_hash[word] += 1
                    duplicate_words[word] = 1
        
        with open("decades/{}/word_count.json".format(decade), "w") as fh:
            json.dump(all_stats, fh, indent=4)
        with open("decades/{}/unique_words.json".format(decade), "w") as fh:
            json.dump(unique_words, fh, indent=4)
        with open("decades/{}/all_words.json".format(decade), "w") as fh:
            json.dump(word_hash, fh, indent=4)

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

def read_word_counts_by_song(decades):
    stop_words = read_stop_words()

    word_stats = {}
    for decade in decades:
        with open("decades/{}/tracklist.json".format(decade)) as fh:
            tracklist = json.loads(fh.read())
        #with open("decades/{}/unique_words.json".format(decade)) as fh:
        with open("decades/{}/word_count.json".format(decade)) as fh:
            word_counts = json.loads(fh.read())
        with open("decades/{}/all_words.json".format(decade)) as fh:
            all_words = json.loads(fh.read())
        with open("decades/{}/album_length.json".format(decade)) as fh:
            album_lengths = json.loads(fh.read())

        #if len(word) <= 3 or word in stop_words:
            #continue
        total_word_counts = {}
        for album in word_counts:
            total_word_counts[album] = 0
            for word in word_counts[album]:
                total_word_counts[album] += word_counts[album][word]

        sorted_all_words = sorted(all_words.items(), key=operator.itemgetter(1), reverse=True)
        check_word = sorted_all_words[0][0]
        total_checked_words = 0

        while total_checked_words < 50:
            for word in sorted_all_words:
                if word[0] not in stop_words and word[0] != "voice":
                    check_word = word[0]
                    stop_words[check_word] = 1
                    total_checked_words += 1
                    break

            #check_word = ""
            arr = []
            sorted_albums = sort_albums_by_year(decade, album_lengths)
            for album in sorted_albums:
                if check_word in word_counts[album]:
                    #word_perc = round(word_counts[album][check_word] / float(len(tracklist[album].keys())), 2)
                    #word_perc = word_counts[album][check_word] / float(total_word_counts[album] - word_counts[album][check_word])
                    #word_perc = word_counts[album][check_word] / float(album_lengths[album]["minutes"] * 60 + album_lengths[album]["seconds"])
                    word_perc = word_counts[album][check_word]
                    arr.append({'album': album, 'count': word_perc})
                    #print(album, word_counts[album][check_word])
            word_stats[check_word] = arr

            #print(check_word)
    return word_stats
    #print("TOTAL", sorted(total_word_counts["unique"].items(), key=operator.itemgetter(1), reverse=True)[:20])


if __name__ == '__main__':
    # takes a really long time

    decades = ["1960s", "1970s", "1980s", "1990s", "2000s", "2010s"]
    decades = ["Led_Zeppelin"]
    decades = ["John_Frusciante"]

    if len(sys.argv) > 1:
        decades = [ sys.argv[1] ]
    
    write_lyrics(decades)
    write_word_counts_by_song(decades)
    #x = read_word_counts_by_song(decades)
    #pprint.pprint(x.keys())


