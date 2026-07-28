import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).parent / "trenmaya_osm.json"

ENDPOINTS = [
    "https://overpass.kumi Systems.com/api/interpreter",  # placeholder, replaced below
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/interpreter",
]

def overpass(query: str) -> dict:
    last_err = None
    for url in ENDPOINTS:
        if "placeholder" in url:
            continue
        data = urllib.parse.urlencode({"data": query}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"User-Agent": "opencode-trip-planning/1.0 (research)"},
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            last_err = e
            print(f"  endpoint {url} failed: {e}")
            continue
    raise last_err

# 1. Exact railway track geometry (relation 13196595 = "Tren Maya" vias)
# Output only the ways with embedded geometry (much lighter than recursing all nodes).
track_query = """
[out:json][timeout:300];
relation(13196595);
way(r);
out geom;
"""

# 2. Station stops: nodes tagged as station/halt/tram_stop in the peninsula+chiapas/tabasco bbox
bbox = "16.0,-93.0,22.0,-85.5"
station_query = f"""
[out:json][timeout:300];
(
  node["railway"~"^(station|halt|tram_stop)$"]["name"]({bbox});
  node["public_transport"="station"]["name"]({bbox});
  node["railway"="stop"]["name"]({bbox});
);
out body geom;
"""

print("Fetching Tren Maya track geometry from OpenStreetMap...")
tracks = overpass(track_query)
print("Fetching station nodes in region...")
stations = overpass(station_query)

result = {
    "tracks": tracks,
    "stations": stations,
}
OUT.write_text(json.dumps(result), encoding="utf-8")

# Quick summary
el = tracks.get("elements", [])
ways = [e for e in el if e.get("type") == "way"]
print(f"Track ways: {len(ways)}")

# Compute bounding box of track geometry
lats, lons = [], []
for e in el:
    g = e.get("geometry")
    if g:
        for p in g:
            lats.append(p["lat"]); lons.append(p["lon"])
if lats:
    print(f"Track bbox: lat {min(lats):.4f}-{max(lats):.4f}, lon {min(lons):.4f}-{max(lons):.4f}")

sel = stations.get("elements", [])
print(f"Station-node candidates: {len(sel)}")
# Print names that look like Tren Maya stops
want = [
    "palenque","boca del cerro","tenosique","el triunfo","candelaria","escarcega",
    "carrillo puerto","champon","champoton","edzna","edzna","campeche","tenabo",
    "hecelchakan","hecalkan","calkini","maxcanu","uman","tixkokob","merida","teya",
    "izamal","chichen","valladolid","nuevo xcan","leona vicario","cancun","puerto morelos",
    "playa del carmen","tulum","felipe carrillo","bacalar","chetumal","xpujil","conhuas",
    "centenario","nicolas bravo","limones"
]
print("\n--- Candidate station nodes (name match) ---")
for e in sel:
    tags = e.get("tags", {})
    name = tags.get("name", "")
    if not name:
        continue
    nl = name.lower()
    if any(w in nl for w in want):
        print(f"{e['id']:>12}  {e['lat']:.5f},{e['lon']:.5f}  {tags.get('railway','')}/{tags.get('public_transport','')}  {name}")
print(f"\nSaved raw data to: {OUT}")