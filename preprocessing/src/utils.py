import pandas as pd

point_mapping = {
    "101": "A13B6",
    "103": "A11B6",
    "105": "A09B6",
    "108": "A06B6",
    "110": "A04B6",
    "112": "A02B6",
    "113": "A01B6",
    "202": "A12B5",
    "204": "A10B5",
    "206": "A08B5",
    "207": "A07B5",
    "209": "A05B5",
    "211": "A03B5",
    "213": "A01B5",
    "301": "A13B4",
    "303": "A11B4",
    "305": "A09B4",
    "308": "A06B4",
    "310": "A04B4",
    "312": "A02B4",
    "313": "A01B4",
    "402": "A12B3",
    "404": "A10B3",
    "406": "A08B3",
    "407": "A07B3",
    "409": "A05B3",
    "411": "A03B3",
    "413": "A01B3",
    "501": "A13B2",
    "503": "A11B2",
    "505": "A09B2",
    "508": "A06B2",
    "510": "A04B2",
    "512": "A02B2",
    "513": "A01B2",
    "602": "A12B1",
    "604": "A10B1",
    "606": "A08B1",
    "607": "A07B1",
    "609": "A05B1",
    "611": "A03B1",
    "613": "A01B1",
    "T01": "T01",
    "T02": "T02",
    "T03": "T03",
    "T04": "T04",
    "T05": "T05",
    "T06": "T06"
}

def rename_points(df, point_column_name='point_id') -> pd.DataFrame:
    """
    Rename points in the DataFrame based on a predefined mapping.

    :param df: DataFrame containing a column with point identifiers.
    :param point_column_name: Name of the column containing point identifiers.
    :return: DataFrame with renamed points.
    """
    if point_column_name in df.columns:
        df[point_column_name] = df[point_column_name].replace(point_mapping)
        # remove points that are not in the mapping
        points_to_drop = set(df[point_column_name]) - set(point_mapping.values())
        if points_to_drop:
            print(f"Dropping points not in mapping: {points_to_drop}")
        # Filter the DataFrame to keep only rows with points in the mapping
        df = df[df[point_column_name].isin(point_mapping.values())]
    else:
        raise ValueError(f"Column '{point_column_name}' not found in DataFrame.")

    return df

def add_point_ground_truth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds point-based ground truth information to the given DataFrame.

    This function processes the input DataFrame by mapping timestamps to point IDs
    and associating the data with ground truth information. The column "mess_id"
    is renamed to "point_id" for uniformity, and additional modifications are
    applied by renaming points as needed. The resulting DataFrame is returned
    with the applied transformations.

    :param df: The input DataFrame that contains timestamp-based data
    :return: DataFrame with added point-based ground truth information
    """
    df = get_pointid_from_timestamp(df)
    df = get_ground_truth(df)
    #df = rename_points(df)
    return df

def get_ground_truth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Merges the input dataframe with the ground truth dataset and sorts the resulting
    dataframe by the timestamp column.

    :param df: A pandas DataFrame containing the input data to be processed.
    :type df: pd.DataFrame
    :return: A pandas DataFrame resulting from the merge and sort operations with
        the ground truth dataset.
    :rtype: pd.DataFrame
    """
    ground_truth = pd.read_pickle("data/reference/pickle/point_coordinates.pkl")
    df = df.merge(ground_truth, on="point_id", how="outer")
    df.sort_values(by="ts", inplace=True)
    return df

def get_pointid_from_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assigns measurement IDs and sequential indices to a DataFrame based on timestamp mappings
    stored in the time keeping file. It calculates local time by adjusting the timestamp in
    milliseconds, then matches the timestamps within a specific time window to assign
    corresponding IDs and indices.

    :param df: A pandas DataFrame containing a column "ts" with timestamps in
        milliseconds.
    :type df: pd.DataFrame
    :return: A pandas DataFrame updated with columns "point" for the measurement ID. Original rows outside any
        defined time window are removed.
    :rtype: pd.DataFrame
    """
    measurement_time = pd.read_pickle("data/reference/pickle/time_reference.pkl")
    df["local_time"] = pd.to_datetime(df["ts"].astype(float), unit="ms") + pd.Timedelta(hours=2)
    for idx, row in measurement_time.iterrows():
        # Determine which rows fall into the current time window
        in_window = (df["local_time"] >= row["start_time_local"]) & (
                df["local_time"] <= row["end_time_local"]
        )
        df.loc[in_window, "point_id"] = row["point"]

    df.drop(columns=["local_time"], inplace=True)
    df.dropna(subset=["point_id"], inplace=True)
    return df

def save_df(df: pd.DataFrame, system_str: str) -> None:
    df.to_csv(f"data/processed/csv/{system_str}.csv", index=False, encoding="utf-8")
    df.to_pickle(f"data/processed/pickle/{system_str}.pkl")
    df.to_parquet(f"data/processed/parquet/{system_str}.parquet")
