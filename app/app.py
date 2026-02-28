from pathlib import Path
import json
import streamlit as st
import pydeck as pdk
import math


st.title("Niveau d'accessibilité aux infrastructures de santé au Bénin")

APP_DIR = Path(__file__).parent
GEOJSON_PATH = APP_DIR / "commune.geojson"

@st.cache_data
def load_geojson(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


try:
    gj = load_geojson(GEOJSON_PATH)
    st.write("✅ GeoJSON chargé :", len(gj["features"]), "communes")
except Exception as e:
    st.error(f"Impossible de charger le GeoJSON : {e}")
    st.stop()



# # ggggg
# st.write("Type racine:", gj.get("type"))
# st.write("Clés racine:", list(gj.keys())[:20])

# # regarder 1 feature
# f0 = gj["features"][0]
# st.write("Feature keys:", list(f0.keys()))
# st.write("Geometry type:", None if f0.get("geometry") is None else f0["geometry"].get("type"))
# st.write("Geometry preview:", f0.get("geometry"))


# def collect_lonlat(geojson, nmax=3000):
#     lons, lats = [], []
#     def walk(c):
#         nonlocal lons, lats
#         if (
#             isinstance(c, (list, tuple))
#             and len(c) >= 2
#             and all(isinstance(x, (int, float)) for x in c[:2])
#         ):
#             lon, lat = c[0], c[1]
#             lons.append(lon)
#             lats.append(lat)

#     for feat in geojson.get("features", []):
#         geom = feat.get("geometry")
#         if not geom:
#             continue
#         walk(geom.get("coordinates"))
#         if len(lons) >= nmax:
#             break
#     return lons, lats

# lons, lats = collect_lonlat(gj)

# if not lons or not lats:
#     st.error("❌ Aucune coordonnée trouvée dans le GeoJSON.")
#     st.stop()

# st.write("🔎 Diagnostics coordonnées")
# st.write("Lon min/max:", min(lons), max(lons))
# st.write("Lat min/max:", min(lats), max(lats))

# # Test CRS
# if max(map(abs, lons)) > 180 or max(map(abs, lats)) > 90:
#     st.error("❌ Ton GeoJSON n'est pas en WGS84 (lon/lat). Il est probablement en UTM (mètres).")
#     st.info("➡️ Reprojette dans QGIS en EPSG:4326 puis ré-exporte en GeoJSON.")
#     st.stop()
# else:
#     st.success("✅ Coordonnées WGS84 (lon/lat) détectées. La carte devrait s'afficher.")





# Couleurs imposées (RGBA)
COLOR_MAP = {
    "Bon acces": [0, 100, 0, 180],      # vert foncé
    "Moyen": [255, 215, 0, 180],        # jaune
    "Faible": [255, 140, 0, 180],       # orange
    "Tres faible": [178, 34, 34, 180],  # rouge
}

def feature_color(feat):
    niv = feat["properties"].get("hopital_com_csv_niv_acces", "Faible")
    return COLOR_MAP.get(niv, [200, 200, 200, 120])

# Ajouter une couleur calculée à chaque feature
for feat in gj["features"]:
    feat["properties"]["__fill_color"] = feature_color(feat)

tooltip = {
    "html": """
    <b>{Com_norm}</b><br/>
    Population : {hopital_com_csv_population}<br/>
    Nb infrastructures : {hopital_com_csv_nb_infra}<br/>
    Niveau : {hopital_com_csv_niv_acces}<br/>
    Indice (0–1) : {hopital_com_csv_idx_A_norm}
    """,
    "style": {"backgroundColor": "white", "color": "black"}
}

layer = pdk.Layer(
    "GeoJsonLayer",
    data=gj,
    opacity=0.8,
    stroked=True,
    filled=True,
    get_fill_color="properties.__fill_color",
    get_line_color=[120, 120, 120, 200],
    line_width_min_pixels=0.6,
    pickable=True,
)

view_state = pdk.ViewState(latitude=9.3, longitude=2.3, zoom=5.6)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tooltip,
    map_style=None,
)

st.pydeck_chart(deck, use_container_width=True)
