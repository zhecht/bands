import argparse
import wikipedia

from bs4 import BeautifulSoup as BS
import urllib
import json
import os
import re
import sys
from datetime import *

def fix_date(date_str):
    try:
        if date_str.startswith('(') and date_str.endswith(')'):
            return date_str[1:-1]
    except:
        m = re.search(r'\((.*?)\)', date_str)
        if not m:
            return datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d") # format is in February 28, 1974
        # format is in February 28, 1974(1974-2-28) (Aged 75)
        date_str = m.group(1)
    return date_str

def make_datetime(date):
    try:
        split_date = map(int, date.split('-'))
    except:
        m = re.search(r'\((.*?)\)', date)
        if not m:
            return datetime.strptime(date, "%B %d, %Y") # format is in February 28, 1974
        # format is in February 28, 1974(1974-2-28) (Aged 75)
        split_date = map(int, m.group(1).split('-'))

    if len(split_date) < 3:
        return datetime(split_date[0], 1, 1)

    return datetime(split_date[0], split_date[1], split_date[2])

def get_age(born, died):
    if died == 0:
        delta = datetime.now() - make_datetime(born)
    else:
        delta = make_datetime(died) - make_datetime(born) 
    return delta.days

if __name__ == "__main__":

    write_bands = 0
    write_age = 0
    write_best_selling = 1
    write_albums = 0

    artist = "John_Frusciante"

    if len(sys.argv) > 1:
        artist = sys.argv[1]

    if write_albums:
        discog_link = "https://en.wikipedia.org/wiki/{}_discography".format(artist)
        soup = BS(urllib.urlopen(discog_link).read(), "lxml")
        all_rows = soup.find("table", class_="wikitable").find_all("tr")[1:]

        album_dict = {}
        for row in all_rows:
            album = row.find("a").text
            album_link = row.find("a").get("href")
            info = row.find("td").find_all("li")[1].text
            date = info.split("Released: ")[1]
            date = date.split(" (US)")[0].split("(US)")[0]

            try:
                dt = datetime.strptime(date, "%d %B %Y")
            except:
                if date == '2001':
                    dt = datetime.strptime("August 1, 2001", "%B %d, %Y")
                else:
                    dt = datetime.strptime(date, "%B %d, %Y")
            album_dict[album] = {"link": album_link, "artist": artist, "date": dt.strftime("%m-%d-%Y")}

        if not os.path.isdir("decades/{}".format(artist)):
            os.mkdir("decades/{}".format(artist))

        with open("decades/{}/best_selling_albums.json".format(artist), "w") as fh:
            json.dump(album_dict, fh, indent=4)
    elif write_best_selling_song:
        for year in range(1950, 2019):
            html = urllib.urlopen("https://en.wikipedia.org/w/index.php?title=Category:{}_songs".format(year))
            soup = BS(html.read(), "lxml")
            trs = soup.find("table", class_="wikitable").find_all("tr")[1:]
            link_exists = {}
            best_selling_albums = {}
            seen = 0
            for row in trs:
                #if seen == 10:
                #    break
                tds = row.find_all("td")
                links = row.find_all("a")
                # Get album and album link
                album = tds[0].text.rstrip()
                try:
                    album_link = link_exists[album]
                except:
                    try:
                        album_link = tds[0].find("a").get("href")
                        link_exists[album] = album_link
                    except:
                        continue
                # Get artist
                artist = tds[1].text.rstrip()

                if artist.lower() == "original soundtrack" or artist.lower() == "original broadway cast" or artist.lower() == "original london cast" or artist.lower() == "various artists":
                    continue
                try:
                    artist_link = link_exists[artist]
                except:
                    artist_link = tds[1].find("a").get("href")
                    link_exists[artist] = artist_link

                seen += 1
                best_selling_albums[album] = { "link": album_link, "artist": artist, "artist_link": artist_link }

            with open("decades/{}/best_selling_albums.json".format(decade), "w") as fh:
                json.dump(best_selling_albums, fh, indent=4)
    elif write_best_selling:
        for year in range(1970, 2019):
            html = urllib.urlopen("https://en.wikipedia.org/w/index.php?title=Category:{}_albums".format(year))
            soup = BS(html.read(), "lxml")
            trs = soup.find("table", class_="wikitable").find_all("tr")[1:]
            link_exists = {}
            best_selling_albums = {}
            seen = 0
            for row in trs:
                #if seen == 10:
                #    break
                tds = row.find_all("td")
                links = row.find_all("a")
                # Get album and album link
                album = tds[0].text.rstrip()
                try:
                    album_link = link_exists[album]
                except:
                    try:
                        album_link = tds[0].find("a").get("href")
                        link_exists[album] = album_link
                    except:
                        continue
                # Get artist
                artist = tds[1].text.rstrip()

                if artist.lower() == "original soundtrack" or artist.lower() == "original broadway cast" or artist.lower() == "original london cast" or artist.lower() == "various artists":
                    continue
                try:
                    artist_link = link_exists[artist]
                except:
                    artist_link = tds[1].find("a").get("href")
                    link_exists[artist] = artist_link

                seen += 1
                best_selling_albums[album] = { "link": album_link, "artist": artist, "artist_link": artist_link }

            with open("decades/{}/best_selling_albums.json".format(decade), "w") as fh:
                json.dump(best_selling_albums, fh, indent=4)

    elif write_age:
        age_hash = {}
        with open("1960_members.json") as fh:
            all_bands = json.loads(fh.read())

        #all_bands = {"Led Zeppelin": {"John Paul Jones": "/wiki/John_Paul_Jones_(musician)", "John Bonham": "/wiki/John_Bonham", "Jimmy Page": "/wiki/Jimmy_Page", "Robert Plant": "/wiki/Robert_Plant"}}

        for band in all_bands:
            age_hash[band] = {}
            all_members = all_bands[band]
            if len(all_members) > 3:
                # Loop through each member
                for member in all_members:
                    if all_members[member].find("/wiki/") != -1: # If page exists
                        html = urllib.urlopen("https://en.wikipedia.org{}".format(all_members[member]))
                        soup = BS(html.read(), "lxml")
                        infobox = soup.find("table", class_="infobox")

                        if not infobox:
                            continue
                        all_rows = infobox.find_all("tr")
                        born = 0
                        died = 0
                        instruments = ""
                        for row in all_rows:
                            try:
                                if row.find("th").text.lower().find("born") != -1:
                                    born = fix_date(row.find("span", class_="bday").text)
                                elif row.find("th").text.lower().find("died") != -1:
                                    died = fix_date(row.find("span").text)
                                elif row.find("th").text.lower().find("instruments") != -1:
                                    instruments = [ i.text.lower() for i in row.find_all("li") ]
                                    if len(instruments) == 0:
                                        text = row.find("td").text.lower()
                                        if text.find(', ') != -1:
                                            instruments = text.split(', ')
                                        else:
                                            instruments = text.split(',')
                            except:
                                pass
                        if born != 0:
                            age_hash[band][member] = { "born": born, "died": died, "instruments": instruments, "age": get_age(born, died) }

        with open("1960_ages.json", "w") as fh:
            json.dump(age_hash, fh, indent=4)

    elif write_bands:
        html = urllib.urlopen("https://en.wikipedia.org/wiki/List_of_1960s_musical_artists")
        soup = BS(html.read(), "lxml")

        all_links = soup.find_all("a")[19:]
        link_hash = {}

        for a in all_links:
            if a.text and a.text != "Edit" and a.get("href") and a.get("href").find("/wiki/") == 0:
                a.text.replace("\"", "'")
                link_hash[a.text] = a.get("href")

        with open("1960_bands.json", "w") as fh:
            json.dump(link_hash, fh, indent=4)

    else:
        with open("1960_bands.json") as fh:
            all_bands = json.loads(fh.read())

        band_members = {}
        for idx, band in enumerate(all_bands):
            print("{}/{} ==> {}%".format(idx, len(all_bands), float(idx) / len(all_bands)))
            url = "https://en.wikipedia.org{}".format(all_bands[band])
            html = urllib.urlopen(url)
            soup = BS(html.read(), "lxml")
            infobox = soup.find("table", class_="infobox")

            if not infobox:
                continue
            all_rows = infobox.find_all("tr")
            
            members = {}
            for row in all_rows:
                try:
                    if row.find("th").text.lower().find("members") != -1:
                        all_data = row.find_all("a")
                        for link in all_data:
                            members[link.text] = link.get("href")
                except:
                    pass
            band_members[band] = members

        with open("1960_members.json", "w") as fh:
            json.dump(band_members, fh, indent=4)





































