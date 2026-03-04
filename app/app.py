from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Accessibilité santé - Bénin", layout="wide")
st.title("Accessibilité communale aux infrastructures de santé - Bénin")

# --- Chemins robustes (local + cloud) ---
APP_DIR = Path(__file__).parent
GEOJSON_PATH = APP_DIR / "commune.geojson"

@st.cache_data
def load_geojson(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

gj = load_geojson(GEOJSON_PATH)
st.caption(f"Total : {len(gj.get('features', []))} communes")

# --- DataFrame depuis les propriétés ---
rows = [feat["properties"] for feat in gj["features"]]
df = pd.DataFrame(rows)

# --- Renommage pour affichage propre ---
df = df.rename(columns={
    "Com_norm": "Commune",
    "hopital_com_csv_population": "Population",
    "hopital_com_csv_nb_infra": "Nb_infra",
    "hopital_com_csv_niv_acces": "Niv_accessibilite",
    "hopital_com_csv_idx_A_norm": "Indice"
})

# --- Nettoyage/formatage ---
df["Indice"] = pd.to_numeric(df["Indice"], errors="coerce").round(2)
df["Population"] = pd.to_numeric(df["Population"], errors="coerce")
df["Nb_infra"] = pd.to_numeric(df["Nb_infra"], errors="coerce")

# Ordre + couleurs imposées
ordre = ["Tres faible", "Faible", "Moyen", "Bon acces"]
df["Niv_accessibilite"] = pd.Categorical(df["Niv_accessibilite"], categories=ordre, ordered=True)

couleurs = {
    "Bon acces": "#006400",    # vert foncé
    "Moyen": "#FFD700",        # jaune
    "Faible": "#FF8C00",       # orange
    "Tres faible": "#B22222"   # rouge
}

st.subheader("Carte interactive")
st.sidebar.header("Filtres")
sel = st.sidebar.multiselect("Niveau d'accessibilité", ordre, default=ordre)
df_map = df[df["Niv_accessibilite"].isin(sel)].copy()
fig = px.choropleth_mapbox(
    df_map,
    geojson=gj,
    locations="Commune",
    featureidkey="properties.Com_norm",   # champ dans le GeoJSON
    color="Niv_accessibilite",
    category_orders={"Niv_accessibilite": ordre},
    color_discrete_map=couleurs,
    hover_name="Commune",
    hover_data={
        "Population": True,
        "Nb_infra": True,
        "Niv_accessibilite": True,
        "Indice": True
    },
    mapbox_style="carto-positron",  # pas besoin de token
    center={"lat": 9.3, "lon": 2.3},
    zoom=5.7,
    opacity=0.85
)

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.plotly_chart(fig, use_container_width=True)

with st.expander("Voir les données"):
    st.dataframe(df.sort_values("Indice"), use_container_width=True)

