import pandas as pd
import math
import numpy as np
from preprocessing.src.utils import add_point_ground_truth, save_df

AP_COLUMNS = ['AP1', 'AP2', 'AP3', 'AP4', 'AP5', 'AP6']
FINAL_COLUMNS = ['point_id', 'ts', 'anchor_ids', 'ranges', 'X_LOCAL_WIFI', 'Y_LOCAL_WIFI', 'Z_LOCAL_WIFI']

AP_MAPPING = {'AP1': 'WIFI_01',
              'AP2': 'WIFI_02',
              'AP3': 'WIFI_03',
              'AP4': 'WIFI_04',
              'AP5': 'WIFI_05',
              'AP6': 'WIFI_06'}


def preprocess_wifi(input_file: str = 'data/raw/wifi/ranges_combined.csv') -> None:
    """
    Preprocess WiFi data by loading, transforming, and saving it in a standardized format.

    Args:
        input_file: Path to the input CSV file containing WiFi range data
        output_dir: Directory where the processed data will be saved
    """

    # Load and rename timestamp column
    df = pd.read_csv(input_file)
    df.rename(columns={'Unix_Timestamp': 'ts'}, inplace=True)

    # Add ground truth information
    df = add_point_ground_truth(df)

    # Remove duplicate measurements
    df.drop_duplicates(AP_COLUMNS, inplace=True)

    # Convert individual AP columns to lists and handle infinity values
    df['ranges'] = df[AP_COLUMNS].values.tolist()
    df['ranges'] = df['ranges'].apply(lambda row: [r if r != math.inf else np.nan for r in row])
    df['anchor_ids'] = [AP_COLUMNS] * len(df)

    # Remove the individual AP columns as they're now in the ranges list
    df.drop(AP_COLUMNS, inplace=True, axis=1)

    # Rename smartphone ref column to ref for consistency with other datasets
    df.rename(columns={'smartphone': 'ref'}, inplace=True)

    # Sort by timestamp
    df.sort_values(by='ts', inplace=True)

    # Select and order final columns
    df = df[FINAL_COLUMNS]

    df['anchor_ids'] = df['anchor_ids'].apply(lambda ids: [AP_MAPPING.get(id, id) for id in ids])

    # Save the processed data
    save_df(df, "wifi")


if __name__ == '__main__':
    preprocess_wifi()
