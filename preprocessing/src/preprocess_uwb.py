import os
import pandas as pd
from typing import Optional

from preprocessing.src.uwb.loadData import ReadDataset
from preprocessing.src.uwb.reorderAnchors import AnchorReorderer
from preprocessing.src.utils import add_point_ground_truth, save_df

# Constants
DEFAULT_INPUT_DIR = 'preprocessing/raw_data/uwb'
DEFAULT_OUTPUT_DIR = 'data'
DEFAULT_TAG_ID = '8121069331292423818'
REQUIRED_COLUMNS = ["point_id", "ts", "anchor_ids", "ranges", "ref"]


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

    # Rename columns for consistency
    df.rename(columns={"zigpos-links": "ref"}, inplace=True)

    # Filter by tag_id if specified
    if tag_id:
        df = df[df["tag_id"] == tag_id]

    # Sort by timestamp
    df = df.sort_values(by='ts')

    # Select only required columns
    df = df[REQUIRED_COLUMNS]

    save_df(df, "uwb")


if __name__ == "__main__":
    preprocess_uwb()