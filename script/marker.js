var markers = {};

function calcMarker(id) {
	var satInfo = PLib.QuickFind(id);
	return new google.maps.LatLng(satInfo.latitude, satInfo.longitude);
}

function createMarker(id, flash) {
	var position = calcMarker(id);
	var title = $("label[for='" + id + "']")[0].innerHTML;

	if ($("input#set_shownames")[0].checked) {
		var icon = new google.maps.MarkerImage("");
		icon.image = "";
		icon.iconAnchor = new google.maps.Point(0, 0);
		if (flash) {
			url = "server.py/label?mode=flash&id=" + id;
		}
		else {
			url = "server.py/label?mode=normal&id=" + id;
		}
		markers[id] = new google.maps.Marker({ position: position, title: title, map: map}); //, "icon": icon });
		if (flash) {
			setTimeout("dimMarker('"+ id + "')", 3000);
		}
 		createInfobox(id);
 		google.maps.event.addListener(markers[id], "click", function() {
 			selectedSatellite = id;
 			infobox.close();
 			infobox.setContent(popups[id]);
 			infobox.open(map, markers[id]);
 		});
 		google.maps.event.addListener(markers[id], "mouseover", function() {
 			highlightTrack(id);
 			highlightFootprint(id);
 		});
 		google.maps.event.addListener(markers[id], "mouseout", function() {
 			dimTrack(id);
 			dimFootprint(id);
 		});
 	}
	else {
		$.get("/icon/" + id, function(url) {
			if (url == "") {
				markers[id] = new google.maps.Marker({position: position, title: title });
			}
			else {
				var icon = new google.maps.MarkerImage(url);
				markers[id] = new google.maps.Marker({position: position, title: title, icon: icon });
			}
			createInfobox(id);
			google.maps.event.addListener(markers[id], "click", function() {
				selectedSatellite = id;
        var infobox = new google.maps.InfoWindow({content: popups[id], position: markers[id].getPosition()});
        infobox.close();
   			infobox.setContent(popups[id]);
   			infobox.open(map, markers[id]);
			});
			google.maps.event.addListener(markers[id], "mouseover", function() {
				highlightTrack(id);
				highlightFootprint(id);
			});
			google.maps.event.addListener(markers[id], "mouseout", function() {
				dimTrack(id);
				dimFootprint(id);
			});
		});
	}
}

function destroyMarker(id) {
	markers[id].setMap();
	delete markers[id];
}

function highlightMarker(id) {
	if ($("input#set_shownames")[0].checked) {
	//	markers[id].setImage("server.py/label?mode=flash&id=" + id);
	}
}

function dimMarker(id) {
	if ($("input#set_shownames")[0].checked) {
	//	markers[id].setImage("server.py/label?mode=normal&id=" + id);
	}
}

function toggleMarkerMode() {
	for (var id in markers) {
		var coord = markers[id].getPosition();
		var title = markers[id].getTitle();
		destroyMarker(id);
		createMarker(id, false);
	}
}
