import pandas as pd
from utils_indicators import load_layers, build_indicators, min_max

COMMUNES_PATH = "../data/raw/ADM_COMMUNE.shp"
LOCALITES_PATH = "../data/raw/LOCALITES.shp"
FACILITIES_PATH = "../data/raw/INF_STRUCTURE_SANTE.shp"

OUT_URBAN_RURAL_TABLE = "../outputs/tables/Urban_Rural_Crosstab_Percent.csv"
OUT_COMMUNE_TABLE = "../outputs/tables/Commune_Access_with_AreaType.csv"

communes, localites, fac = load_layers(COMMUNES_PATH, LOCALITES_PATH, FACILITIES_PATH, target_epsg=32631)

df = build_indicators(communes, localites, fac, commune_col="Nom_COM", pop_col="Population", type_col="Type")

# Scenario A (baseline)
df["idx_A"] = (df["dist_norm"] + df["pressure_norm"]) / df["pond"]
df["idx_A_norm"] = min_max(df["idx_A"])

df["idx_A_class"] = pd.qcut(
    df["idx_A_norm"],
    q=4,
    labels=["Good access", "Medium access", "Poor access", "Very Poor access"],
    duplicates="drop"
)

# Urban communes list (same as yours)
urban_communes = ["COTONOU", "PORTO-NOVO", "ABOMEY-CALAVI", "PARAKOU"]

# If your commune names are not already uppercase, enforce it:
df["commune_upper"] = df["Nom_COM"].astype(str).str.upper()

df["urban"] = 0
df.loc[df["commune_upper"].isin(urban_communes), "urban"] = 1
df["area_type"] = df["urban"].map({1: "Urban", 0: "Rural"})

# Stats
stats_urban_rural = (
    df.groupby("area_type")["idx_A_norm"]
      .agg(count="count", mean="mean", median="median", std="std", min="min", max="max")
)
print("\nUrban vs Rural stats (idx_A_norm):")
print(stats_urban_rural.round(3))

# Crosstab (%)
cross = pd.crosstab(
    df["area_type"],
    df["idx_A_class"],
    normalize="index"
) * 100

cross = cross.round(1)
print("\nUrban vs Rural distribution (%):")
print(cross)

cross.to_csv(OUT_URBAN_RURAL_TABLE, encoding="utf-8")
print(f"\nSaved: {OUT_URBAN_RURAL_TABLE}")

# Commune-level export for QGIS
out_cols = [
    "Nom_COM", "area_type", "urban",
    "idx_A_norm", "idx_A_class",
    "dist_norm", "pressure_norm", "pond"
]
df[out_cols].to_csv(OUT_COMMUNE_TABLE, index=False, encoding="utf-8")
print(f"Saved: {OUT_COMMUNE_TABLE}")
