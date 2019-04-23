from flask import *
import json
import os
import operator
stats = Blueprint('stats', __name__, template_folder='views')


@stats.route('/stats',methods=["GET"])
def stats_route():

	stats_hash = read_stats()
	stats = {}
	totals = {}
	for data in stats_hash:
		totals[data["decade"]] = data["total"]
		for label in data["labels"]: #label0=record, label1=total
			if label[0] not in stats:
				stats[label[0]] = {}
			stats[label[0]][data["decade"]] = label[1]
	real_stats = []
	for label in stats:
		tot = 0
		for year in stats[label]:
			tot += stats[label][year]
		real_stats.append({"label": label, "data": stats[label], "total": tot})

	real_stats = sorted(real_stats, key=operator.itemgetter("total"), reverse=True)[:5]
	print(real_stats)
	return render_template("stats.html", stats=real_stats, totals=totals)

def read_stats():
	with open("stats.out") as fh:
		j = json.loads(fh.read())
	return j

def write_stats():
	decade_stats = []	
	for decade in range(1950, 2019, 10):
		labels = {}
		total_albums = 0
		for year in range(0, 10):
			if not os.path.isdir("decades/years/{}".format(decade+year)):
				continue
			artist = [ a for a in os.listdir("decades/years/{}".format(decade+year)) if a[0] != '.' and a != "failed" and a != "album_list" ]
			total_albums += len(artist)
			for a in artist:
				with open("decades/years/{}/{}/best_selling_albums.json".format(decade+year, a)) as fh:
					best_selling = json.loads(fh.read())
				try:
					for album in best_selling:
						if "label" not in best_selling[album]:
							pass
						
						check_label = best_selling[album]["label"].lower()
						check_label = fix_label(decade+year, check_label)
						if not check_label:
							continue
						if check_label not in labels:
							labels[check_label] = 0
						labels[check_label] += 1
				except:
					continue
		sort = sorted(labels.items(), key=operator.itemgetter(1), reverse=True)
		decade_stats.append({"decade": decade, "total": total_albums, "labels": sort})
		#print(decade, sort)
	with open("stats.out", "w") as fh:
		json.dump(decade_stats, fh, indent=4)
	
def fix_label(year, label):
	return label
	if label.find("arc") >= 0:
		pass
	elif label.find("bmg") >= 0 or label.find("rca") >= 0 or label.find("ariola") >= 0:
		# RCA/Ariola merged into BMG (1984)
		return "bmg records"
	elif label.find("sony") >= 0 or label.find("cbs") >= 0:
		return "sony music"

	elif label.find("warner bros") >= 0:
		return "warner bros records"
	elif label.find("american") >= 0:
		return "american records"
	elif label.find("decca") >= 0:
		return "decca records"
	elif label.find("mca") >= 0:
		return "mca music"
	elif label.find("columbia") >= 0:
		return "columbia records"
	elif label.find("prestige") >= 0:
		return "prestige records"
	elif label.find("verve") >= 0:
		return "verve records"
	elif label.find("emi") >= 0:
		return "emi records"
	elif label.find("universal") >= 0:
		return "universal music"
	elif label.find("polygram") >= 0:
		return "polygram records"
	
	elif label.find("sony") >= 0 or label.find("cbs") >= 0:
		return "sony music"

	return label


#write_stats()
