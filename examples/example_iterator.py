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
        folder: Union[str, Path] = "data",
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


if __name__ == "__main__":
    ds = Dataset(folder="data", systems=["wifi", "gnss", "ble", "uwb", "nr5g"], backend="parquet", use_tqdm=True)
    print(f"Dataset length: {len(ds)}")

    for i, item in enumerate(ds):
        print(f"Item {i}: {item}")
        if i >= 10:
            break