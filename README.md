# Tren Maya 12-Day Trip

A 12-day archaeological route through Mexico's Yucatan Peninsula on the Tren Maya railway, covering Palenque, Calakmul, Tulum, Chichen Itza, Edzna, and more.

- **[itinerary.md](itinerary.md)** -- full day-by-day itinerary with budgets, tips, and practical info
- **[route-map.html](route-map.html)** -- interactive Leaflet map of the route and archaeological sites

Open the map in a browser to see all stops, archaeological sites, and train stations along the loop.

## Map generation

The map was built with Python using real OSM track geometry.

- `build_map.py` -- generates `route-map.html` from the OSM data
- `fetch_trenmaya.py` -- queries Overpass API for Tren Maya track geometry and station nodes
- `trenmaya_osm.json` -- cached OSM response (track ways + station nodes)
