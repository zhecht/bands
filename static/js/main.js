

var percentiles_graph = [];
var percentiles = [75, 50, 25];
var highest_percentile = 0;

for (var p = 0; p < percentiles.length; ++p) {
	var trace = {
		x: [], 
		y: [], 
		mode: 'lines+markers', 
		name: percentiles[p] + 'th percentile', 
		text: [], 
		type: 'scatter', 
		hoverinfo: 'text',
		uid: '8b99bc'
	};
	for (var i = 0; i < albums.length; ++i) {
		var rank = (percentiles[p] / 100) * (traces[i]["y"].length + 1);
		var score;
		if (Number.isInteger(rank)) {
			score = ranks[albums[i]][rank];
		} else {
			var int_rank = Math.floor(rank);
			var frac_rank = rank - Math.floor(rank);
			var lower_score = ranks[albums[i]][int_rank];
			var higher_score = ranks[albums[i]][int_rank + 1];

			score = frac_rank * (higher_score - lower_score) + lower_score;
		}
		trace["text"].push(format_sec(score));
		trace["x"].push(i);
		trace["y"].push(score);
		if (score > highest_percentile) {
			highest_percentile = score;
		}
	}
	console.log(percentiles[p]+"% = "+ calculate_R(trace["y"]));
	percentiles_graph.push(trace);

}

var layout = {
	title: 'Percentiles',
	xaxis: {
		tickvals:[],
		ticktext:[]
	},
	yaxis: {
		tickvals:[],
		ticktext:[]
	}
}
for (var i = 0; i < albums.length; ++i) {
	layout["xaxis"]["tickvals"].push(i);
	layout["xaxis"]["ticktext"].push(htmlDecode(albums[i]));
}
for (var i = 0; i < highest_percentile; i += 61) {
	layout["yaxis"]["tickvals"].push(i);
	layout["yaxis"]["ticktext"].push((i % 60) + ":00");
}

Plotly.plot('percentiles', percentiles_graph, layout);


var input = document.getElementById("word_search");
new Awesomplete(input, {list: "#word_list"});




function average(arr) {
	var sum = 0;
	for (var i = 0; i < arr.length; ++i) {
		sum += parseFloat(arr[i]);
	}
	return sum / arr.length;
}

function deviation_squared(arr, mean) {
	var sum = 0;
	for (var i = 0; i < arr.length; ++i) {
		sum += Math.pow((parseFloat(arr[i]) - mean), 2);
	}
	return sum;
}

function deviation_combined(x_axis, y_axis, x_mean, y_mean) {
	var sum = 0;
	for (var i = 0; i < x_axis.length; ++i) {
		sum += ((x_axis[i] - x_mean) * (y_axis[i] - y_mean));
	}
	return sum;
}

function calculate_R(x_axis) {
	var y_axis = [];
	for (var i = 0; i < x_axis.length; ++i) {
		y_axis.push(i);
	}
	var x_mean = average(x_axis);
	var x_deviation = deviation_squared(x_axis, x_mean);
	var y_mean = average(y_axis);
	var y_deviation = deviation_squared(y_axis, y_mean);
	var combined = deviation_combined(x_axis, y_axis, x_mean, y_mean);
	var r = combined / Math.sqrt(x_deviation * y_deviation);
	return r;
}