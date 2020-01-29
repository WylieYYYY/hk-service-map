"use strict";
function info_update(unit_index, info, ui_scale) {
	info.style.opacity = 1;
	info.className = "info bar";
	info.innerHTML = "<b>--" + localise["info" + lang] + "--</b>";
	unitinfo[unit_index].forEach(function(property, index) {
		var skip = false;
		Object.keys(locale).forEach(function(lang_opt) {
			if (lang_opt == lang) return;
			if (unitinfo[0][index].indexOf(lang_opt) != -1) skip = true;
		});
		if (property == null || skip) return;
		var localised_key = unitinfo[0][index];
		if (localised_key.indexOf(lang) == -1) localised_key += lang;
		var localised_name = localise[localised_key];
		if (localised_name == undefined) {
			localised_name = unitinfo[0][index].replace(new RegExp("(" + Object.keys(locale).join("|") + ")", "g"), "");
			localised_name = localised_name.replace(/([A-Z])/g, " $1")
			localised_name = localised_name.replace(/^./, localised_name.charAt(0).toUpperCase()) + ": ";
		}
		info.innerHTML += "<br/><b>" + localised_name + "</b>" + property;
	});
	info.style.width = window.innerWidth / 2 * ui_scale + "px";
}

function display_status(unit_index) {
	if ("ontouchstart" in document.documentElement) {
		info.style.opacity = 0;
	} else {
		info.className = "status bar";
		info.innerText = unitinfo[unit_index][unitinfo[0].indexOf("name" + lang)];
		info.style.width = "auto";
	}
}

function info_switch(unit_index) {
	if (selected == 0) {
		selected = unit_index;
		info_update(unit_index, document.getElementById("info"), marker_scale);
		info.className += " spaced-dock";
	} else {
		selected = 0;
		display_status(unit_index);
	}
}