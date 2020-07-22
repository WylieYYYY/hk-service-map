"use strict";
function lang_mouse_over(mousein) {
	document.getElementById("lang_icon").style.display = mousein ? "none" : "inline";
	document.getElementById("lang_name").innerText = mousein ? locale[lang] : "";
}
var lang_key_list = Object.keys(locale);
var lang_rota = lang_key_list.indexOf(lang);
function lang_change(callback) {
	lang_rota = (lang_rota + 1) % lang_key_list.length;
	lang = lang_key_list[lang_rota];
	document.getElementById("lang_name").innerText = locale[lang];
	callback == undefined || callback();
}