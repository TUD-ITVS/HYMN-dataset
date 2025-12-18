# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 13:00:55 2025

@author: M.Ammad
"""

import pandas as pd

rename_dict = {
    'mess_id': 'point_id',
    'XYZ_gnss': 'ref_ecef',
    'gnss-antenne': 'ref',
    'Messung': 'measurement',
    'gps_millis': 'gps_millis',
}

def reformat_final(data: pd.DataFrame) -> pd.DataFrame:
    columns_to_drop = ['signal_type']
    # Rename columns
    data = data.rename(columns=rename_dict)
    # merge timestamp into one row per timestamp
    data = data.drop(columns=columns_to_drop, errors='ignore')
    data = data.groupby('ts').agg(lambda x: list(x)).reset_index()
    # Use first value for all values in rename_dict
    for col in rename_dict.values():
        if col in data.columns:
            data[col] = data[col].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0
            else None)
    return data


def reformat(data):
    
    timestamps = data['timestamp(ms)'].unique()
    
    satPos = []
    svIDs = []
    pranges = []
    sat_clk = []
    antenna_xyz = []
    ecef_xyz = []

    for timestamp in timestamps:
        filteredData = data[data['timestamp(ms)'] == timestamp]
    
        svIDs.append(filteredData['gnss_sv_id'].values.tolist())
        
        satPos.append(filteredData['sat_xyz'].values.tolist())
        
        
        pranges.append(filteredData['raw_pr_m'].values.tolist())
        
        sat_clk.append(filteredData['b_sv_m'].values.tolist())

        antenna_xyz.append(filteredData['gnss-antenne'].iloc[0])

        ecef_xyz.append(filteredData['XYZ_gnss'].iloc[0])


        
    # Create a new formatted DataFrame
    gnssData = pd.DataFrame({
        'timestamp(ms)': timestamps,
        'sv_ids': svIDs,
        'sat_xyz': satPos,
        'PRanges_m': pranges,
        'sat_clk': sat_clk,
        'gnss-antenne': antenna_xyz,
        'XYZ_gnss': ecef_xyz
    })
    
    id_timestamps = data.drop_duplicates(['mess_id','timestamp(ms)'])
    gnssData = id_timestamps[['timestamp(ms)', 'mess_id']].merge(gnssData, on = 'timestamp(ms)')
    
    columns = ['mess_id', 'timestamp(ms)', 'sv_ids', 'sat_xyz', 'PRanges_m', 'sat_clk', 'gnss-antenne', 'XYZ_gnss']
    
    gnssData = gnssData[columns]
    
    return gnssData