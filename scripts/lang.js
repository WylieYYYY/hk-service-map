/* exported langChange, langMouseOver */
/* global lang:writable, locale */
'use strict';

/**
 * Changes button appearance between globe icon and language abbreviation.
 * @param {boolean} mouseIn - Whether mouse is entering the button.
 */
function langMouseOver(mouseIn) {
  document.getElementById('lang_icon').style.display = mouseIn ?
      'none' : 'inline';
  document.getElementById('lang_name').innerText = mouseIn ? locale[lang] : '';
}

var langKeyList = Object.keys(locale);
var langRota = langKeyList.indexOf(lang);

/**
 * Rotates the language and change button's language abbreviation.
 * @param {function} callback - Called to change other elements' language.
 */
function langChange(callback) {
  langRota = (langRota + 1) % langKeyList.length;
  lang = langKeyList[langRota];
  document.getElementById('lang_name').innerText = locale[lang];
  document.getElementById('lang_icon').style.display = 'none';
  callback == undefined || callback();
}
