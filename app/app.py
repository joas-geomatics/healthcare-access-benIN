# from pathlib import Path
# import json
# import pandas as pd
# import streamlit as st
# import plotly.express as px
# import re
# import unicodedata

# st.set_page_config(page_title="Accessibilité santé – Bénin", layout="wide")
# st.title("Accessibilité communale aux infrastructures de santé – Bénin")

# # --- Chemins robustes (local + cloud) ---
# APP_DIR = Path(__file__).parent
# GEOJSON_PATH = APP_DIR / "communef.geojson"


# def norm(s: str) -> str:
#     if s is None:
#         return ""
#     s = str(s).strip().upper()
#     s = unicodedata.normalize("NFKD", s)
#     s = "".join([c for c in s if not unicodedata.combining(c)])  # enlève accents
#     s = s.replace("’", "'")
#     s = re.sub(r"\s+", " ", s)
#     return s


# @st.cache_data
# def load_geojson(path: Path):
#     with open(path, "r", encoding="utf-8") as f:
#         gj = json.load(f)

#     # IMPORTANT: on prépare commune_id ici (dans le cache)
#     for feat in gj.get("features", []):
#         props = feat.setdefault("properties", {})
#         props["commune_id"] = norm(props.get("Com_norm"))
#     return gj


# gj = load_geojson(GEOJSON_PATH)
# st.caption(f"GeoJSON chargé : {len(gj.get('features', []))} communes")


# # --- DataFrame depuis les propriétés ---
# rows = [feat["properties"] for feat in gj["features"]]
# df = pd.DataFrame(rows)

# # --- Renommage pour affichage propre ---
# df = df.rename(columns={
#     "Com_norm": "Commune",
#     "hopital_com_csv_population": "Population",
#     "hopital_com_csv_nb_infra": "Nb_infrastructures",
#     "hopital_com_csv_niv_acces": "Niveau_accessibilite",
#     "hopital_com_csv_idx_A_norm": "Indice"
# })

# # --- Nettoyage/formatage ---
# df["commune_id"] = df["Commune"].apply(norm)
# df["Indice"] = pd.to_numeric(df["Indice"], errors="coerce").round(2)
# df["Population"] = pd.to_numeric(df["Population"], errors="coerce")
# df["Nb_infrastructures"] = pd.to_numeric(df["Nb_infrastructures"], errors="coerce")

# # Ordre + couleurs imposées
# ordre = ["Tres faible", "Faible", "Moyen", "Bon acces"]
# df["Niveau_accessibilite"] = pd.Categorical(df["Niveau_accessibilite"], categories=ordre, ordered=True)

# couleurs = {
#     "Bon acces": "#006400",    # vert foncé
#     "Moyen": "#FFD700",        # jaune
#     "Faible": "#FF8C00",       # orange
#     "Tres faible": "#B22222"   # rouge
# }

# st.subheader("Carte interactive")

# st.sidebar.header("Filtres")
# sel = st.sidebar.multiselect("Niveau d’accessibilité", ordre, default=ordre)
# df_map = df[df["Niveau_accessibilite"].isin(sel)].copy()

# with st.expander("Voir les données"):
#     st.dataframe(df.sort_values("Indice"), width="stretch")

# fig = px.choropleth_mapbox(
#     df_map,
#     geojson=gj,
#     locations="commune_id",
#     featureidkey="properties.commune_id",
#     color="Niveau_accessibilite",
#     category_orders={"Niveau_accessibilite": ordre},
#     color_discrete_map=couleurs,
#     hover_name="Commune",
#     hover_data={
#         "Population": True,
#         "Nb_infrastructures": True,
#         "Niveau_accessibilite": True,
#         "Indice": True
#     },
#     center={"lat": 9.3, "lon": 2.3},
#     zoom=5.7,
#     opacity=0.85,
#     mapbox_style="open-street-map"
# )

# fig.update_layout(
#     margin={"r":0,"t":0,"l":0,"b":0},
#     height=650
# )

# st.plotly_chart(fig, width="stretch")





# st.set_page_config(page_title="Carte du Bénin", layout="wide")

