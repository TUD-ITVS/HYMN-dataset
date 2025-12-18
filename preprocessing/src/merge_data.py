# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 13:35:18 2025

@author: M.Ammad
"""
import pandas as pd



def minimal_df(df: pd.DataFrame, system_name: str) -> pd.DataFrame:
    """Return minimal view with ts, point_id, system, and index in original df.
    - Resets the index to ensure a clean 0..N-1 index per df used as sys_idx.
    - Adds a 'system' column with the system_name.
    """
    df = df.reset_index(drop=True).copy()
    df['sys_idx'] = df.index
    df['system'] = system_name
    return df[['ts', 'point_id', 'system', 'sys_idx']]


def data_merge(systems: list, systems_paths: dict[str, str]) -> None:
    """
    Build a lookup DataFrame with columns: ts, point_id, and per-system index columns.
    - Creates columns: idx_ble, idx_gnss, idx_uwb, idx_nr5g, idx_wifi (for the systems provided).
    - Each column contains the index (int) or list of indices (if multiple rows exist) in that system's df
      for the given (ts, point_id). Only systems provided in `systems` are considered.
    - Saves the resulting DataFrame to csv/pickle/parquet.
    """
    # Load and build minimal views for requested systems
    minimals = []
    for sys in systems:
        if sys not in systems_paths:
            raise KeyError(f"System '{sys}' not found in systems_paths")
        df = pd.read_pickle(systems_paths[sys])
        minimals.append(minimal_df(df, sys))

    # Determine target per-system column names based on requested systems
    idx_cols = [f"idx_{s}" for s in systems]

    if not minimals:
        # Nothing to merge
        merged_df = pd.DataFrame(columns=['ts', 'point_id'] + idx_cols)
    else:
        # Concatenate and aggregate per (ts, point_id, system)
        cat = pd.concat(minimals, ignore_index=True)

        # Aggregate indices per system; turn singleton list into int, keep list otherwise
        def agg_indices(g: pd.DataFrame):
            vals = g['sys_idx'].tolist()
            return int(vals[0]) if len(vals) == 1 else [int(v) for v in vals]

        grouped = (
            cat.groupby(['ts', 'point_id', 'system'], as_index=False)
               .apply(lambda g: pd.Series({'idx': agg_indices(g)}), include_groups=False)
        )

        # Pivot to wide format: columns per system
        pivoted = grouped.pivot_table(
            index=['ts', 'point_id'],
            columns='system',
            values='idx',
            aggfunc='first'
        ).reset_index()

        # Rename pivoted system columns to idx_<system>
        for s in systems:
            if s in pivoted.columns:
                pivoted.rename(columns={s: f"idx_{s}"}, inplace=True)

        # Ensure all required idx columns exist even if missing in data
        for col in idx_cols:
            if col not in pivoted.columns:
                pivoted[col] = None

        # Order columns: ts, point_id, idx_* in the order of systems
        merged_df = pivoted[['ts', 'point_id'] + idx_cols]

    # Format the idx columns as integers for CSV export
    export_df = merged_df.copy()

    idx_cols = [f"idx_{s}" for s in systems]
    for col in idx_cols:
        # Convert only non-NaN values to integers
        export_df[col] = export_df[col].apply(
            lambda x: f"{int(x)}" if pd.notna(x) and not isinstance(x, list) else x
        )

    export_df.to_csv(f"data/csv/merged.csv", index=False)
    merged_df.to_pickle(f"data/pickle/merged.pkl")
    merged_df.to_parquet(f"data/parquet/merged.parquet")


if __name__ == '__main__':
    systems_to_process = ['wifi', 'ble', 'uwb', 'gnss', 'nr5g']
    preprocessing_data_paths = {
        'wifi': 'data/pickle/wifi.pkl',
        'ble': 'data/pickle/ble.pkl',
        'uwb': 'data/pickle/uwb.pkl',
        'gnss': 'data/pickle/gnss.pkl',
        'nr5g': 'data/pickle/nr5g.pkl'
    }
    data_merge(systems_to_process, preprocessing_data_paths)
