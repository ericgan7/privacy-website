paths = {};
red = 255;
blue = 00;

function change(input) {
	console.log("CHANGE");
	var b = document.getElementById("deltaInput");
	b.innerHTML = input.toString() + "<span class='caret'></span>";
	b.value = input
}

function init() {
	$("#searchButton").click(fetchData);
	initMap();
}

function initMap() {
	map = new google.maps.Map(document.getElementById('viewDiv'), {
		center: { lat: 40.729375, lng: -73.951556 },
		zoom: 11
	});
	console.log("init");
}

function selectTours(all) {
	if (all) {
		for (key in paths) {
			paths[key]['polyline'].setMap(map);
			paths[key]['start'].setMap(map);
		}
		$(".toursCheckboxes").checked = true;
	}
	else {
		for (key in paths){
			paths[key]['polyline'].setMap(null);
			paths[key]['start'].setMap(null);
		}
		$(".toursCheckboxes").checked = false;
	}
}

function fetchData() {
	for (var key in paths) {
		paths[key]['polyline'].setMap(null);
		paths[key]['start'].setMap(null);
	}
	var s = $(".tourListElement");
	var list = document.getElementById("tourList");
	for (var i = 0; i < s.length; ++i) {
		list.removeChild(l[i]);
	}
	paths = {}
	retrieveData().done(tourData => {
		var list = document.getElementById("tourList");
		for (key in tourData) {
			if (key == 0) {
				continue;
			}
			populateMap(key, tourData[key], key%4);
			populateTable(key, tourData[key]);
			k = key.toString();
			var item = document.createElement('li');
			var checkbox = document.createElement('input')
			var label = document.createElement("label")
			label.innerHTML = 'Tour ' + k;
			label.setAttribute('for', k);


			checkbox.type = 'checkbox';
			checkbox.id = k;
			checkbox.checked = true;
			checkbox.value = k;
			checkbox.className = 'tourCheckboxes';
			checkbox.setAttribute("onchange", "toggleTour(this)");

			item.appendChild(checkbox);
			item.appendChild(label);
			item.className = 'tourListElement';
			item.value = k;
			item.setAttribute("onmouseenter", "highlightTour(this.value)");
			item.setAttribute("onmouseleave", "dehighlightTour()");

			list.appendChild(item);
		}
	});
}

function highlightTour(key){
	for (k in paths) {
		if (k == key) {
			paths[k]['polyline'].setOptions({ strokeWeight: 4 });
		}
		else {
			paths[k]['polyline'].setOptions({ strokeOpacity: 0.5 });;
		}
	}
}

function dehighlightTour() {
	for (key in paths) {
		paths[key]['polyline'].setOptions({ strokeWeight: 1 });
		paths[key]['polyline'].setOptions({ strokeOpacity: 1.0 });
	}
}

function toggleTour(element) {
	if (element.checked) {
		paths[element.value]['polyline'].setMap(map);
		paths[element.value]['start'].setMap(map);
	}
	else {
		paths[element.value]['polyline'].setMap(null);
		paths[element.value]['start'].setMap(null);
	}

}

function populateMap(key, data, delay) {
	if (delay > 120) {
		console.log('RESPONSE TOOK TOO LONG');
		return null;
	}
	var directions = new google.maps.DirectionsService;
	directions.route({
		origin: data[0],
		destination: data[1],
		travelMode: 'DRIVING'
	}, function (response, status) {
		console.log(status);
		if (status == google.maps.DirectionsStatus.OK) {
			draw(response, key);
		}
		else {
			if (delay > 5) {
				console.log('repeated');
			}
			setTimeout(function () { populateMap(key, data, delay * 2) }, delay* 500.);
		}
		$('nav-pills a[href="#mapSelect"]').tab('show');
	});
}

function draw(response, key){
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
		strokeWeight: 1,
		icons: [{
			icon: lineSymbol,
			offset: '100%',
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
	paths[key] = { 'polyline': path, 'start': start };
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

function checkValid() {
	var param = new Object();
	param.delta = parseFloat(document.getElementById('delta').value);
	param.num = parseInt(document.getElementById('numTours').value);
	param.maxK = parseInt(document.getElementById('maxK').value);
	param.startDate = document.getElementById('startDate').value;
	param.endDate = document.getElementById('endDate').value;
	if (param.startDate != '' && param.endDate != '') {
		if (new Date(param.startDate).getDate() > new Date(param.endDate).getDate()) {
			return false;
		}
	}
	if (param.maxK <= 1 || param.delta <= 0) {
		return false;
	}
	var sfile = document.getElementById('sFile').files;
	if (sfile.length > 0) {
		sfile = sfile[0].name;
	}
	else {
		sfile = null;
	}
	var lfile = document.getElementById('lFile').files;
	if (lfile.length > 0) {
		lfile = lfile[0].name;
	}
	else {
		lfile = null;
	}
	param.sFile = sfile;
	param.lFile = lfile;
	return param;
}

function retrieveData() {
	var param = checkValid();
	if (param) {
		return $.ajax({
			url: "run/OD",
			type: "POST",
			data: JSON.stringify(param),
			contentType: 'application/json'
		});
	}
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
