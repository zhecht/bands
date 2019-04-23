from bs4 import BeautifulSoup as BS
import urllib
import os
import json

j = {}
for decade in range(1950, 2020, 10):
    tot_missing = 0
    total = 0
    a = []
    for year in range(10):
        i = decade + year
        if not os.path.isdir("decades/years/{}".format(i)):
        	continue
        for artist in os.listdir("decades/years/{}".format(i)):
            if not os.path.exists("decades/years/{}/{}/best_selling_albums.json".format(i, artist)):
                continue
            with open("decades/years/{}/{}/best_selling_albums.json".format(i, artist)) as fh:
                best = json.loads(fh.read())
            for album in best:
                total += 1
                if "label" not in best[album] or not best[album]["label"]:
                    tot_missing += 1
                    a.append(best[album]["link"])
    j[decade] = a
    print("{} missing {}/{}".format(decade, tot_missing, total))

with open("out.json", "w") as fh:
    json.dump(j, fh, indent=4)