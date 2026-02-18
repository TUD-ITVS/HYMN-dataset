"""
NR5G Data Preprocessing Module

This module handles the preprocessing of NR5G data from raw format to standardized format.
Naming scheme:
    MRK = Local 5G coordinates, processed by proprietary software provided by MRK company
    LOCAL = Local coordinates, as defined in the paper
"""

import numpy as np
import pandas as pd
from preprocessing.src.nr5g.loadData import ReadDataset
from preprocessing.src.utils import add_point_ground_truth, save_df


FINAL_COLUMNS = ["point_id", "ts", "anchor_ids", "pos", "SNR", "X_LOCAL_NR5G", "Y_LOCAL_NR5G", "Z_LOCAL_NR5G"]



# Rotation matrix in x-y-plane
A_XY_LOCAL_TO_MRK = np.array(
    [
        [-1.000094040184, 0.003027006984],
        [-0.002137889009, -1.000154061449],
    ],
    dtype=float,
)

# Translation vector in x-y-plane
B_XY_LOCAL_TO_MRK = np.array([4.353538911053, 36.997794200742], dtype=float)

# Mean z offset (MRK_Z - LOCAL_Z). It is assumed x-y planes are aligned.
DZ_LOCAL_TO_MRK = -1.0566666666666666

# Inverse XY mapping
A_XY_MRK_TO_LOCAL = np.linalg.inv(A_XY_LOCAL_TO_MRK)
B_XY_MRK_TO_LOCAL = -A_XY_MRK_TO_LOCAL @ B_XY_LOCAL_TO_MRK
DZ_MRK_TO_LOCAL = -DZ_LOCAL_TO_MRK


def local_to_mrk(xyz_local: np.ndarray) -> np.ndarray:
    """Transform LOCAL (X,Y,Z) to MRK (X,Y,Z) using 2D affine + z-offset.

    Accepts shape (3,), (N, 3).
    Returns same shape.
    """
    x = np.asarray(xyz_local, dtype=float)

    if x.shape == (3,):
        xy_mrk = A_XY_LOCAL_TO_MRK @ x[:2] + B_XY_LOCAL_TO_MRK
        z_mrk = x[2] + DZ_LOCAL_TO_MRK
        xy_mrk = np.round(xy_mrk, 3)
        z_mrk = np.round(z_mrk, 3)
        return np.array([xy_mrk[0], xy_mrk[1], z_mrk], dtype=float)

    if x.ndim == 2 and x.shape[1] == 3:
        xy_mrk = (x[:, :2] @ A_XY_LOCAL_TO_MRK.T) + B_XY_LOCAL_TO_MRK
        z_mrk = x[:, 2] + DZ_LOCAL_TO_MRK
        xy_mrk = np.round(xy_mrk, 3)
        z_mrk = np.round(z_mrk, 3)
        return np.column_stack([xy_mrk, z_mrk])

    raise ValueError(f"xyz_local must have shape (3,) or (N, 3), got {x.shape}")


def mrk_to_local(xyz_mrk: np.ndarray) -> np.ndarray:
    """Transform MRK (X,Y,Z) to LOCAL (X,Y,Z) using inverse 2D affine + z-offset."""
    x = np.asarray(xyz_mrk, dtype=float)

    if x.shape == (3,):
        xy_local = A_XY_MRK_TO_LOCAL @ x[:2] + B_XY_MRK_TO_LOCAL
        z_local = x[2] + DZ_MRK_TO_LOCAL
        xy_local = np.round(xy_local, 3)
        z_local = np.round(z_local, 3)
        return np.array([xy_local[0], xy_local[1], z_local], dtype=float)

    if x.ndim == 2 and x.shape[1] == 3:
        xy_local = (x[:, :2] @ A_XY_MRK_TO_LOCAL.T) + B_XY_MRK_TO_LOCAL
        z_local = x[:, 2] + DZ_MRK_TO_LOCAL
        xy_local = np.round(xy_local, 3)
        z_local = np.round(z_local, 3)
        return np.column_stack([xy_local, z_local])

    raise ValueError(f"xyz_mrk must have shape (3,) or (N, 3), got {x.shape}")

def add_local_columns_from_mrk(
    df: pd.DataFrame,
    *,
    x_col: str = "X_MRK",
    y_col: str = "Y_MRK",
    out_col: str = "pos",
) -> pd.DataFrame:
    """Return a copy with a LOCAL 2D position column computed from MRK X/Y.

    This is a lightweight helper for cases where we only need 2D coordinates.

    Args:
        df: Input dataframe.
        x_col: Column name containing the MRK X coordinate.
        y_col: Column name containing the MRK Y coordinate.
        out_col: Output column name that will contain `[X_LOCAL, Y_LOCAL]` per row.

    Returns:
        Copy of `df` with `out_col` added as a list `[x, y]` for each row.
    """
    required = {x_col, y_col}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing columns: {sorted(missing)}")

    xy_mrk = df[[x_col, y_col]].to_numpy(dtype=float)
    # Convert 2D via the 2D inverse affine mapping.
    xy_local = (xy_mrk @ A_XY_MRK_TO_LOCAL.T) + B_XY_MRK_TO_LOCAL
    xy_local = np.round(xy_local, 3)

    out = df.copy()
    out[out_col] = xy_local.tolist()
    return out


def preprocess_nr5g(
        input_dir: str = 'data/raw/nr5g',
        output_dir: str = 'data/',
        ip_address: str = '10.45.2.1',
) -> None:
    """
    Preprocess NR5G data from raw files to a standardized format.

    Args:
        input_dir: Directory containing raw NR5G data files
        output_dir: Directory where processed data will be saved
        ip_address: IP address to filter the data
    """
    # Load and preprocess the data
    dataset = ReadDataset(input_dir)
    df = dataset.load_data(ip_address)

    df = add_local_columns_from_mrk(df, x_col="X", y_col="Y", out_col="pos")
    df = add_point_ground_truth(df)


    # Final data formatting
    df.rename(columns={"5g-antenne": "ref"}, inplace=True)
    # `pos` is already created above in a vectorized way.

    # Sort by timestamp
    df.sort_values(by='ts', inplace=True)

    # Select final columns and save
    final_df = df[FINAL_COLUMNS]
    save_df(final_df, "nr5g")


if __name__ == "__main__":
    preprocess_nr5g()
