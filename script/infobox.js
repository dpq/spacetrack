var popups = {};

var infobox = {};

function createInfobox(id) {
	popups[id] = document.createElement("div");
	popups[id].style.marginTop = "8px";

	var header = document.createElement("h4");
	header.style.margin = "0px";
	header.innerHTML = $("label[for='" + id + "']")[0].innerHTML;

	var norad = document.createElement("span");
	norad.innerHTML = "Catalog #: " + id + "<br/>";

	var int_id = "";
	var wwas = document.createElement("span");
	var age = document.createElement("span");
	var launch = document.createElement("span");

	launch.innerHTML = "Launch date: <br/>";
	age.innerHTML = "TLE age: <br/>";

	for (var z = 0; z < PLib.sat.length; z++) {
		if (PLib.sat[z].catnum == id) {
			int_id = mkYear(PLib.sat[z].line1.substring(9, 11)) + "-" + PLib.sat[z].line1.substring(11, 17);
			wwas.innerHTML = "International ID: " + int_id +  "<br/>";
			break;
		}
	}

	var details = document.createElement("a");
	details.href = "http://nssdc.gsfc.nasa.gov/nmc/spacecraftDisplay.do?id=" + int_id;
	details.innerHTML = "Details";
	details.target = "_blank";

	var nodetails = document.createElement("span");
	nodetails.innerHTML = "No details available";
	nodetails.style.display = "none";

	var follow = document.createElement("input");
	follow.type = "button";
	follow.value = "Follow";
	follow.style.marginLeft = "15px";
	follow.onclick = function() {
		followSatellite = selectedSatellite;
		followZoomInitialized = false;
	}
 
	$.get("/age/" + id, function(info) {
		age.innerHTML = "TLE age: " + info + "<br/>";
	});

// 	$.get("/details/" + int_id, function(info) {
// 		var str_begin = "<strong>Launch Date:</strong>&nbsp;";
// 		var str_end = "<br />";
// 		var i_begin = info.indexOf(str_begin) + str_begin.length;
// 		var i_end = info.indexOf("<br />", i_begin);
// 		if (i_begin != -1 && i_end != -1) {
// 			launch.innerHTML = "Launch date: " + info.substring(i_begin, i_end) + "<br/>";
// 		}
// 		else {
// 			launch.innerHTML = "Launch date: N/A <br/>";
// 			details.style.display = "none";
// 			nodetails.style.display = "inline";
// 		}
// 		var str_funding = "<h2>Funding Agenc";
// 		var i_funding = info.indexOf(str_funding);
// 		str_begin = "(";
// 		str_end = ")";
// 		i_begin = info.indexOf(str_begin, i_funding) + 1;
// 		i_end = info.indexOf(str_end, i_funding);
// 		if (i_funding != -1 && i_begin != -1 && i_end != -1) {
// 			$.get("server.py/flag?nation=" + info.substring(i_begin, i_end), function(info) {
// 				popups[id].style.backgroundImage = "url('" + info + "')";
// 				popups[id].style.backgroundPosition = "top right";
// 				popups[id].style.backgroundRepeat = "no-repeat";
// 			});
// 		}
// 	});

	popups[id].appendChild(document.createElement("br"));
	popups[id].appendChild(header);
	popups[id].appendChild(document.createElement("br"));
	popups[id].appendChild(norad);
	popups[id].appendChild(wwas);
	//popups[id].appendChild(launch);
	popups[id].appendChild(age);
	popups[id].appendChild(document.createElement("br"));
	popups[id].appendChild(details);
	popups[id].appendChild(nodetails);
	popups[id].appendChild(follow);
	popups[id].appendChild(document.createElement("br"));
	return popups[id];
}

function destroyInfobox(id) {
	delete popups[id];
}
