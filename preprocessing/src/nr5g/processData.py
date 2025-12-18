# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 15:30:42 2024

@author: M.Ammad
"""

import pandas as pd

class DataProcessor:
    def __init__(self, df, messungTimePath='preprocessing/reference/time_reference.pkl'):
        self.df = df
        self.messungTime = pd.read_pickle(messungTimePath)
        
    def process_timestamps(self):
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp(ms)'].astype(float), unit='ms') + pd.Timedelta(hours=2)
    
    def assign_measurement_ids(self):
        self.df['mess_id'] = None
        self.df['Messung'] = None
        for idx, row in self.messungTime.iterrows():
            timestampRange = (self.df['timestamp'] >= row['startTime']) & (self.df['timestamp'] <= row['endTime'])
            self.df.loc[timestampRange, 'mess_id'] = row['mess_id']
            self.df.loc[timestampRange, 'Messung'] = idx + 1

    def clean_data(self):
        self.df.drop(columns=['timestamp'], inplace=True)
        self.df.dropna(inplace=True)
        self.df.reset_index(drop=True, inplace=True)

    def get_processed_data(self):
        return self.df
