# HK Service Map
HK Service Map is a map to visualise service units data from XML provided by the Hong Kong Social Welfare Department.
#### Screenshot
![Example Screenshot](screenshot.png "Map Screen With Leaflet.js")
![Example Info Screenshot](screenshot-info.png "Displaying Info With OpenLayers")

### Features:
- Implementation in both OpenLayers and Leaflet.js;
- Can be run locally or with a web server;
- No API limit (Address lookup service by HK-OGCIO, map tiles by OSM, layering API by OpenLayers or Leaflet.js);
- Multilingual support (Additional language and field support can be added through editing `scripts/localise.js`)

### Setup
1. Download the source code here.
2. Install `python3` and `pip` from repositories or build from source.
3. Using `pip`, install `grequests` and `xmljson`
4. Connect to the internet and run `getinfo.py` using `python3` (Heavy Internet traffic process)
5. Wait for the script to finish and open either `openlayers.html` or `leaflet.html` depends on the preferred API.
