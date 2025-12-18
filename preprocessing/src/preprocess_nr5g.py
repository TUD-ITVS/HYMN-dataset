"""
NR5G Data Preprocessing Module

This module handles the preprocessing of NR5G data from raw format to standardized format.
"""

from preprocessing.src.nr5g.loadData import ReadDataset
from preprocessing.src.transformations import CoordinateTransformer
from preprocessing.src.utils import add_point_ground_truth, save_df

# Constants for coordinate transformation
COORDINATES_5G = (4.418, 35.978)
DISPLACEMENT_X = 0.60
DISPLACEMENT_Y = 1.10
OUTPUT_FILENAME = "nr5g"
FINAL_COLUMNS = ["point_id", "ts", "anchor_ids", "pos", "SNR", "ref"]


def preprocess_nr5g(
        input_dir: str = 'preprocessing/raw_data/nr5g',
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
    df = add_point_ground_truth(df)

    # Transform coordinates
    transformer = CoordinateTransformer(
        ecke5g=COORDINATES_5G,
        displacement_x=DISPLACEMENT_X,
        displacement_y=DISPLACEMENT_Y
    )
    transformed_df = transformer.calculate_transformation(df)

    # Final data formatting
    transformed_df.rename(columns={"5g-antenne": "ref"}, inplace=True)
    transformed_df['pos'] = transformed_df.apply(
        lambda row: (row['X'], row['Y']), axis=1
    )

    # Sort by timestamp
    transformed_df.sort_values(by='ts', inplace=True)

    # Select final columns and save
    final_df = transformed_df[FINAL_COLUMNS]
    save_df(final_df, "nr5g")


if __name__ == "__main__":
    preprocess_nr5g()
