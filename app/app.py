import streamlit as st
import json
import pydeck as pdk
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Accessibilité santé – Bénin", layout="wide")
st.title("Accessibilité communale aux infrastructures de santé – Bénin")

APP_DIR = Path(__file__).parent
GEOJSON_PATH = APP_DIR / "communef_web.geojson"

with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    gj = json.load(f)

# --- DataFrame à partir des propriétés du GeoJSON ---
rows = [feat["properties"] for feat in gj["features"]]
df = pd.DataFrame(rows)

df = df.rename(columns={
    "Com_norm": "Commune",
    "hopital_com_csv_population": "Population",
    "hopital_com_csv_nb_infra": "Nb_infrastructures",
    "hopital_com_csv_niv_acces": "Niveau_accessibilite",
    "hopital_com_csv_idx_A_norm": "Indice"
})

df["Indice"] = pd.to_numeric(df["Indice"], errors="coerce").round(2)
df["Population"] = pd.to_numeric(df["Population"], errors="coerce")
df["Nb_infrastructures"] = pd.to_numeric(df["Nb_infrastructures"], errors="coerce")

ordre = ["Tres faible", "Faible", "Moyen", "Bon acces"]

# --- Couleurs ---
colors = {
    "Tres faible": [178, 34, 34, 160],
    "Faible": [255, 140, 0, 160],
    "Moyen": [255, 215, 0, 160],
    "Bon acces": [0, 100, 0, 160],
}

# =========================
# SIDEBAR
# =========================
st.sidebar.header("Filtres")

niveaux_selectionnes = st.sidebar.multiselect(
    "Niveau d'accès",
    ordre,
    default=ordre
)

# Filtrer le dataframe pour la liste
df_filtre = df[df["Niveau_accessibilite"].isin(niveaux_selectionnes)].copy()

st.sidebar.markdown("### Communes par niveau")

for niveau in ordre:
    if niveau in niveaux_selectionnes:
        communes = sorted(
            df_filtre.loc[df_filtre["Niveau_accessibilite"] == niveau, "Commune"]
            .dropna()
            .astype(str)
            .tolist()
        )
        with st.sidebar.expander(f"{niveau} ({len(communes)})", expanded=False):
            if communes:
                for commune in communes:
                    st.write(f"- {commune}")
            else:
                st.write("Aucune commune")

# =========================
# FILTRAGE DU GEOJSON
# =========================
features_filtrees = []

for feat in gj["features"]:
    niveau = feat["properties"].get("hopital_com_csv_niv_acces")
    if niveau in niveaux_selectionnes:
        feat["properties"]["color"] = colors.get(niveau, [150, 150, 150, 150])
        features_filtrees.append(feat)

gj_filtre = {
    "type": "FeatureCollection",
    "features": features_filtrees
}

# =========================
# CARTE
# =========================
layer = pdk.Layer(
    "GeoJsonLayer",
    gj_filtre,
    opacity=0.7,
    stroked=True,
    filled=True,
    get_fill_color="properties.color",
    get_line_color=[0, 0, 0],
    line_width_min_pixels=1,
    pickable=True
)

tooltip = {
    "html": """
    <b>Commune :</b> {Com_norm}<br/>
    <b>Niveau :</b> {hopital_com_csv_niv_acces}<br/>
    <b>Population :</b> {hopital_com_csv_population}<br/>
    <b>Infrastructures :</b> {hopital_com_csv_nb_infra}<br/>
    <b>Indice :</b> {hopital_com_csv_idx_A_norm}
    """,
    "style": {"backgroundColor": "white", "color": "black"}
}

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=pdk.ViewState(
        latitude=9.0,
        longitude=2.4,
        zoom=7,
        pitch=0
    ),
    map_style="light",
    tooltip=tooltip
)

st.pydeck_chart(deck, width="stretch")