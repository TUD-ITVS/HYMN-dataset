import glob
import json
import os
import numpy as np
import pandas as pd
from preprocessing.src.utils import add_point_ground_truth, save_df

# Constants
REQUIRED_RANGE_LENGTH = 5
INVALID_RANGE_VALUE = 0.0
TIMESTAMP_MULTIPLIER = 1000

def load_json_logs(file_path):
    """Load and parse JSON logs from a file, filtering for entries with 'message'."""
    with open(file_path, "r") as fh:
        return [json.loads(line) for line in fh if "message" in line]

def create_dataframe_from_logs(logs):
    """Convert JSON logs to a pandas DataFrame with proper data transformation."""
    if len(logs) <= 2:
        return None

    temp_df = pd.DataFrame()
    temp_df["ts"] = [int(row["time"] * TIMESTAMP_MULTIPLIER) for row in logs]
    temp_df["ts_pc"] = [[int(x * TIMESTAMP_MULTIPLIER) for x in row["timestamp_pc"]] for row in logs]
    temp_df["anchor_ids"] = [row["anchor_ids"] for row in logs]
    temp_df["tag_ids"] = [row["tag_id"] for row in logs]
    temp_df["ranges"] = [row["ranges"] for row in logs]

    # Replace invalid ranges (0.0) with NaN
    temp_df["ranges"] = temp_df["ranges"].apply(
        lambda arr: [r if r != INVALID_RANGE_VALUE else np.nan for r in arr]
    )

    return temp_df

def filter_and_clean_dataframe(df):
    """Apply filtering and cleaning operations to the DataFrame."""
    # Add ground truth information
    df = add_point_ground_truth(df)

    # Remove duplicate timestamps
    df.drop_duplicates(subset=["ts"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Keep only readings with the required number of range entries
    df = df[df["ranges"].apply(lambda arr: len(arr) == REQUIRED_RANGE_LENGTH)]

    # Rename columns and select the relevant ones
    df.rename(columns={"metirionic": "ref"}, inplace=True)
    df = df[["point_id", "ts", "anchor_ids", "ranges", "ref"]].copy()

    return df

def preprocess_ble(input_dir: str = 'preprocessing/raw_data/ble/', output_dir: str = 'data/') -> None:
    """
    Preprocess BLE data from JSON files into a structured DataFrame.

    Args:
        input_dir: Directory containing the raw BLE data files
        output_dir: Directory where processed data will be saved

    """
    df = pd.DataFrame()

    # Recursively find and process all JSON files in input_dir
    pattern = os.path.join(input_dir, '**', '*.json')
    for file in glob.glob(pattern, recursive=True):
        logs = load_json_logs(file)
        temp_df = create_dataframe_from_logs(logs)
        if temp_df is not None:
            df = pd.concat([df, temp_df])

    df.reset_index(drop=True, inplace=True)
    df = filter_and_clean_dataframe(df)

    # Sort by timestamp
    df.sort_values(by="ts", inplace=True)

    # Save the processed data
    save_df(df, "ble")


if __name__ == "__main__":
    preprocess_ble()
