import json
import pandas as pd
import plotly.express as px
import streamlit as st

st.subheader("Niveau d'accessibilité aux infrastructures de santé au Bénin")

with open("app/commune.geojson", "r", encoding="utf-8") as f:
    gj = json.load(f)

rows = [feat["properties"] for feat in gj["features"]]
df = pd.DataFrame(rows)

df = df.rename(columns={
    "Com_norm": "Commune",
    "hopital_com_csv_population": "Population",
    "hopital_com_csv_nb_infra": "Nb_infra",
    "hopital_com_csv_niv_acces": "Accessibilité",
    "hopital_com_csv_idx_A_norm": "Indice"
})

# Formatage
df["Population"] = df["Population"].apply(lambda x: f"{int(x):,}".replace(",", " "))
df["Indice"] = df["Indice"].round(2)

# --- IMPORTANT : forcer l'ordre des catégories ---
ordre = ["Tres faible", "Faible", "Moyen", "Bon acces"]
df["Accessibilité"] = pd.Categorical(df["Accessibilité"], categories=ordre, ordered=True)

# --- IMPORTANT : forcer les couleurs ---
couleurs = {
    "Bon acces": "#006400",   # vert foncé
    "Moyen": "#FFD700",       # jaune
    "Faible": "#FF8C00",      # orange
    "Tres faible": "#B22222"  # rouge
}

fig = px.choropleth_mapbox(
    df,
    geojson=gj,
    locations="Commune",
    featureidkey="properties.Com_norm",
    hover_name="Commune",
    color="Accessibilité",
    category_orders={"Accessibilité": ordre},
    color_discrete_map=couleurs,
    hover_data={
        "Population": True,
        "Nb_infra": True,
        "Accessibilité": True,
        "Indice": True
    },
    mapbox_style="carto-positron",
    zoom=5.7,
    center={"lat": 9.3, "lon": 2.3},
    opacity=0.85
)

fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    legend_title_text="Accessibilité"
)

st.plotly_chart(fig, use_container_width=True)