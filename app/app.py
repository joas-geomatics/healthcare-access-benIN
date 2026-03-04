from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import re
import unicodedata

st.set_page_config(page_title="Accessibilité santé – Bénin", layout="wide")
st.title("Accessibilité communale aux infrastructures de santé – Bénin")

# --- Chemins robustes (local + cloud) ---
APP_DIR = Path(__file__).parent
GEOJSON_PATH = APP_DIR / "communef.geojson"


def norm(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip().upper()
    s = unicodedata.normalize("NFKD", s)
    s = "".join([c for c in s if not unicodedata.combining(c)])  # enlève accents
    s = s.replace("’", "'")
    s = re.sub(r"\s+", " ", s)
    return s


@st.cache_data
def load_geojson(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

gj = load_geojson(GEOJSON_PATH)
st.caption(f"GeoJSON chargé : {len(gj.get('features', []))} communes")
for f in gj["features"]:
    f["properties"]["commune_id"] = norm(f["properties"].get("Com_norm"))

# --- DataFrame depuis les propriétés ---
rows = [feat["properties"] for feat in gj["features"]]
df = pd.DataFrame(rows)

# --- Renommage pour affichage propre ---
df = df.rename(columns={
    "Com_norm": "Commune",
    "hopital_com_csv_population": "Population",
    "hopital_com_csv_nb_infra": "Nb_infrastructures",
    "hopital_com_csv_niv_acces": "Niveau_accessibilite",
    "hopital_com_csv_idx_A_norm": "Indice"
})

# --- Nettoyage/formatage ---
df["commune_id"] = df["Commune"].apply(norm)
df["Indice"] = pd.to_numeric(df["Indice"], errors="coerce").round(2)
df["Population"] = pd.to_numeric(df["Population"], errors="coerce")
df["Nb_infrastructures"] = pd.to_numeric(df["Nb_infrastructures"], errors="coerce")

# Ordre + couleurs imposées
ordre = ["Tres faible", "Faible", "Moyen", "Bon acces"]
df["Niveau_accessibilite"] = pd.Categorical(df["Niveau_accessibilite"], categories=ordre, ordered=True)

couleurs = {
    "Bon acces": "#006400",    # vert foncé
    "Moyen": "#FFD700",        # jaune
    "Faible": "#FF8C00",       # orange
    "Tres faible": "#B22222"   # rouge
}

st.subheader("Carte interactive")

st.sidebar.header("Filtres")
sel = st.sidebar.multiselect("Niveau d’accessibilité", ordre, default=ordre)
df_map = df[df["Niveau_accessibilite"].isin(sel)].copy()

fig = px.choropleth_map(
    df,
    geojson=gj,
    locations="commune_id",
    featureidkey="properties.commune_id",   # champ dans le GeoJSON
    color="Niveau_accessibilite",
    category_orders={"Niveau_accessibilite": ordre},
    color_discrete_map=couleurs,
    hover_name="Commune",
    hover_data={
        "Population": True,
        "Nb_infrastructures": True,
        "Niveau_accessibilite": True,
        "Indice": True
    },
    
    center={"lat": 9.3, "lon": 2.3},
    zoom=5.7,
    opacity=0.85
)

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.plotly_chart(fig, width="stretch")

with st.expander("Voir les données"):
    st.dataframe(df.sort_values("Indice"), use_container_width=True)
