# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 15:18:34 2024

@author: M.Ammad
"""


import pandas as pd
import os
from datetime import datetime
from datetime import timezone
import re

class ReadDataset:
    def __init__(self, path):
        self.path = path
        self.df = pd.DataFrame()

    def load_data(self, ip, filename = False):
        files5G = [
            os.path.join(path, file)
            for path, _, files in os.walk(self.path)
            for file in files if file.endswith('.csv')
        ]

        for index, file5G in enumerate(files5G):
                            
            logData = pd.read_csv(file5G)
            logData['TIME'] = logData.apply(
                lambda row: datetime.fromisoformat(row['TIME'][:-1] + '+00:00').astimezone(timezone.utc), axis=1
            )
            logData['TIME'] = logData.apply(
                lambda row: int(datetime.timestamp(row['TIME']) * 1000), axis=1
            )
            logData = logData[logData['IP Address'] == ip]
            logData.drop(['IP Address', 'RNTI'], inplace=True, axis=1)
            
            logData.rename(columns={'TIME': 'ts'}, inplace=True)
            logData['anchor_ids'] = [['RU1', 'RU2', 'RU3']] * len(logData)
            logData['SNR'] = logData[['SNR RU1', 'SNR RU2', 'SNR RU3']].values.tolist()
            logData.drop(['SNR RU1', 'SNR RU2', 'SNR RU3'], inplace=True, axis=1)
            
            # Adding file_id to make the format of both the 5th Nov and 23rd october the same
            fileID = file5G.split('\\')[-1].split('_ue')[0]
            logData['file_id'] = len(logData) * [fileID]
            
            # The following lines are add for measurements taken on 5-Nov-2024
            if filename:
                fileID = file5G.split('\\')[-1].split('_ue')[0]
                
                # Assigning mess_id here because we don't have messung_time for 5th Nov
                # Mess ID pattern (Consecutive 3 digits)
                pattern = r"(?<!\d)\d{3}(?!\d)"
                messID = re.findall(pattern, fileID)[0]
                logData['file_id'] = len(logData) * [fileID]
                logData['mess_id'] = len(logData) * [messID]
                

            self.df = pd.concat([self.df, logData])

        return self.df