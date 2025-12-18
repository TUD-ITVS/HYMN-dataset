# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 10:54:41 2024

@author: M.Ammad
"""

import gnss_lib_py as glp
import pandas as pd
import os
import numpy as np
from gnss.calculateErrors import calculate_athmospheric_corrected_pseudorange
from gnss.GNSS_Formatting import reformat_final
import pickle

import warnings

from utils import rename_points, save_df

def load_rinex(file: str) -> glp.RinexObs:
    """
    Loads a RINEX observation file using gnss_lib_py.

    Parameters:
    file (str): Path to the RINEX observation file.

    Returns:
    glp.RinexObs: Loaded RINEX observation data.
    """
    if not os.path.exists(file):
        raise FileNotFoundError(f"The file {file} does not exist.")
    if file.endswith('.pkl'):
        with open(file, 'rb') as f:
            rinex_obs = pickle.load(f)
        print("RINEX data loaded successfully from pickle file.")
    else:
        rinex_obs = glp.RinexObs(file)
        pickle.dump(rinex_obs, open('preprocessing/raw_data/gnss/preprocessed_rinex.pkl', 'wb'))
        print("RINEX data loaded successfully and saved to preprocessed_rinex.pkl")
    return rinex_obs

def read_data(rinex_obs: glp.RinexObs, dump_file_dir: str) -> pd.DataFrame:
    """
    Reads GNSS data from a RINEX file and adds satellite states.

    Parameters:
    rinex_file (str): Path to the RINEX observation file.
    nav_iono (str): Path to the navigation ionosphere file.

    Returns:
    pd.DataFrame: Processed GNSS data as a pandas DataFrame.
    """

    data = rinex_obs

    data = glp.add_sv_states(data, download_directory="preprocessing/raw_data/gnss/ephemeris/")
    data = data.pandas_df()
    data.loc[:, 'ts'] = data.apply(lambda row:
                                                     (glp.gps_millis_to_datetime(
                                                         row['gps_millis']).timestamp()) * 1000,
                                                     axis=1)
    data.to_csv(os.path.join(dump_file_dir, 'all_raw.csv'), index=False)
    return data


def get_point_ids(data: pd.DataFrame) -> pd.DataFrame:

    time_reference = pd.read_pickle('preprocessing/reference/time_reference.pkl')

    # Create a temporary timestamp datetime column to filter the dataset
    data['timestamp_temp'] = pd.to_datetime(data['ts'].astype(float),
                                                    unit='ms') + pd.Timedelta(hours=2)

    # Initialize mess_id column with None
    data['mess_id'] = None

    # Assign mess_id based on the time range in time_reference
    for idx, row in time_reference.iterrows():
        # Assign mess_id to rows in trajData where timestamp is within the range
        timestampRange = (data['timestamp_temp'] >= row['startTime']) & (data['timestamp_temp'] <= row['endTime'])
        data.loc[timestampRange, 'mess_id'] = row['mess_id']


    # Drop the temporary timestamp datetime column
    data = data.drop(columns=['timestamp_temp'])
    data.dropna(inplace = True)
    data.reset_index(drop = True, inplace = True)
    return data



# =============================================================================
# # Getting the gnss-antenne xyz location based on Tachymeter data
# =============================================================================
def get_ground_truth(data: pd.DataFrame) -> pd.DataFrame:
    """
    Merges the trajectory data with ground truth data.

    Parameters:
    trajData (pd.DataFrame): Trajectory data DataFrame.

    Returns:
    pd.DataFrame: Merged DataFrame with ground truth data.
    """

    groundTruth = pd.read_pickle('preprocessing/reference/ground_truth.pkl')
    groundTruth = groundTruth[['mess_id', 'gnss-antenne', 'XYZ_gnss']]


    data = data.merge(groundTruth, on ='mess_id', how ='outer')
    data = data.sort_values(by ='ts')
    return data

def generate_final_output(data: pd.DataFrame, nav_iono: str, output_dir: str) -> None:
    """
    Defines the final output columns for the trajectory data.

    Parameters:
    trajData (pd.DataFrame): Trajectory data DataFrame.

    Returns:
    pd.DataFrame: DataFrame with only the final output columns.
    """


     # Reformatting the GNSS Data
    data = reformat_final(data)

    # Calculating the Atmospheric Errors
    data = calculate_athmospheric_corrected_pseudorange(data, nav_iono)

    # Reorder columns to match the final output format
    final_columns = ['point_id', 'ts', 'gnss_sv_id', 'observation_code', 'raw_pr_m', 'corr_pr_m',
                     'carrier_phase', 'raw_doppler_hz', 'cn0_dbhz',
                     'x_sv_m', 'y_sv_m', 'z_sv_m', 'vx_sv_mps', 'vy_sv_mps', 'vz_sv_mps',
                     'b_sv_m', 'b_dot_sv_mps',
                     'ref', 'ref_ecef']

    data = data[final_columns]

    data = rename_points(data, point_column_name='point_id')

    # Convert all columns to native Python types
    for col in data.columns:
        # if elements are lists, check the type of their elements. If np.str_ convert to str
        if data[col].dtype == 'object':
            data[col] = data[col].apply(lambda x: [str(i) if isinstance(i, np.str_) else i for i in x] if isinstance(x, list) else x)

    save_df(data, "gnss")



def preprocess_gnss(raw_dir: str = 'preprocessing/raw_data/gnss/', processed_dir: str = 'data/') -> None:
    # Trajectory GNSS File
    rinexFile = os.path.join(raw_dir, 'all.24O')
    pickledFile = os.path.join(raw_dir + 'preprocessed_rinex.pkl')
    nav_iono = os.path.join(raw_dir, 'LEIJ00DEU_R_20242970000_01D_MN.rnx')

    # Warning wrapper until xarray usage in gnss_lib_py is fixed upstream
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=FutureWarning,
            #message=".*use_new_combine_kwarg_defaults.*",
        )
        # try to load pickled observation file, otherwise load the RINEX file and parse using glp
        try:
            rinex_obs = load_rinex(pickledFile)
        except FileNotFoundError:
            rinex_obs = load_rinex(rinexFile)
        gnss_data = read_data(rinex_obs, dump_file_dir=raw_dir)
        gnss_data = get_point_ids(gnss_data)
        gnss_data = get_ground_truth(gnss_data)
        generate_final_output(gnss_data, nav_iono, output_dir=processed_dir)

if __name__ == '__main__':
    preprocess_gnss()
