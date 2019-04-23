from flask import *
from controllers.best_selling import *
from controllers.lyrics import *
from statistics import mean, median 
main = Blueprint('main', __name__, template_folder='views')

@main.route('/',methods=["GET"])
def main_route():
	#stats = best_selling.read_album_lengths(["Red_Hot_Chili_Peppers"])
	#stats = best_selling.read_album_lengths(["Led_Zeppelin"])
	#x_axis, y_axis, mean_y_axis = prepare_graph_data(stats)
	
	words = []
	artist = "Red_Hot_Chili_Peppers"	
	artist = "Led_Zeppelin"
	artist = "John_Frusciante"
	graph, rank_data = box_graph(artist)

	medians = []
	for album_arr in graph:
		lengths_arr = [ l["seconds"] for l in album_arr["lengths"] ]
		med = median(lengths_arr)
		medians.append(med)
	print(calc_R(medians))


	lyric_stats = read_word_counts_by_song([artist])
	words, x_axis, y_axis = prepare_lyric_data(lyric_stats)

	return render_template("main.html", words=words, x_axis = x_axis, y_axis = y_axis, graph=graph, ranks=rank_data, artist=artist)

def box_graph(artist):
	with open("decades/{}/tracklist.json".format(artist)) as fh:
		tracklist = json.loads(fh.read())
	with open("decades/{}/album_length.json".format(artist)) as fh:
		album_lengths = json.loads(fh.read())

	graph = []
	rank_data = []
	sorted_albums = sort_albums_by_year(artist, album_lengths)
	for album in sorted_albums:
		lengths = []
		ranks = []
		for song in tracklist[album]:
			minutes, seconds = map(int, tracklist[album][song]["length"].split(":"))
			lengths.append({"name": song, "seconds": minutes * 60 + seconds})
			ranks.append(minutes * 60 + seconds)
		rank_data.append({"name": album, "ranks": sorted(ranks)})
		graph.append({"name": album, "lengths": lengths})
	#print(rank_data)
	return graph, rank_data

def prepare_lyric_data(all_data):
	all_x_axis = []
	all_y_axis = []
	all_words = []
	for word in all_data:
		x_axis = []
		y_axis = []
		for data in all_data[word]:
			x_axis.append(str(data["album"]))
			y_axis.append(str(data["count"]))
		
		all_words.append(word)
		all_x_axis.append(','.join(x_axis))
		all_y_axis.append(','.join(y_axis))
	return ','.join(all_words), '~'.join(all_x_axis), '~'.join(all_y_axis)

def prepare_graph_data(all_data):
	x_axis = []
	y_axis = []
	mean_y_axis = []
	for data in all_data:
		x_axis.append(str(data["album"]))
		y_axis.append(str(data["median"]))
		mean_y_axis.append(str(data["mean"]))
	return ','.join(x_axis), ','.join(y_axis), ','.join(mean_y_axis)


def deviation_squared(data, mean):
	sum_ = 0
	for i in data:
		sum_ += pow(i - mean, 2)
	return sum_

def deviation_combined(x_data, y_data, x_mean, y_mean):
	sum_ = 0
	for idx, val in enumerate(x_data):
		sum_ += ((val - x_mean) * (y_data[idx] - y_mean))
	return sum_

def calc_R(x_data):
	y_data = []
	for idx, x in enumerate(x_data):
		y_data.append(idx)

	x_mean = mean(x_data)
	x_deviation = deviation_squared(x_data, x_mean)
	y_mean = mean(y_data)
	y_deviation = deviation_squared(y_data, y_mean)
	combined = deviation_combined(x_data, y_data, x_mean, y_mean)
	r = combined / pow(x_deviation * y_deviation, 0.5)
	return r
