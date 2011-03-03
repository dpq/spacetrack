var tracks = {}, customTracks = {};

var trackTimestamps = {};
var trackPrecision = 25;

function calcTrack(id) {
	var line = [];
	var dt = new Date();
	trackTimestamps[id] = dt.getTime();
	for (var secs = -7200; secs < 7200; secs += trackPrecision) {
		var satInfo = PLib.CustomFind(id, dt.getTime() + secs*1000);
		line.push(new google.maps.LatLng(satInfo.latitude, satInfo.longitude));
	}
	return line;
}

function recalcTrack(id) {
	var dt = new Date();
	if (dt.getTime() > trackTimestamps[id] + trackPrecision*1000) {
		var satInfo = PLib.CustomFind(id, dt.getTime() + 7200*1000);
		tracks[id].getPath().push(new google.maps.LatLng(satInfo.latitude, satInfo.longitude));
		tracks[id].getPath().removeAt(0);
		trackTimestamps[id] = dt.getTime();
	}
}

function createTrack(id, flash) {
	if (flash) {
		tracks[id] = new google.maps.Polyline({path: calcTrack(id), geodesic: true,  strokeColor: "#e03030", strokeWeight: 1, strokeOpacity: 1.0, map: map});
		setTimeout("dimTrack('"+ id + "')", 3000);
	}
	else {
		tracks[id] = new google.maps.Polyline({path: calcTrack(id), geodesic: true, strokeColor: "#00dd40", strokeWeight: 1, strokeOpacity: 0.4, map: map});
	}
}

function destroyTrack(id) {
	tracks[id].setMap();
	delete tracks[id];
}

function highlightTrack(id) {
	if (!tracks[id]) {
		return;
	}
	if (customTracks[id]) {
		tracks[id].setOptions({ strokeColor: customTracks[id], strokeOpacity: 1.0 });
	}
	else {
		tracks[id].setOptions({ strokeColor: "#e03030", strokeOpacity: 1.0 });
	}
}

function dimTrack(id) {
	if (!tracks[id]) {
		return;
	}
	if (customTracks[id]) {
		tracks[id].setOptions({ strokeColor: customTracks[id], strokeOpacity: 0.4 });
	}
	else {
		tracks[id].setOptions({ strokeColor: "#00dd40", strokeOpacity: 0.4 });
	}
}

function setTrackPrecision() {
	if (!isNumeric($("input#set_trackprecision")[0].value)) {
		$("input#set_trackprecision")[0].value = "25";
	};
	trackPrecision = parseInt($("input#set_trackprecision")[0].value);
	if (typeof map.addOverlay != "function") {
		return;
	}
	for (var id in tracks) {
		recalcTrack(id);
	}
}

function toggleTracks() {
	if ($("input#set_showtracks")[0].checked) {
		for (var id in markers) {
			createTrack(id, true);
		}
	}
	else {
		for (var id in tracks) {
			destroyTrack(id);
		}
	}
}
