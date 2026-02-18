import pandas as pd
from pathlib import Path
from typing import Iterator, Optional, Union, Dict, Any


class Dataset:
    """
    Iterable dataset that uses the merged index file to reference per-technology data.

    - Supports backends: 'pickle', 'csv', 'parquet'
    - Exposes per-item dictionaries that include ts, point_id and each requested system's row(s) as pandas objects.

    Directory layout (relative to folder):
      folder/
        csv/merged.csv
        parquet/merged.parquet
        pickle/merged.pkl
        <backend>/wifi.* , ble.* , uwb.* , gnss.* , nr5g.*  (optional but supported for convenience)
        Or: data for systems may also be found specifically under folder/pickle/<sys>.pkl as per preprocessing.

    Each item produced by iteration is a dict with keys:
      - 'ts': timestamp from merged
      - 'point_id': point id from merged
      - For each system in `systems`: one of
          * pandas.Series for a single-row match
          * pandas.DataFrame for multiple rows match (if merged idx column holds list of indices)
          * None if there is no match for that system in this (ts, point_id)
    """

    SUPPORTED_BACKENDS = {"pickle", "csv", "parquet"}

    def __init__(
        self,
        folder: Union[str, Path] = "data/processed/",
        systems: list[str] = ["wifi", "gnss", "ble", "uwb", "nr5g"],
        backend: str = "parquet",
        use_tqdm: bool = False,
    ) -> None:
        self.folder = Path(folder)
        self.systems = list(systems)
        self.backend = backend.lower()
        self.use_tqdm = use_tqdm

        if self.backend not in self.SUPPORTED_BACKENDS:
            raise ValueError(f"Unsupported backend '{backend}'. Choose from {sorted(self.SUPPORTED_BACKENDS)}")

        # Resolve merged file path based on backend
        self.paths = {
            "csv": self.folder / "csv" / "merged.csv",
            "parquet": self.folder / "parquet" / "merged.parquet",
            "pickle": self.folder / "pickle" / "merged.pkl",
        }
        self.merged_path = self.paths[self.backend]
        if not self.merged_path.exists():
            raise FileNotFoundError(f"Merged file not found: {self.merged_path}")

        # Load merged index into DataFrame
        if self.backend == "csv":
            self.merged = pd.read_csv(self.merged_path)
        elif self.backend == "parquet":
            self.merged = pd.read_parquet(self.merged_path)
        else:  # pickle
            self.merged = pd.read_pickle(self.merged_path)

        # Normalize column names and ensure index columns exist for requested systems
        # Expected columns: ts, point_id, idx_<system>
        for s in self.systems:
            col = f"idx_{s}"
            if col not in self.merged.columns:
                # If missing, create with None to simplify access
                self.merged[col] = None

        # Lazy-loaded per-system full DataFrames (always read from pickle which is the canonical store per merge_data.py)
        self._system_cache: Dict[str, Optional[pd.DataFrame]] = {s: None for s in self.systems}

    def _system_file_path(self, system: str) -> Path:
        """Prefer canonical pickle path data/pickle/<system>.pkl. Fallback to current backend folder if present."""
        # canonical
        pkl = self.folder / "pickle" / f"{system}.pkl"
        if pkl.exists():
            return pkl
        # fallback to backend-specific files named <system>.<ext>
        if self.backend == "csv":
            path = self.folder / "csv" / f"{system}.csv"
        elif self.backend == "parquet":
            path = self.folder / "parquet" / f"{system}.parquet"
        else:
            path = self.folder / "pickle" / f"{system}.pkl"
        return path

    def _load_system_df(self, system: str) -> pd.DataFrame:
        df = self._system_cache.get(system)
        if df is not None:
            return df
        path = self._system_file_path(system)
        if not path.exists():
            # If not found, keep an empty DataFrame for graceful handling
            self._system_cache[system] = pd.DataFrame()
            return self._system_cache[system]
        if path.suffix == ".pkl" or path.suffix == ".pickle":
            df = pd.read_pickle(path)
        elif path.suffix == ".csv":
            df = pd.read_csv(path)
        elif path.suffix == ".parquet":
            df = pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported file type for system '{system}': {path.suffix}")
        # Ensure a clean 0..N-1 index so the saved indices map correctly
        df = df.reset_index(drop=True)
        self._system_cache[system] = df
        return df

    def __len__(self) -> int:
        return len(self.merged)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        row = self.merged.iloc[idx]
        item: Dict[str, Any] = {"ts": row.get("ts"), "point_id": row.get("point_id")}
        for s in self.systems:
            col = f"idx_{s}"
            sys_idx = row.get(col)
            df = self._load_system_df(s)
            if df.empty or pd.isna(sys_idx):
                item[s] = None
            elif isinstance(sys_idx, list):
                # Multiple matches: return a DataFrame slice
                # Ensure indices are ints
                indices = [int(i) for i in sys_idx]
                item[s] = df.iloc[indices].copy()
            else:
                # Single match: return a Series (single row)
                try:
                    i = int(sys_idx)
                    item[s] = df.iloc[i].copy()
                except Exception:
                    item[s] = None
        return item

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        iterator = range(len(self))
        if self.use_tqdm:
            try:
                from tqdm import tqdm  # type: ignore
                iterator = tqdm(iterator, total=len(self))
            except Exception:
                # If tqdm unavailable, silently fall back
                pass
        for i in iterator:
            yield self[i]


