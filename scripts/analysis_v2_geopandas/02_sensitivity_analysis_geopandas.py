import pandas as pd
import geopandas as gpd
from utils_indicators import load_layers, build_indicators, min_max

COMMUNES_PATH = "../data/raw/ADM_COMMUNE.shp"
LOCALITES_PATH = "../data/raw/LOCALITES.shp"
FACILITIES_PATH = "../data/raw/INF_STRUCTURE_SANTE.shp"

OUT_SCENARIOS_PATH = "../outputs/tables/Health_Access_Sensitivity_Scenarios.csv"
OUT_GPKG_PATH = "../data/processed/Health_Access_Sensitivity_Scenarios.gpkg"

communes, localites, fac = load_layers(COMMUNES_PATH, LOCALITES_PATH, FACILITIES_PATH, target_epsg=32631)

df = build_indicators(communes, localites, fac, commune_col="Nom_COM", pop_col="Population", type_col="Type")

# Scenarios
df["idx_A"] = (df["dist_norm"] + df["pressure_norm"]) / df["pond"]
df["idx_B"] = ((2 * df["dist_norm"]) + df["pressure_norm"]) / df["pond"]
df["idx_C"] = (df["dist_norm"] + (2 * df["pressure_norm"])) / df["pond"]
df["idx_D"] = (df["dist_norm"] + df["pressure_norm"]) / (df["pond"] ** 2)

for c in ["idx_A", "idx_B", "idx_C", "idx_D"]:
    df[f"{c}_norm"] = min_max(df[c])

for c in ["idx_A", "idx_B", "idx_C", "idx_D"]:
    df[f"{c}_class"] = pd.qcut(
        df[f"{c}_norm"],
        q=4,
        labels=["Good access", "Medium access", "Poor access", "Very Poor access"],
        duplicates="drop"
    )

# Changes vs baseline
baseline = "idx_A_class"
for c in ["idx_B_class", "idx_C_class", "idx_D_class"]:
    df[f"change_{c}"] = (df[c] != df[baseline])

df["nb_changes"] = (
    df["change_idx_B_class"].astype(int) +
    df["change_idx_C_class"].astype(int) +
    df["change_idx_D_class"].astype(int)
)

df["stability"] = "Stable"
df.loc[df["nb_changes"] == 1, "stability"] = "Slightly sensitive"
df.loc[df["nb_changes"] == 2, "stability"] = "Sensitive"
df.loc[df["nb_changes"] >= 3, "stability"] = "Highly sensitive"

out_cols = [
    "Nom_COM",
    "dist_norm", "pressure_norm", "pond",
    "idx_A_norm", "idx_A_class",
    "idx_B_norm", "idx_B_class",
    "idx_C_norm", "idx_C_class",
    "idx_D_norm", "idx_D_class",
    "nb_changes", "stability"
]

df[out_cols].to_csv(OUT_SCENARIOS_PATH, index=False, encoding="utf-8")
print(f"Saved: {OUT_SCENARIOS_PATH}")

gdf_out = communes.merge(df[out_cols], on="Nom_COM", how="left")
gdf_out.to_file(OUT_GPKG_PATH, driver="GPKG")
print(f"Saved: {OUT_GPKG_PATH}")
