paths = {};
red = 255;
blue = 00;

//init document
$(document).ready(
	function () {
		init();
	})

//not used
function change(input) {
	console.log("CHANGE");
	var b = document.getElementById("deltaInput");
	b.innerHTML = input.toString() + "<span class='caret'></span>";
	b.value = input
}

//init map, add listeners
function init() {
	$("#searchButton").click(fetchData);
	$("#selectToggle").change(function () {
		selectTours(this.checked);
	});
	initMap();
}

//google maps centered on manhattan/brooklyn
function initMap() {
	map = new google.maps.Map(document.getElementById('viewDiv'), {
		center: { lat: 40.729375, lng: -73.951556 },
		zoom: 13
	});
	console.log("init");
}

//select all/none button function
function selectTours(all) {
	if (all) {
		var elements = $(".tourCheckboxes");
		for (var i = 0; i < elements.length; ++i) {
			if (!elements[i].checked) {
				elements[i].checked = true;
				toggleTour(elements[i]);
			}
		}
	}
	else {
		var elements = $(".tourCheckboxes");
		for (var i = 0; i < elements.length; ++i) {
			if (elements[i].checked) {
				elements[i].checked = false;
				toggleTour(elements[i]);
			}
		}
	}
}

//sends paramaeters to get tours
function fetchData() {
	//clear out all previous data
	for (var key in paths) {
		paths[key]['polyline'].setMap(null);
		paths[key]['start'].setMap(null);
	}
	var s = $(".tourListElement");
	var list = document.getElementById("tourList");
	for (var i = 0; i < s.length; ++i) {
		list.removeChild(s[i]);
	}
	paths = {}
	var param = checkValid();
	if (!param) {
		console.log("INVALID PARAMETERS")
		return None
	}
	var body = document.getElementById("resultsBody");
	while (body.children.length > 0){
		body.removeChild(body.children[0]);	
	}
	//switch to map after selecting to show data
	$('a[href="#mapSelect"').tab('show');
	retrieveData(param).done(tourData => {
		var list = document.getElementById("tourList");
		var idData = tourData[0];
		var locationData = tourData[1];
		for (key in locationData) {
			//put data on map
			populateMap(key, locationData[key], key % 4);
			//put data in table
			populateTable(key, idData[key], locationData[key]);
			//tour list check boxes
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
			//functions for toggling and highlightings
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
//highlight when mousing over
	//adds end marker, raises stroke weight of selected, decreases stroke opacity for all others
function highlightTour(key){
	for (k in paths) {
		if (k == key) {
			paths[k]['polyline'].setOptions({ strokeWeight: 4 });
			if (document.getElementById(key.toString()).checked){
				paths[k]['end'].setMap(map);
			}
		}
		else {
			paths[k]['polyline'].setOptions({ strokeOpacity: 0.5 });;
		}
	}
}
//unhighlight tours when mouse leaving
	//removes end marker, resets stroke weight ans opacity
function dehighlightTour() {
	for (key in paths) {
		paths[key]['polyline'].setOptions({ strokeWeight: 1 });
		paths[key]['end'].setMap(null);
		paths[key]['polyline'].setOptions({ strokeOpacity: 1.0 });
	}
}

//toggle tour on/off
	//removes poly lines, end markers, and table row
function toggleTour(element) {
	if (element.checked) {
		paths[element.value]['polyline'].setMap(map);
		paths[element.value]['start'].setMap(map);
		document.getElementById('t' + element.value.toString()).style = 'display: true';
	}
	else {
		paths[element.value]['polyline'].setMap(null);
		paths[element.value]['start'].setMap(null);
		document.getElementById('t' + element.value.toString()).style = 'display: none';
	}
}

//add poly line to map
	//route is calculated with google directions api
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
			//sends path to be converted to polyline and displayed
			draw(response, key);
		}
		else {
			//exponential delay to overcome query quota
			setTimeout(function () { populateMap(key, data, delay * 2) }, delay * 500.);
		}
		$('nav-pills a[href="#mapSelect"]').tab('show');
	});
}

//draws polyline on map
function draw(response, key) {
	//random color
	var r = lerp(0, 255, Math.random());
	var b = lerp(0, 255, Math.random());
	var g = lerp(0, 255, Math.random());
	var color = "#" + ("00" + r.toString(16)).slice(-2) +
		("00" + g.toString(16)).slice(-2) +
		("00" + b.toString(16)).slice(-2);
	var lineSymbol = {
		path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
		fillColor: 'black',
		scale: 2,
		strokeWeight: 2,
		strokeColor: 'black'
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
	//gets route from directions api
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
	var dest = response.request.destination.location;
	var start = new google.maps.Marker({
		position: new google.maps.LatLng(ori.lat(), ori.lng()),
		map: map
	});
	var end = new google.maps.Marker({
		position: new google.maps.LatLng(dest.lat(), dest.lng()),
	});
	paths[key] = { 'polyline': path, 'start': start , 'end': end};
}

//populate table
function populateTable(tourID, idData, locationData) {
	console.log(idData);
	var body = document.getElementById('resultsBody');
	var row = document.createElement('tr');
	row.id = 't' + tourID.toString();
	var id = document.createElement('td');
	id.innerHTML = tourID;
	row.appendChild(id);
	var d;
	var l;
	for (index in idData) {
		d = document.createElement('td');
		d.innerHTML = idData[index].toString();
		row.appendChild(d);
		l = document.createElement('td');
		l.innerHTML = locationData[index].toString();
		row.appendChild(l);
	}
	body.appendChild(row);
}

//check parameters are valid
function checkValid() {
	var param = new Object();
	param.delta = parseFloat(document.getElementById('delta').value);
	param.num = parseInt(document.getElementById('numTours').value);
	param.maxK = parseInt(document.getElementById('maxK').value);
	param.startTime = document.getElementById('startTime').value;
	param.endTime = document.getElementById('endTime').value;
	param.startDate = document.getElementById('startDate').value;
	param.endDate = document.getElementById('endDate').value;
	//date is valid
	if (param.startDate != '' && param.endDate != '') {
		if (new Date(param.startDate).getDate() > new Date(param.endDate).getDate()) {
			return false;
		}
	}
	//time is valid
	if (param.startTime != '' && param.endTime != '') {
		if (param.startTime > param.endTime) {
			return false;
		}
	}
	//max k  and delta is present
	else if (param.maxK == '' || param.delta == '') {
		return false;
	}
	//maxk, delta, and num is valid number
	else if (param.maxK <= 1 || param.delta <= 0 || param.num <= 0) {
		return false;
	}
	//check available files
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
	var zfile = document.getElementById('lFile').files;
	if (zfile.length > 0) {
		zfile = lfile[0].name;
	}
	else {
		zfile = null;
	}
	param.sFile = sfile;
	param.lFile = lfile;
	param.zFile = zFile;
	return param;
}

//retrieve tour data
function retrieveData(param) {
	return $.ajax({
		url: "run/OD",
		type: "POST",
		data: JSON.stringify(param),
		contentType: 'application/json'
	});
}

//upload other datasets if inputed
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

//LERP gets the fraction between two numbers
function lerp(v1, v2, amt) {
	return Math.floor((1 - amt) * v1 + v2 * amt);
}
