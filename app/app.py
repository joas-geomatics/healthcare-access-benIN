from pathlib import Path
import json
import streamlit as st
import pydeck as pdk


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