# st.title("Carte simple du Bénin")

# # Coordonnées de Cotonou
# data = pd.DataFrame({
#     "Ville": ["Cotonou"],
#     "lat": [6.3654],
#     "lon": [2.4183]
# })

# fig = px.scatter_mapbox(
#     data,
#     lat="lat",
#     lon="lon",
#     hover_name="Ville",
#     zoom=7,
#     center={"lat": 6.4, "lon": 2.4},
#     height=600
# )

# fig.update_layout(
#     mapbox_style="open-street-map",
#     margin={"r":0,"t":0,"l":0,"b":0}
# )

# st.plotly_chart(fig, width="stretch")


# from pathlib import Path
# import json
# import streamlit as st
# import pydeck as pdk

# st.set_page_config(page_title="Test GeoJSON Bénin", layout="wide")
# st.title("Test carte GeoJSON – Bénin")

# APP_DIR = Path(__file__).parent
# GEOJSON_PATH = APP_DIR / "communef.geojson"

# with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
#     gj = json.load(f)

# st.caption(f"GeoJSON chargé : {len(gj.get('features', []))} communes")

# layer = pdk.Layer(
#     "GeoJsonLayer",
#     gj,
#     opacity=0.6,
#     stroked=True,
#     filled=True,
#     extruded=False,
#     wireframe=False,
#     get_fill_color=[200, 30, 0, 120],
#     get_line_color=[0, 0, 0, 180],
#     line_width_min_pixels=1,
#     pickable=True,
# )

# view_state = pdk.ViewState(
#     latitude=9.3,
#     longitude=2.3,
#     zoom=6,
#     pitch=0
# )

# deck = pdk.Deck(
#     layers=[layer],
#     initial_view_state=view_state,
#     map_style=None
# )

# st.pydeck_chart(deck, width="stretch")


# Crequestion : comment préparer un GeoJSON pour une carte web (simplification, nettoyage, etc.) ?

# import geopandas as gpd

# gdf = gpd.read_file(r"app\communef.geojson")

# # Reprojection en WGS84 si nécessaire
# if gdf.crs is None:
#     gdf = gdf.set_crs(epsg=4326)
# elif gdf.crs.to_epsg() != 4326:
#     gdf = gdf.to_crs(epsg=4326)

# # Corriger les géométries invalides
# gdf = gdf[gdf.geometry.notnull()].copy()
# gdf = gdf[~gdf.geometry.is_empty].copy()
# gdf["geometry"] = gdf.buffer(0)

# # Garder seulement les colonnes utiles
# cols = [
#     "Com_norm",
#     "hopital_com_csv_population",
#     "hopital_com_csv_nb_infra",
#     "hopital_com_csv_niv_acces",
#     "hopital_com_csv_idx_A_norm",
#     "geometry"
# ]
# cols = [c for c in cols if c in gdf.columns]
# gdf = gdf[cols].copy()

# # Simplification légère pour le web
# gdf["geometry"] = gdf.geometry.simplify(0.001, preserve_topology=True)

# # Export
# gdf.to_file("communef_web.geojson", driver="GeoJSON")
# print("Fichier généré : communef_web.geojson")


from pathlib import Path
import json
import streamlit as st
import pydeck as pdk

st.set_page_config(page_title="Test GeoJSON Bénin", layout="wide")
st.title("Test carte GeoJSON – Bénin")

APP_DIR = Path(__file__).parent
GEOJSON_PATH = APP_DIR / "communef_web.geojson"

with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    gj = json.load(f)

st.caption(f"GeoJSON chargé : {len(gj.get('features', []))} communes")

layer = pdk.Layer(
    "GeoJsonLayer",
    gj,
    opacity=0.6,
    stroked=True,
    filled=True,
    extruded=False,
    wireframe=False,
    get_fill_color=[200, 30, 0, 120],
    get_line_color=[0, 0, 0, 180],
    line_width_min_pixels=1,
    pickable=True,
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=pdk.ViewState(
        latitude=9.3,
        longitude=2.3,
        zoom=6,
        pitch=0,
    ),
    map_style=None,
)

st.pydeck_chart(deck, width="stretch")