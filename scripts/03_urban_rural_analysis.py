import pandas as pd


def min_max(s: pd.Series) -> pd.Series:
    smin, smax = s.min(), s.max()
    if pd.isna(smin) or pd.isna(smax) or smax == smin:
        return pd.Series([0] * len(s), index=s.index)
    return (s - smin) / (smax - smin)


DIST_PATH = "../data/raw/Distances_localites_health_facilities.csv"
FAC_PATH = "../data/raw/Health_Facilities_Communes.csv"

OUT_URBAN_RURAL_TABLE = "../outputs/tables/Urban_Rural_Crosstab_Percent.csv"
OUT_COMMUNE_TABLE = "../outputs/tables/Commune_Access_with_AreaType.csv"


df1 = pd.read_csv(DIST_PATH)
df2 = pd.read_csv(FAC_PATH)

df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()

# ---- Distance ----
df1["distance_km"] = df1["Distance"] / 1000
df_distance = (
    df1.groupby("commune_norm", as_index=False)
       .agg(distance_m=("Distance", "mean"))
)
df_distance["distance_km"] = df_distance["distance_m"] / 1000
df_distance["dist_norm"] = min_max(df_distance["distance_km"])

# ---- Pressure ----
df_pressure = (
    df2.groupby("commune_norm", as_index=False)
       .agg(nb_facilities=("Nom_SAN", "count"),
            population=("Population", "first"))
)
df_pressure["pressure"] = df_pressure["population"] / df_pressure["nb_facilities"].replace(0, pd.NA)
df_pressure["pressure_norm"] = min_max(df_pressure["pressure"])

# ---- Capacity proxy ----
type_weight = {
    "CH_NAT": 1.0,
    "CH_DEP": 1.0,
    "HOPITAL_ZONE": 1.0,
    "CENTRE_SANTE": 0.6,
    "CLINIQUE": 0.6,
    "MATERNITE": 0.5,
    "DISPENSAIRE": 0.4,
    "UNITE_VILLAGEOISE": 0.2,
}
df2["ponderation"] = df2["Type"].map(type_weight)

df_ponderation = (
    df2.groupby("commune_norm", as_index=False)
       .agg(pond=("ponderation", "mean"))
)

# ---- Merge ----
df_final = (
    df_distance.merge(df_pressure, on="commune_norm", how="left")
               .merge(df_ponderation, on="commune_norm", how="left")
)

# ---- Scenario A index + class (same as your baseline) ----
df_final["idx_A"] = (df_final["dist_norm"] + df_final["pressure_norm"]) / df_final["pond"]
df_final["idx_A_norm"] = min_max(df_final["idx_A"])

df_final["idx_A_class"] = pd.qcut(
    df_final["idx_A_norm"],
    q=4,
    labels=["Good access", "Medium access", "Poor access", "Very Poor access"],
    duplicates="drop"
)

# -----------------------------
# Define urban communes (your exact list)
# -----------------------------
urban_communes = ["COTONOU", "PORTO-NOVO", "ABOMEY-CALAVI", "PARAKOU"]

df_final["urban"] = 0
df_final.loc[df_final["commune_norm"].isin(urban_communes), "urban"] = 1

df_final["area_type"] = df_final["urban"].map({1: "Urban", 0: "Rural"})

# -----------------------------
# Summary stats: Urban vs Rural (baseline index)
# -----------------------------
stats_urban_rural = (
    df_final.groupby("area_type")["idx_A_norm"]
           .agg(count="count", mean="mean", median="median", std="std", min="min", max="max")
)
print("\nUrban vs Rural stats (idx_A_norm):")
print(stats_urban_rural.round(3))

# -----------------------------
# Crosstab (%): area type vs access class
# -----------------------------
cross = pd.crosstab(
    df_final["area_type"],
    df_final["idx_A_class"],
    normalize="index"
) * 100

cross = cross.round(1)
print("\nUrban vs Rural distribution (%):")
print(cross)

# Export crosstab for report/portfolio
cross.to_csv(OUT_URBAN_RURAL_TABLE, encoding="utf-8")
print(f"\nSaved: {OUT_URBAN_RURAL_TABLE}")

# Export commune-level table for QGIS
out_cols = [
    "commune_norm", "area_type", "urban",
    "idx_A_norm", "idx_A_class",
    "dist_norm", "pressure_norm", "pond"
]
df_final[out_cols].to_csv(OUT_COMMUNE_TABLE, index=False, encoding="utf-8")
print(f"Saved: {OUT_COMMUNE_TABLE}")
