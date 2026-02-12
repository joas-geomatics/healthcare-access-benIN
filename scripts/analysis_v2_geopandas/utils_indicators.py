import geopandas as gpd
import pandas as pd


def min_max(s: pd.Series) -> pd.Series:
    smin, smax = s.min(), s.max()
    if pd.isna(smin) or pd.isna(smax) or smax == smin:
        return pd.Series([0] * len(s), index=s.index)
    return (s - smin) / (smax - smin)


def load_layers(communes_path: str,
                localites_path: str,
                facilities_path: str,
                target_epsg: int = 32631):
    communes = gpd.read_file(communes_path)
    localites = gpd.read_file(localites_path)
    facilities = gpd.read_file(facilities_path)

    communes.columns = communes.columns.str.strip()
    localites.columns = localites.columns.str.strip()
    facilities.columns = facilities.columns.str.strip()

    communes = communes.to_crs(epsg=target_epsg)
    localites = localites.to_crs(communes.crs)
    facilities = facilities.to_crs(communes.crs)

    return communes, localites, facilities


def build_indicators(communes: gpd.GeoDataFrame,
                     localites: gpd.GeoDataFrame,
                     facilities: gpd.GeoDataFrame,
                     commune_col: str = "Nom_COM",
                     pop_col: str = "Population",
                     type_col: str = "Type",
                     type_weight: dict | None = None,
                     fill_pond_if_missing: float = 0.2,
                     fill_norm_if_missing: float = 1.0) -> pd.DataFrame:
    """
    Builds commune-level indicators:
      - distance_km + dist_norm (locality -> nearest facility then mean by commune)
      - nb_facilities + pressure + pressure_norm
      - pond (mean weight by commune)

    Returns pandas DataFrame keyed by commune_col including pop_col.
    """
    if type_weight is None:
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

    communes = communes.copy()
    communes[pop_col] = pd.to_numeric(communes[pop_col], errors="coerce").fillna(0).astype(int)

    base = communes[[commune_col, pop_col]].drop_duplicates()

    # --- Distance: locality -> nearest facility (meters), then attach commune and average
    nearest_loc_fac = gpd.sjoin_nearest(
        localites[["geometry"]].copy(),
        facilities[["geometry"]].copy(),
        how="left",
        distance_col="dist_m",
    )

    loc_with_commune = gpd.sjoin(
        nearest_loc_fac,
        communes[[commune_col, "geometry"]],
        predicate="within",
        how="left",
    )

    df_distance = (
        loc_with_commune.dropna(subset=[commune_col])
        .groupby(commune_col, as_index=False)
        .agg(distance_m=("dist_m", "mean"))
    )
    df_distance["distance_km"] = df_distance["distance_m"] / 1000
    df_distance["dist_norm"] = min_max(df_distance["distance_km"])

    # --- Facilities in commune: count + pressure + pond
    fac_with_commune = gpd.sjoin(
        facilities[[type_col, "geometry"]],
        communes[[commune_col, pop_col, "geometry"]],
        predicate="within",
        how="left",
    )

    df_pressure = (
        fac_with_commune.groupby(commune_col, as_index=False)
        .agg(nb_facilities=(type_col, "count"),
             population=(pop_col, "first"))
    )
    df_pressure["pressure"] = df_pressure["population"] / df_pressure["nb_facilities"].replace(0, pd.NA)
    df_pressure["pressure_norm"] = min_max(df_pressure["pressure"])

    fac_with_commune["ponderation"] = fac_with_commune[type_col].map(type_weight)
    df_pond = (
        fac_with_commune.groupby(commune_col, as_index=False)
        .agg(pond=("ponderation", "mean"))
    )

    # --- Merge indicators
    df = (
        base
        .merge(df_distance[[commune_col, "distance_km", "dist_norm"]], on=commune_col, how="left")
        .merge(df_pressure[[commune_col, "nb_facilities", "pressure", "pressure_norm"]], on=commune_col, how="left")
        .merge(df_pond[[commune_col, "pond"]], on=commune_col, how="left")
    )

    # conservative fills (avoid crash + keep "worst access" logic)
    df["nb_facilities"] = df["nb_facilities"].fillna(0).astype(int)
    df["pond"] = df["pond"].fillna(fill_pond_if_missing)
    df["dist_norm"] = df["dist_norm"].fillna(fill_norm_if_missing)
    df["pressure_norm"] = df["pressure_norm"].fillna(fill_norm_if_missing)

    return df
