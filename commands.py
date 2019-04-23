
from bs4 import BeautifulSoup as BS
from datetime import *
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.dummy import *

import re
import json
import os

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#import controllers.best_selling


def write_list(which):
	conn = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
	for year in range(1950, 1960):
		next_page_link = ""
		first = True
		while next_page_link is not None:
			if next_page_link == "":
				next_page_link = "/w/index.php?title=Category:{}_{}s".format(year, which)
			url = "https://en.wikipedia.org{}".format(next_page_link).split("#")[0]
			r = conn.request("GET", url)
			soup = BS(r.data, "lxml")

			pages_table = soup.find("div", id="mw-pages")
			all_li = pages_table.find_all("li")
			albums = []
			for li in all_li:
				link = li.find("a")
				albums.append({"name": link.text, "url": link.get("href")})

			if not os.path.exists("decades/years/{}".format(year)):
				os.mkdir("decades/years/{}".format(year))
			
			mode = "a"
			if first:
				first = False
				mode = "w"
			
			with open("decades/years/{}/{}_list".format(year, which), mode) as fh:
				for album in albums:
					try:
						fh.write("{}\t{}\n".format(album["name"], album["url"]))
					except:
						pass
						#print(album)
			#print(next_page_link)
			found = 0
			for elem in soup(text=re.compile(r'next page')):
				#print(elem.parent)
				found = 1
				next_page_link = elem.parent.get("href")
				break
			
			if not found:
				break


def get_dt(date):
	try:
		dt = datetime.strptime(date, "%d %B %Y")
	except:
		try:
			dt = datetime.strptime(date, "%Y")
		except:
			try:
				dt = datetime.strptime(date, "%B %d, %Y")
			except:
				try:
					dt = datetime.strptime(date, "%B %Y")
				except:
					try:
						dt = datetime.strptime(date, "%b %Y")
					except:
						return None
	return dt

def get_html(year):
	r = requests.get("")

def get_list(which, year):
	data = {}
	with open("decades/years/{}/{}_list".format(year, which)) as fh:
		for line in fh:
			name, url = line.split("\t")
			data[name] = url
	return data

def write_artists_thread():
	all_p = []
	pool = Pool()
	for year in range(1950, 2019):
		pool.apply_async(write_artists, args=(year,))
	pool.close()
	pool.join()


def write_artists(year):
	failed = {}
	conn = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
	albums = get_list("album", year)
	for album in albums:
		url = albums[album].rstrip()
		r = conn.request("GET", "https://en.wikipedia.org{}".format(url))
		soup = BS(r.data, "lxml")
		
		try:
			artist = soup.find("div", class_="contributor").find("a").text
			published = soup.find("td", class_="published").text
		except:
			failed[album] = "LINE96: "+url
			continue
		try:
			label = soup.find("a", title="Record label").parent.next_sibling.find("a").get("title")
		except:
			try:
				label = soup.find("a", title="Record label").parent.next_sibling.text
			except:
				label = ""

		try:
			producer = soup.find("a", title="Record producer").parent.next_sibling.text
		except:
			producer = ""
		
		try:
			genre = ",".join([ li.find("a").text for li in soup.find("a", title="Music genre").parent.next_sibling.find_all("li") ])
		except:
			try:
				genre = soup.find("a", title="Music genre").parent.next_sibling.text
			except:
				genre = ""

		try:
			p = soup.find("span", id="Personnel")
			if p:
				for el in p.parent.next_sibling:
					if el.name == 'h2':
						break
					elif el.name == 'ul':
						all_li = el.find_all("li")
						for li in all_li:
							name = li.text
							a = li.find("a")
							if a:
								name = str(a)+a
						break

		except:
			personnel = []
		#date = published.split("Released: ")[1]
		date = published.split(" [")[0]
		dt = get_dt(date)
		if dt is None:
			dt = datetime.strptime(str(year), "%Y")

		album_dict = {}
		artist_formatted = artist.replace(" ", "_")
		try:
			if not os.path.exists("decades/years/{}/{}".format(year, artist_formatted)):
				os.mkdir("decades/years/{}/{}".format(year, artist_formatted))
			else:
				with open("decades/years/{}/{}/best_selling_albums.json".format(year, artist_formatted)) as fh:
					album_dict = json.loads(fh.read())
		except:
			pass
			#continue

		if album in album_dict:
			#continue
			pass
		album_dict[album] = {"link": url.rstrip(), "artist": artist, "date": dt.strftime("%m-%d-%Y"), "label": label, "genre": genre, "producer": producer}
		try:
			with open("decades/years/{}/{}/best_selling_albums.json".format(year, artist_formatted), "w") as fh:
				json.dump(album_dict, fh, indent=4)
		except:
			pass
	with open("decades/years/{}/failed".format(year), "w") as fh:
		json.dump(failed, fh, indent=4)	
		
		#exit()

def write_tracklist():
	pool = Pool()
	for year in range(1950, 2019):
		#print(year)
		artists = [ "years/{}/".format(year) + artist for artist in os.listdir("decades/years/{}".format(year)) if os.path.isdir("decades/years/{}/{}".format(year, artist)) ]
		pool.apply_async(controllers.best_selling.write_tracklist, args=(artists, ))
		#controllers.best_selling.write_tracklist(artists)
	pool.close()
	pool.join()

def write_album_lengths():
	for year in range(1950, 2019):
		#print(year)
		artists = [ "years/{}/".format(year) + artist for artist in os.listdir("decades/years/{}".format(year)) if os.path.isdir("decades/years/{}/{}".format(year, artist)) ]
		controllers.best_selling.write_album_lengths(artists)


#write_list("album")
#write_song_list()

#write_artists_thread()
#write_tracklist()
#write_album_lengths()



