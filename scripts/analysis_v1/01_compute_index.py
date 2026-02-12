import pandas as pd


def min_max(s: pd.Series) -> pd.Series:
    """
    Min-max normalization to [0, 1].
    If all values are identical, returns 0 for all rows to avoid division by zero.
    """
    smin, smax = s.min(), s.max()
    if pd.isna(smin) or pd.isna(smax) or smax == smin:
        return pd.Series([0] * len(s), index=s.index)
    return (s - smin) / (smax - smin)


# ------------------ Paths (GitHub-friendly) ------------------
DIST_PATH = "../data/raw/Distances_localites_health_facilities.csv"
FAC_PATH = "../data/raw/Health_Facilities_Communes.csv"

OUT_INDEX_PATH = "../data/processed/Health_Access_Index_Scenario_A.csv"

# ------------------ Read input CSV files ------------------
df1 = pd.read_csv(DIST_PATH)
df2 = pd.read_csv(FAC_PATH)

# Clean column names (avoid hidden spaces)
df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()

# ------------------ Distance processing ------------------
df1["distance_km"] = df1["Distance"] / 1000

df_distance = (
    df1.groupby("commune_norm", as_index=False)
       .agg(distance_m=("Distance", "mean"))
)
df_distance["distance_km"] = df_distance["distance_m"] / 1000
df_distance["dist_norm"] = min_max(df_distance["distance_km"])

# ------------------ Demographic pressure processing ------------------
df_pressure = (
    df2.groupby("commune_norm", as_index=False)
       .agg(
           nb_facilities=("Nom_SAN", "count"),
           population=("Population", "first")
       )
)

# Avoid division by zero in case nb_facilities == 0
df_pressure["pressure"] = df_pressure["population"] / df_pressure["nb_facilities"].replace(0, pd.NA)
df_pressure["pressure_norm"] = min_max(df_pressure["pressure"])

# ------------------ Facility type weighting (capacity/quality proxy) ------------------
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

# ------------------ Merge indicators ------------------
df_final = (
    df_distance.merge(df_pressure, on="commune_norm", how="left")
               .merge(df_ponderation, on="commune_norm", how="left")
)

# ------------------ Scenario A (baseline) ------------------
# Higher index = worse accessibility.
# We divide by pond because higher capacity should reduce the final "bad access" index.
df_final["idx_A"] = (df_final["dist_norm"] + df_final["pressure_norm"]) / df_final["pond"]
df_final["idx_A_norm"] = min_max(df_final["idx_A"])

# 4-class quantile classification (same as your project)
df_final["idx_A_class"] = pd.qcut(
    df_final["idx_A_norm"],
    q=4,
    labels=["Good access", "Medium access", "Poor access", "Very Poor access"],
    duplicates="drop"
)

# ------------------ Export (Scenario A) ------------------
out_cols = [
    "commune_norm",
    "distance_km", "dist_norm",
    "pressure", "pressure_norm",
    "pond",
    "idx_A", "idx_A_norm", "idx_A_class"
]

df_final[out_cols].to_csv(OUT_INDEX_PATH, index=False, encoding="utf-8")
print(f"Saved: {OUT_INDEX_PATH}")
