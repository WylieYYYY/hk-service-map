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
		info.innerHTML += "<br/><b>" + localise[unitinfo[0][index]] + "</b>" + property;
	});
	info.style.width = window.innerWidth / 2 * ui_scale + "px";
}

function info_switch(unit_index) {
	if (selected == 0) {
		selected = unit_index;
		info_update(unit_index, document.getElementById("info"), marker_scale);
		info.className += " spaced-dock";
	} else {
		selected = 0;
		info.className = "status bar";
		info.innerText = unitinfo[unit_index][unitinfo[0].indexOf("name" + lang)];
		info.style.width = "auto";
	}
}