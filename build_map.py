import json
from pathlib import Path

import folium
from folium import Element, Icon, Marker, PolyLine, Popup

PROJECT_ROOT = Path(__file__).resolve().parent
OSM_DATA_PATH = PROJECT_ROOT / "trenmaya_osm.json"
OUTPUT_PATH = PROJECT_ROOT / "route-map.html"


def load_osm_track() -> list:
    osm_data = json.loads(OSM_DATA_PATH.read_text(encoding="utf-8"))
    return [e for e in osm_data["tracks"]["elements"] if e.get("type") == "way" and e.get("geometry")]


def snap_to_track(lat: float, lon: float, track_points: list) -> tuple:
    best_d = float("inf")
    best_pt = (lat, lon)
    for pt in track_points:
        d = (pt[0] - lat)**2 + (pt[1] - lon)**2
        if d < best_d:
            best_d = d
            best_pt = pt
    return best_pt


def main() -> None:
    track_ways = load_osm_track()

    all_track_points = []
    for w in track_ways:
        for p in w["geometry"]:
            all_track_points.append((p["lat"], p["lon"]))

    def estimate(lat, lon):
        return snap_to_track(lat, lon, all_track_points)

    # Full station list (counter-clockwise from Cancun)
    # (name, lat, lon, day, overnight, key_site, wikipedia_url)
    stations = [
        # Sections 4+5 -- Cancun and Caribbean coast
        ("Cancun Aeropuerto",     21.02808,  -86.87281,  1,   True,  False, "https://en.wikipedia.org/wiki/Canc%C3%BAn_Airport_railway_station"),
        ("Puerto Morelos",        20.85278,  -86.94944,  None,False, False, "https://en.wikipedia.org/wiki/Puerto_Morelos"),
        ("Playa del Carmen",      20.67882,  -87.11759,  None,False, False, "https://en.wikipedia.org/wiki/Playa_del_Carmen"),
        ("Tulum",                 20.24681,  -87.45392,  2,   True,  True,  "https://en.wikipedia.org/wiki/Tulum_%28archaeological_site%29"),
        ("Tulum Aeropuerto",      20.1516,   -87.6399,   None,False, False, "https://en.wikipedia.org/wiki/Tulum_Airport_railway_station"),

        # Section 6 -- down through QR to Chetumal
        ("Felipe Carrillo Pto.",  19.57861,  -88.04528,  None,False, False, "https://en.wikipedia.org/wiki/Felipe_Carrillo_Puerto,_Quintana_Roo"),
        ("Limones",               19.02432,  -88.10948,  None,False, False, ""),
        ("Bacalar",               18.6810,   -88.393,    3,   True,  False, "https://en.wikipedia.org/wiki/Bacalar"),
        ("Chetumal Aeropuerto",   18.50843,  -88.32324,  None,False, False, "https://en.wikipedia.org/wiki/Chetumal_International_Airport"),

        # Section 7 -- west through southern Campeche
        ("Nicolas Bravo (Kohunlich)",  18.450,  -88.720,  None,False, False, ""),
        ("Xpujil",                18.52670,  -89.39620,  4,   True,  True,  "https://en.wikipedia.org/wiki/Xpujil"),
        ("Conhuas",               18.500,   -89.860,    None,False, False, ""),
        ("Centenario",            18.65604,  -90.28635,  None,False, False, ""),
        ("Escarcega",             18.60667,  -90.73444,  None,False, False, "https://en.wikipedia.org/wiki/Esc%C3%A1rcega"),

        # Section 1 -- south to Palenque
        ("Candelaria",            18.18437,  -91.04454,  None,False, False, ""),
        ("El Triunfo",            17.92368,  -91.17104,  None,False, False, ""),
        ("Boca del Cerro",        17.43031,  -91.49650,  None,False, False, ""),
        ("Tenosique",             17.46033,  -91.43043,  None,False, False, "https://en.wikipedia.org/wiki/Tenosique"),
        ("Palenque",              17.53332,  -91.97937,  6,   True,  True,  "https://en.wikipedia.org/wiki/Palenque"),

        # Section 2 -- north-west to Campeche and beyond
        ("Carrillo Puerto (Champoton)", 19.09283, -90.52310, None,False, False, ""),
        ("Edzna",                19.400,   -90.420,    None,False, False, "https://en.wikipedia.org/wiki/Edzn%C3%A1"),
        ("San Fco. Campeche",    19.82258,  -90.47660,  8,   True,  False, "https://en.wikipedia.org/wiki/Campeche_City"),
        ("Tenabo",               20.04001,  -90.24443,  None,False, False, ""),
        ("Hecelchakan",          20.16667,  -90.13333,  None,False, False, "https://en.wikipedia.org/wiki/Hecelchak%C3%A1n"),
        ("Calkini",              20.367,    -90.050,    None,False, False, "https://en.wikipedia.org/wiki/Calkin%C3%AD"),

        # Section 3 -- eastern Yucatan to Izamal
        ("Maxcanu",              20.583,    -89.983,    None,False, False, "https://en.wikipedia.org/wiki/Maxcan%C3%BA"),
        ("Uman",                 20.84891,  -89.75603,  None,False, False, "https://en.wikipedia.org/wiki/Um%C3%A1n_railway_station"),
        ("Teya Merida",          20.92883,  -89.51449,  9,   True,  False, "https://en.wikipedia.org/wiki/M%C3%A9rida,_Yucat%C3%A1n"),
        ("Tixkokob",             20.98704,  -89.39865,  None,False, False, ""),
        ("Izamal",               20.93608,  -89.08559,  None,False, False, "https://en.wikipedia.org/wiki/Izamal"),

        # Section 4 -- back east to Cancun
        ("Chichen-Itza",         20.72160,  -88.54874,  10,  False, True,  "https://en.wikipedia.org/wiki/Chichen_Itza"),
        ("Valladolid",           20.74033,  -88.19312,  None,False, False, "https://en.wikipedia.org/wiki/Valladolid,_Yucat%C3%A1n"),
        ("Nuevo Xcan",           20.87907,  -87.60277,  None,False, False, "https://en.wikipedia.org/wiki/Nuevo_Xc%C3%A1n_railway_station"),
        ("Leona Vicario",        20.97966,  -87.19723,  None,False, False, ""),
    ]

    # Snap estimated-only coords
    ROUGH_ESTIMATES = {"Edzna", "Conhuas", "Nicolas Bravo (Kohunlich)", "Limones"}
    for i, (name, lat, lon, day, ovn, key, wiki) in enumerate(stations):
        if name in ROUGH_ESTIMATES:
            nlat, nlon = estimate(lat, lon)
            stations[i] = (name, nlat, nlon, day, ovn, key, wiki)

    # Key archaeological sites
    sites = [
        ("Tulum (ruins)",                 20.2147,  -87.4290,  "https://en.wikipedia.org/wiki/Tulum_%28archaeological_site%29"),
        ("Calakmul (ruins)  UNESCO",      18.1056,  -89.8128,  "https://en.wikipedia.org/wiki/Calakmul"),
        ("Palenque (ruins)  UNESCO",      17.4840,  -91.9861,  "https://en.wikipedia.org/wiki/Palenque"),
        ("Chichen Itza (ruins)  UNESCO",  20.6829,  -88.5686,  "https://en.wikipedia.org/wiki/Chichen_Itza"),
    ]

    # Rental-car drive Xpujil -> Calakmul
    calakmul_road = [
        (18.52670, -89.39620),   # Xpujil station
        (18.1056,  -89.8128),    # Calakmul ruins
    ]

    # Build map
    m = folium.Map(location=[19.2, -89.5], zoom_start=7, tiles="OpenStreetMap")

    # Tren Maya track (exact OSM railway alignment)
    for w in track_ways:
        coords = [(p["lat"], p["lon"]) for p in w["geometry"]]
        PolyLine(coords, color="#d4651f", weight=3, opacity=0.85, tooltip="Tren Maya").add_to(m)

    # Calakmul drive
    PolyLine(
        calakmul_road, color="#8B4513", weight=3, opacity=0.7,
        dash_array="6, 6", tooltip="Drive Xpujil -> Calakmul  (~2 h, 110 km)",
    ).add_to(m)

    # Station markers
    for name, lat, lon, day, ovn, key, wiki in stations:
        pop = f"<b>{name}</b>"
        if key:
            pop += "  * <b>Key site</b>"
        if day:
            pop += f"<br>Day {day}"
        if ovn:
            pop += "  (overnight)"
        if wiki:
            pop += f'<br><a href="{wiki}" target="_blank">Wikipedia</a>'

        if key:
            ico = Icon(color="darkgreen", icon="monument", prefix="fa")
        elif ovn:
            ico = Icon(color="red", icon="bed", prefix="fa")
        else:
            ico = Icon(color="blue", icon="circle", prefix="fa")

        Marker(location=[lat, lon], popup=Popup(pop, max_width=300), tooltip=name, icon=ico).add_to(m)

    # Ruin site markers
    for name, lat, lon, wiki in sites:
        pop = f"<b>{name}</b>"
        if wiki:
            pop += f'<br><a href="{wiki}" target="_blank">Wikipedia</a>'
        Marker(
            location=[lat, lon], popup=Popup(pop, max_width=300), tooltip=name,
            icon=Icon(color="darkgreen", icon="star", prefix="fa"),
        ).add_to(m)

    # Cancun Airport
    Marker(
        location=[21.02808, -86.87281],
        popup=Popup("<b>Arrive &amp; Depart</b><br>London <-> Cancun (CUN)<br>Round-trip ~GBP 450-600", max_width=300),
        tooltip="Cancun Airport  (CUN)",
        icon=Icon(color="green", icon="plane", prefix="fa"),
    ).add_to(m)

    # Flight line
    folium.PolyLine(
        [(51.47, -0.4543), (21.02808, -86.87281)],
        color="green", weight=2, opacity=0.35, dash_array="4, 8",
        tooltip="Round-trip: London <-> Cancun  (~10.5 h)",
    ).add_to(m)

    # Legend overlay
    title_html = '''
<div style="position:fixed;top:10px;left:50%;transform:translateX(-50%);z-index:9999;
            background:white;padding:13px 22px;border-radius:8px;
            box-shadow:0 2px 10px rgba(0,0,0,.3);font-family:Arial,sans-serif;text-align:center;">
  <h2 style="margin:0 0 6px 0;color:#333;">Tren Maya  .  Complete Loop  .  12 Days</h2>
  <p style="margin:0;font-size:12px;color:#666;">
    <span style="color:#d4651f;">---</span> Railway &nbsp;
    <span style="color:#8B4513;">- - -</span> Calakmul drive &nbsp;
    <span style="color:red;">o</span> Overnight &nbsp;
    <span style="color:darkgreen;">o</span> Key site &nbsp;
    <span style="color:blue;">o</span> Station/Paradero &nbsp;
    <span style="color:green;">o</span> Airport
  </p>
</div>
'''
    m.get_root().html.add_child(Element(title_html))

    # Save
    m.save(str(OUTPUT_PATH))
    print(f"Map saved: {OUTPUT_PATH}")
    print(f"Track ways: {len(track_ways)}")
    print(f"Stations plotted: {len(stations)}")
    print(f"Sites plotted: {len(sites)}")


if __name__ == "__main__":
    main()
