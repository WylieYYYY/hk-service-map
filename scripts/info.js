/* exported infoSwitch */
/* global info, lang, locale, localise, markerScale, selected:writable,
       unitinfo */
'use strict';

/**
 * Shows or updates info box according to language and specified unit.
 * @param {number} unitIndex - Unit's index in unitinfo.
 * @param {object} info - The info boxs' elements to be modified.
 * @param {number} UIScale - Multiplier determining the scale of the box.
 */
function infoUpdate(unitIndex, info, UIScale) {
  info.style.opacity = 1;
  info.className = 'info bar';
  info.innerHTML = '<b>--' + localise['info' + lang] + '--</b>';
  unitinfo[unitIndex].forEach(function(property, index) {
    var skip = false;
    Object.keys(locale).forEach(function(langOpt) {
      if (langOpt == lang) return;
      if (unitinfo[0][index].indexOf(langOpt) != -1) skip = true;
    });
    if (property == null || skip) return;
    var localisedKey = unitinfo[0][index];
    if (localisedKey.indexOf(lang) == -1) localisedKey += lang;
    var localisedName = localise[localisedKey];
    if (localisedName == '') return;
    if (localisedName == undefined) {
      localisedName = unitinfo[0][index].replace(
          new RegExp('(' + Object.keys(locale).join('|') + ')', 'g'), '');
      localisedName = localisedName.replace(/([A-Z])/g, ' $1');
      localisedName = localisedName.replace(/^./,
          localisedName.charAt(0).toUpperCase()) + ': ';
    }
    info.innerHTML += '<br/><b>' + localisedName + '</b>' + property;
  });
  info.style.width = window.innerWidth / 2 * UIScale + 'px';
}

/**
 * Displays the small unit name status bar if the device is not a touchscreen.
 * @param {number} unitIndex - Unit's index in unitinfo.
 */
function displayStatus(unitIndex) {
  if ('ontouchstart' in document.documentElement) {
    info.style.opacity = 0;
  } else {
    info.className = 'status bar';
    info.innerText = unitinfo[unitIndex][unitinfo[0].indexOf('name' + lang)];
    info.style.width = 'auto';
  }
}

/**
 * Displays info box if a marker is selected, displays status bar otherwise.
 * @param {number} unitIndex - Unit's index in unitinfo.
 */
function infoSwitch(unitIndex) {
  if (selected == 0) {
    selected = unitIndex;
    infoUpdate(unitIndex, document.getElementById('info'), markerScale);
    info.className += ' spaced-dock';
  } else {
    selected = 0;
    displayStatus(unitIndex);
  }
}
