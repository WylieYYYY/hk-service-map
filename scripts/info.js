/* exported infoSwitch, searchUnit, toggleDynamicSearch */
/* global addMarker, fuzzysort, info, lang, locale, localise, longlat, map,
    markerGroup, markerIcon, markerScale, L, selected:writable, unitinfo,
    vectorLayer */
'use strict';

// Add and prevent displaying index
unitinfo[0].unshift(Object.keys(locale).join());
for (var i = 1; i < unitinfo.length; i++) unitinfo[i].unshift(i - 1);
var keyparts = ['name', 'district', 'address', 'telephoneNumber',
  'addTelephoneNumber', 'faxNumber', 'type', 'religious', 'mealProvision',
  'typeResentialCareHomes', 'addressOverride',
];
// match valid keys and get their indexes
var keyRegex = new RegExp('^(' + keyparts.join('|') + ').*$');
var keyIndexes = [];
unitinfo[0].forEach(function(key, index) {
  if (keyRegex.test(key)) keyIndexes.push(index.toString());
});
var searchedGroup = null;

/**
 * Click search button on pressing return.
 * @param {object} e - Keyup event.
 */
function clickSearch(e) {
  if (e.keyCode == 13) {
    e.preventDefault();
    document.getElementById('search_button').click();
  }
}

/**
 * Toggle whether search should be done during typing.
 */
function toggleDynamicSearch() {
  var searchBox = document.getElementById('search_box');
  var searchButton = document.getElementById('search_button');
  if (document.getElementById('dynamic_search').checked) {
    searchButton.style.display = 'none';
    searchUnit(searchBox.value);
    searchBox.onchange = function() {
      searchUnit(searchBox.value);
    };
    searchBox.onpaste = function() {
      searchUnit(searchBox.value);
    };
    searchBox.onkeyup = function() {
      searchUnit(searchBox.value);
    };
  } else {
    searchButton.style.display = 'flex';
    searchBox.onchange = undefined;
    searchBox.onpaste = undefined;
    searchBox.onkeyup = clickSearch;
  }
}

var isLeaflet = window.ol == undefined;
/**
 * Search and display units with a search term.
 * @param {string} term - Search term to be used.
 */
function searchUnit(term) {
  if (selected != 0) {
    if (isLeaflet) {
      (searchedGroup == null ? markerGroup : searchedGroup)
          .getLayers().find(function(marker) {
            return marker.properties.unitIndex == selected;
          }).setIcon(markerIcon);
    }
    selected = 0;
    info.className = 'status bar';
    info.innerText = '';
    info.style.opacity = 0;
    info.style.width = 'auto';
  }
  if (isLeaflet) {
    if (searchedGroup == null) map.removeLayer(markerGroup);
    else map.removeLayer(searchedGroup);
  }
  searchedGroup = null;
  if (term == '') {
    if (isLeaflet) markerGroup.addTo(map);
    return;
  }
  var filteredIndexes = fuzzysort.go(term, unitinfo.slice(1), {
    keys: keyIndexes,
    threshold: -10000,
  }).map(function(x) {
    return x.obj[0];
  });
  searchedGroup = isLeaflet ? L.layerGroup() : filteredIndexes;
  if (isLeaflet) {
    for (var i = 0; i < filteredIndexes.length; i++) {
      if (longlat[i][1] == -91) break;
      addMarker(filteredIndexes[i], searchedGroup);
    }
    searchedGroup.addTo(map);
  } else vectorLayer.getSource().changed();
}

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
