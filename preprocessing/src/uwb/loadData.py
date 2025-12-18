# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 14:51:08 2024

@author: M.Ammad
"""

import pandas as pd
import sqlite3
import json
import glob
import numpy as np

class ReadDataset:
    def __init__(self, path):
        self.path = path

    def load_data(self):
        zigposFiles = glob.glob(self.path, recursive=True)
        df = pd.DataFrame()

        for index, zigposFile in enumerate(zigposFiles):
            with sqlite3.connect(zigposFile) as con:
                logData = pd.read_sql_query("SELECT * FROM LOG", con)
                logData['MESSAGE'] = logData.apply(lambda row: json.loads(row['MESSAGE'].decode('utf-8')), axis=1)
                
                tempDf = pd.DataFrame({
                    'ts': logData.apply(lambda row: row['MESSAGE'][0]['timestamp'], axis=1),
                    'anchor_ids': logData.apply(lambda row: [hex(int(item['addressB']))[-2:].upper() for item in row['MESSAGE']], axis=1),
                    'tag_id': logData.apply(lambda row: row['MESSAGE'][0]['addressA'], axis=1),
                    'ranges': logData.apply(lambda row: [item['value'] for item in row['MESSAGE']], axis=1),
                })

                tempDf['ranges'] = tempDf['ranges'].apply(lambda row: [r if r > 0.0 else np.nan for r in row])
                tempDf['ts'] = tempDf['ts'].apply(lambda x: int(x))
                df = pd.concat([df, tempDf])

        df.reset_index(drop=True, inplace=True)
        return df
