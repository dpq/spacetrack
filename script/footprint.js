var footprints = {}, customFootprints = {};

var footprintPrecision = 60;

function calcFootprint(id, points) {
	var satInfo = PLib.QuickFind(id);
	var lat = satInfo.latitude, lon = satInfo.longitude, alt = satInfo.altitude;
	var sat = new google.maps.LatLng(lat, lon);
	if (points < 3) {
		return [ sat ];
	}
	var perimeter = new Array();
	var dg = 2.0*3.1415/points;
	var re = 6375.0;
	var visibilityCos = re/(re + alt);
	var visibilitySin = Math.sqrt(1 - visibilityCos*visibilityCos);
	for (var i = 0; i < points; i++) {
		perimeter.push(cart2sph(rotate([visibilitySin*Math.cos(i*dg), visibilitySin*Math.sin(i*dg), visibilityCos], satInfo)));
	}
	if (distHaversine(sat, new google.maps.LatLng(90, 0)) < distHaversine(sat, perimeter[0])) {
		perimeter.push(new google.maps.LatLng(perimeter[0].lat(), perimeter[0].lng()));
		for (var i = points - 1; i >= 0; i--) {
			perimeter.push(new google.maps.LatLng(85, perimeter[i].lng()));
		}
		perimeter.push(new google.maps.LatLng(85, perimeter[points - 1].lng()));
		perimeter.push(new google.maps.LatLng(perimeter[0].lat(), perimeter[0].lng()));
	}
	if (distHaversine(sat, new google.maps.LatLng(-90, 0)) < distHaversine(sat, perimeter[0])) {
		perimeter.push(new google.maps.LatLng(perimeter[0].lat(), perimeter[0].lng()));
		for (var i = points - 1; i >= 0; i--) {
			perimeter.push(new google.maps.LatLng(-85, perimeter[i].lng()));
		}
		perimeter.push(new google.maps.LatLng(-85, perimeter[points - 1].lng()));
		perimeter.push(new google.maps.LatLng(perimeter[0].lat(), perimeter[0].lng()));
	}
	else {
		perimeter.push(new google.maps.LatLng(perimeter[0].lat(), perimeter[0].lng()));
	}
	return perimeter;
}

function recalcFootprint(id) {
	footprints[id].setPaths(calcFootprint(id, footprintPrecision));
}

function createFootprint(id, flash) {
	if (flash) {
		footprints[id] = new google.maps.Polygon({map: map, paths: calcFootprint(id, footprintPrecision), strokeColor: "#EA0000", strokeWeight: 1, strokeOpacity: 0.8, fillColor: "#E14000", fillOpacity: 0.6, clickable: false });
		setTimeout("dimFootprint('"+ id + "')", 3000);
	}
	else {
		footprints[id] = new google.maps.Polygon({map: map, paths: calcFootprint(id, footprintPrecision), strokeColor: "#00EA00", strokeWeight: 1, strokeOpacity: 0.4, fillColor: "#E1E100", fillOpacity: 0.2, clickable: false });
	}
}

function destroyFootprint(id) {
	footprints[id].setMap();
	delete footprints[id];
}

function highlightFootprint(id) {
	if (!footprints[id]) {
		return;
	}
	if (customFootprints[id]) {
		footprints[id].setOptions({ strokeColor: customFootprints[id][0], strokeOpacity: 0.8 });
		footprints[id].setOptions({ fillColor: customFootprints[id][1], fillOpacity: 0.6 });
	}
	else {
		footprints[id].setOptions({ strokeColor: "#EA0000", strokeOpacity: 0.8 });
		footprints[id].setOptions({ fillColor: "#E14000", fillOpacity: 0.6 });
	}
}

function dimFootprint(id) {
	if (!footprints[id]) {
		return;
	}
	if (customFootprints[id]) {
		footprints[id].setOptions({ strokeColor: customFootprints[id][0], strokeOpacity: 0.4 });
		footprints[id].setOptions({ fillColor: customFootprints[id][1], fillOpacity: 0.2 });
	}
	else {
		footprints[id].setOptions({ strokeColor: "#00EA00", strokeOpacity: 0.4 });
		footprints[id].setOptions({ fillColor: "#E1E100", fillOpacity: 0.2 });
	}
}

function setFootprintPrecision() {
	if (!isNumeric($("input#set_footprintprecision")[0].value)) {
		$("input#set_footprintprecision")[0].value = "20";
	};
	footprintPrecision = parseInt($("input#set_footprintprecision")[0].value);
	for (var id in footprints) {
		recalcFootprint(id);
	}
}

function toggleFootprints() {
	if ($("input#set_showfootprints")[0].checked) {
		for (var id in markers) {
			createFootprint(id, true);
		}
	}
	else {
		for (var id in footprints) {
			destroyFootprint(id);
		}
	}
}
