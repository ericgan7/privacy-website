var paths = {};
red = 255;
blue = 00;

function change(input) {
	console.log("CHANGE");
	var b = document.getElementById("deltaInput");
	b.innerHTML = input.toString() + "<span class='caret'></span>";
	b.value = input
}

function init() {
	$("#tempButton").click(runSim);
	$("#searchButton").click(fetchData);
	initMap();
}

function initMap() {
	map = new google.maps.Map(document.getElementById('viewDiv'), {
		center: { lat: 40.794263, lng: -73.308177 },
		zoom: 10
	});
	console.log("init");
}

function runSim() {
	delta = parseFloat(document.getElementById("deltaInput").value);
	console.log(delta);
	num = parseInt(document.getElementById("querySizeInput").value);
	if (checkValid(num, delta)) {
		retrieveData1(delta, num).done(tourData => {
			var list = document.getElementById("tourList");
			for (key in tourData) {
				if (key == 0) {
					continue;//header
				}
				data = [40.780566, -73.543677, 40.692956, -73.984266];
				populateMap(data);
				populateTable(key, tourData[key]);
				var item = document.createElement('li');
				item.appendChild(document.createElement('link'));
				k = key.toString();
				item.innerHTML = 'Tour ' + k;
				item.id = k;
				item.className = 'tours';
				list.appendChild(item);
			}
		})
	}
}

function fetchData() {
	retrieveData().done(tourData => {
		var list = document.getElementById("tourList");
		for (key in tourData) {
			if (key == 0) {
				continue;
			}
			populateMap(key, tourData[key]);
			populateTable(key, tourData[key]);
			var item = document.createElement('li');
			item.appendChild(document.createElement('link'));
			k = key.toString();
			item.innerHTML = 'Tour ' + k;
			item.id = k;
			item.className = 'tours';
			list.appendChild(item);
		}
	});
}

function populateMap(key, data) {
	var directions = new google.maps.DirectionsService;
	directions.route({
		origin: data[0],
		destination: data[1],
		travelMode: 'DRIVING'
	}, function (response, status) {
		if (status == google.maps.DirectionsStatus.OK) {
			var r = lerp(0, 255, Math.random());
			var b = lerp(0, 255, Math.random());
			var g = lerp(0, 255, Math.random());
			var color = "#" + ("00" + r.toString(16)).slice(-2) +
				("00" + g.toString(16)).slice(-2) +
				("00" + b.toString(16)).slice(-2);
			var lineSymbol = {
				path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW
			};
			console.log(color);
			path = new google.maps.Polyline({
				path: [],
				strokeColor: color,
				strokeOpacity: 1.0,
				strokeWeight: 2,
				icons: [{
					icon: lineSymbol,
					offset : '100%',
				}],
				map: map
			});
			for (var i = 0; i < response['routes'].length; ++i) {
				var leg = response['routes'][i]['legs'];
				for (var j = 0; j < leg.length; ++j) {
					var steps = leg[j]['steps'];
					for (var k = 0; k < steps.length; ++k) {
						points = steps[k]['path'];
						for (var l = 0; l < points.length; ++l) {
							path.getPath().push(new google.maps.LatLng(points[l].lat(), points[l].lng()));
						}
					}
				}
			}
			var ori = response.request.origin.location;
			//var dest = response.request.destination.location;
			var start = new google.maps.Marker({
				position: new google.maps.LatLng(ori.lat(), ori.lng()),
				map: map
			});
			paths[key] = { 'polyline':path, 'start': start};
		}
		$('nav-pills a[href="#mapSelect"]').tab('show');
	});
	
}

function populateTable(tourID, data) {
	console.log(data);
	var body = document.getElementById('resultsBody');
	var row = document.createElement('tr');
	var id = document.createElement('td');
	id.innerHTML = tourID;
	row.appendChild(id);
	var d;
	var values = [0, 1, 2, 3];
	for (index in data) {
		if (data[index] in values) {
			continue;
		}
		else {
			d = document.createElement('td');
			d.innerHTML = data[index];
			row.appendChild(d);
		}
	}
	body.appendChild(row);
}

function checkValid(num, delta) {
	if ((delta == 0.2 || delta == 0.3) && Number.isInteger(num)) {
		console.log("RUN");
		$('#resultsBody tr').remove();
		$('#tourList li').remove();
		return true;
	}
	return false;
}

function retrieveData1(delta, num) {
	d = delta.toString();
	n = num.toString();
	return $.ajax({
		url: "run/tourset/"+ d + n
	})
}

function retrieveData() {
	var d = parseFloat(document.getElementById('delta').value);
	var n = parseInt(document.getElementById('numTours').value);
	var k = parseInt(document.getElementById('maxK').value);
	var sdate = document.getElementById('startDate').value;

	return $.ajax({
		url: "run/OD",
		type: "GET",
		data: 
	})
}

function uploadFile(name){
	console.log('change');
	var file = event.target.files[0];
	var fData = new FormData;
	fData.append(name, file, name+'.csv');
	$.ajax({
		url: "run/OD/" + name,
		type: "POST",
		data: fData,
		contentType: false,
		cache: false,
		fetchData: false,
		processData: false
	})
}

$(document).ready(
	function(){
		init();
	})

function lerp(v1, v2, amt) {
	return Math.floor((1 - amt) * v1 + v2 * amt);
}
