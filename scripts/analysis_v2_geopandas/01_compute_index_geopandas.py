import pandas as pd
import geopandas as gpd
from utils_indicators import load_layers, build_indicators, min_max

COMMUNES_PATH = "../data/raw/ADM_COMMUNE.shp"
LOCALITES_PATH = "../data/raw/LOCALITES.shp"
FACILITIES_PATH = "../data/raw/INF_STRUCTURE_SANTE.shp"

OUT_INDEX_PATH = "../data/processed/Health_Access_Index_Scenario_A.csv"
OUT_GPKG_PATH = "../data/processed/Health_Access_Index_Scenario_A.gpkg"

communes, localites, fac = load_layers(COMMUNES_PATH, LOCALITES_PATH, FACILITIES_PATH, target_epsg=32631)

df = build_indicators(communes, localites, fac, commune_col="Nom_COM", pop_col="Population", type_col="Type")

df["idx_A"] = (df["dist_norm"] + df["pressure_norm"]) / df["pond"]
df["idx_A_norm"] = min_max(df["idx_A"])

df["idx_A_class"] = pd.qcut(
    df["idx_A_norm"],
    q=4,
    labels=["Good access", "Medium access", "Poor access", "Very Poor access"],
    duplicates="drop"
)

out_cols = [
    "Nom_COM",
    "distance_km", "dist_norm",
    "nb_facilities",
    "pressure", "pressure_norm",
    "pond",
    "idx_A", "idx_A_norm", "idx_A_class"
]

df[out_cols].to_csv(OUT_INDEX_PATH, index=False, encoding="utf-8")
print(f"Saved: {OUT_INDEX_PATH}")

gdf_out = communes.merge(df[out_cols], on="Nom_COM", how="left")
gdf_out.to_file(OUT_GPKG_PATH, driver="GPKG")
print(f"Saved: {OUT_GPKG_PATH}")
