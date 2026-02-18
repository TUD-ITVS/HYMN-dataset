import os
import pandas as pd
from typing import Optional

from preprocessing.src.uwb.loadData import ReadDataset
from preprocessing.src.uwb.reorderAnchors import AnchorReorderer
from preprocessing.src.utils import add_point_ground_truth, save_df

# Constants
DEFAULT_INPUT_DIR = 'data/raw/uwb'
DEFAULT_OUTPUT_DIR = 'data'
DEFAULT_TAG_ID = '8121069331292423818' # Name: "Zigpos links"
REQUIRED_COLUMNS = ["point_id", "ts", "anchor_ids", "ranges", "X_LOCAL_UWB", "Y_LOCAL_UWB", "Z_LOCAL_UWB"]

anchor_mapping = {
    "AB": "UWB_06",
    "9A": "UWB_07",
    "97": "UWB_01",
    "94": "UWB_05",
    "89": "UWB_02",
    "92": "UWB_04",
    "9C": "UWB_09",
    "95": "UWB_03",
    "9B": "UWB_08",
    "98": "UWB_10"}

def preprocess_uwb(
        input_dir: str = DEFAULT_INPUT_DIR,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        tag_id: Optional[str] = DEFAULT_TAG_ID
) -> None:
    """
    Preprocess UWB data by loading, cleaning, and transforming it for analysis.

    Args:
        input_dir: Directory containing the raw UWB data files
        output_dir: Directory where processed data will be saved
        tag_id: Specific tag ID to filter the data for; if None, all tags are included
    """
    # Find all SQLite files in the input directory
    sqlite_glob = os.path.join(input_dir, '**', '*.sqlite')

    # Load data
    data_reader = ReadDataset(path=sqlite_glob)
    df = data_reader.load_data()


    # Process data
    df = add_point_ground_truth(df)

    # Filter out rows where all range values are NaN
    df = df[df['ranges'].apply(lambda x: not all(pd.isna(x)))]

    # Reorder anchors
    anchor_reorderer = AnchorReorderer(df)
    df = anchor_reorderer.reorder()

    # Filter by tag_id if specified
    if tag_id:
        df = df[df["tag_id"] == tag_id]

    # Sort by timestamp
    df = df.sort_values(by='ts')

    df = df.rename(columns={"X_LOCAL_UWB2": "X_LOCAL_UWB", "Y_LOCAL_UWB2": "Y_LOCAL_UWB", "Z_LOCAL_UWB2": "Z_LOCAL_UWB"})

    # Select only required columns
    df = df[REQUIRED_COLUMNS]


    # Replace anchor_ids based on anchor_mapping
    df['anchor_ids'] = df['anchor_ids'].apply(lambda ids: [anchor_mapping.get(id, id) for id in ids])

    save_df(df, "uwb")


if __name__ == "__main__":
    preprocess_uwb()