def example_calculate_wifi_ranging_error(measurement: Dict[str, Any]):
    """
    Exemplary function to illustrate the usage of the Dataset iterator. Calculates the WiFi ranging error based on
    the provided measurement and reference position data.

    This function processes a WiFi measurement dictionary containing information about anchor IDs, ranges, and
    timestamps. It calculates the error between the measured distances and the true distances obtained from
    predefined reference points and anchor coordinates. The result is a DataFrame containing the measured range,
    true range, and their error for each anchor ID.

    Args:
        measurement (Dict[str, Any]): A dictionary containing WiFi measurement data. Must include:
            - "wifi": A pandas DataFrame or Series with WiFi data for anchor IDs and ranges.
            - "point_id": A unique identifier for a reference point.

    Returns:
        pandas.DataFrame: A DataFrame containing the following columns:
            - "ts": Timestamp of the measurement.
            - "point_id": The reference point identifier.
            - "anchor_id": The identifier of the WiFi anchor.
            - "measured_range": The measured distance to the anchor.
            - "true_range": The true distance to the anchor from the reference point.
            - "error": The difference between measured and true distances.
    """

    wifi_obj = measurement.get("wifi")
    point_id = measurement.get("point_id")

    if wifi_obj is None or point_id is None:
        raise ValueError("Measurement must contain 'wifi' and 'point_id'")

    # Normalize to DataFrame
    if isinstance(wifi_obj, pd.Series):
        wifi_df = wifi_obj.to_frame().T
    elif isinstance(wifi_obj, pd.DataFrame):
        wifi_df = wifi_obj
    else:
        raise NotImplementedError(f"Unsupported wifi object type: {type(wifi_obj)}")

    base = Path(__file__).resolve().parents[1]
    ref_anchor_path = base / "data" / "reference" / "pickle" / "anchor_coordinates.pkl"
    ref_point_path = base / "data" / "reference" / "pickle" / "point_coordinates.pkl"

    anchors = pd.read_pickle(ref_anchor_path)
    points = pd.read_pickle(ref_point_path)

    # --- Reference position of the WiFi device for this point_id
    p = points.loc[points["point_id"].astype(str) == str(point_id)]
    if p.empty:
        raise ValueError(f"No point found for point_id '{point_id}'")

    # Point reference for WiFi
    x_col, y_col, z_col = "X_LOCAL_WIFI", "Y_LOCAL_WIFI", "Z_LOCAL_WIFI"

    p0 = p.iloc[0]
    ref = pd.to_numeric(pd.Series([p0.get(x_col), p0.get(y_col), p0.get(z_col)]), errors="coerce").to_numpy(dtype=float)
    if pd.isna(ref).any():
        raise ValueError(f"Missing reference position for point_id '{point_id}'")

    # --- Anchor positions (WiFi)
    if "point_id" not in anchors.columns:
        raise KeyError(f"anchor_coordinates is missing required column 'point_id'")

    wifi_anchors = anchors[anchors["point_id"].astype(str).str.upper().str.startswith("WIFI_")].copy()
    anchor_pos = {
        str(r["point_id"]): pd.to_numeric(pd.Series([r["X_LOCAL"], r["Y_LOCAL"], r["Z_LOCAL"]]), errors="coerce").to_numpy(dtype=float)
        for _, r in wifi_anchors.iterrows()
    }

    rows: list[dict[str, Any]] = []

    # Each wifi row has `anchor_ids` and `ranges` lists
    for _, wrow in wifi_df.iterrows():
        anchor_ids = wrow.get("anchor_ids")
        ranges = wrow.get("ranges")

        if not isinstance(anchor_ids, list) or not isinstance(ranges, list):
            continue

        ts = wrow.get("ts", measurement.get("ts"))

        for aid, meas_r in zip(anchor_ids, ranges):
            axyz = anchor_pos.get(aid)
            if axyz is None or (isinstance(meas_r, float) and pd.isna(meas_r)):
                continue

            true_r = float(((axyz - ref) ** 2).sum() ** 0.5)
            meas_r_f = float(meas_r)
            rows.append(
                {
                    "ts": ts,
                    "point_id": point_id,
                    "anchor_id": aid,
                    "measured_range": meas_r_f,
                    "true_range": true_r,
                    "error": abs(meas_r_f - true_r),
                }
            )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    ds = Dataset(folder="data/processed/", systems=["wifi", "gnss", "ble", "uwb", "nr5g"], backend="parquet", use_tqdm=True)
    print(f"Dataset length: {len(ds)}")

    for i, item in enumerate(ds):
        if item["wifi"] is not None:
            epoch_statistics = example_calculate_wifi_ranging_error(item)
            print("Epoch WiFi Ranging Error for epoch {i}:".format(i=i))
            print(epoch_statistics)
            print(" \nRanging error statistics:") 
            print(epoch_statistics["error"].describe())
        if i >= 10:
            break