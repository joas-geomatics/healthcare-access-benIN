import pandas as pd


def min_max(s: pd.Series) -> pd.Series:
    smin, smax = s.min(), s.max()
    if pd.isna(smin) or pd.isna(smax) or smax == smin:
        return pd.Series([0] * len(s), index=s.index)
    return (s - smin) / (smax - smin)


DIST_PATH = "../data/raw/Distances_localites_health_facilities.csv"
FAC_PATH = "../data/raw/Health_Facilities_Communes.csv"

OUT_SCENARIOS_PATH = "../outputs/tables/Health_Access_Sensitivity_Scenarios.csv"


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

# ---- Capacity proxy (facility type weighting) ----
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

# -----------------------------
# Sensitivity scenarios
# -----------------------------
# A: Balanced (baseline)
df_final["idx_A"] = (df_final["dist_norm"] + df_final["pressure_norm"]) / df_final["pond"]

# B: Distance prioritized
df_final["idx_B"] = ((2 * df_final["dist_norm"]) + df_final["pressure_norm"]) / df_final["pond"]

# C: Pressure prioritized
df_final["idx_C"] = (df_final["dist_norm"] + (2 * df_final["pressure_norm"])) / df_final["pond"]

# D: Strong facility-type effect
df_final["idx_D"] = (df_final["dist_norm"] + df_final["pressure_norm"]) / (df_final["pond"] ** 2)

# Normalize each scenario index (0–1)
for c in ["idx_A", "idx_B", "idx_C", "idx_D"]:
    df_final[f"{c}_norm"] = min_max(df_final[c])

# Classify each scenario into 4 quantile classes
for c in ["idx_A", "idx_B", "idx_C", "idx_D"]:
    df_final[f"{c}_class"] = pd.qcut(
        df_final[f"{c}_norm"],
        q=4,
        labels=["Good access", "Medium access", "Poor access", "Very Poor access"],
        duplicates="drop"
    )

# -----------------------------
# Changes vs baseline (A)
# -----------------------------
baseline = "idx_A_class"
for c in ["idx_B_class", "idx_C_class", "idx_D_class"]:
    df_final[f"change_{c}"] = (df_final[c] != df_final[baseline])

df_final["nb_changes"] = (
    df_final["change_idx_B_class"].astype(int) +
    df_final["change_idx_C_class"].astype(int) +
    df_final["change_idx_D_class"].astype(int)
)

# Stability label
df_final["stability"] = "Stable"
df_final.loc[df_final["nb_changes"] == 1, "stability"] = "Slightly sensitive"
df_final.loc[df_final["nb_changes"] == 2, "stability"] = "Sensitive"
df_final.loc[df_final["nb_changes"] >= 3, "stability"] = "Highly sensitive"

# -----------------------------
# Export (table for QGIS)
# -----------------------------
out_cols = [
    "commune_norm",
    "dist_norm", "pressure_norm", "pond",
    "idx_A_norm", "idx_A_class",
    "idx_B_norm", "idx_B_class",
    "idx_C_norm", "idx_C_class",
    "idx_D_norm", "idx_D_class",
    "nb_changes", "stability"
]

df_final[out_cols].to_csv(OUT_SCENARIOS_PATH, index=False, encoding="utf-8")
print(f"Saved: {OUT_SCENARIOS_PATH}")

# Optional quick summary in console
summary = pd.Series({
    "Scenario B changes": df_final["change_idx_B_class"].sum(),
    "Scenario C changes": df_final["change_idx_C_class"].sum(),
    "Scenario D changes": df_final["change_idx_D_class"].sum(),
})
print("\nChanges vs baseline (A):")
print(summary)
