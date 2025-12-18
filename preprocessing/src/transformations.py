# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 15:45:29 2024

@author: M.Ammad
"""

import pandas as pd

class CoordinateTransformer:
    def __init__(self, ecke5g, displacement_x, displacement_y):
        self.ecke5g = ecke5g
        self.origin = (ecke5g[0] + displacement_x, ecke5g[1] + displacement_y)

    def calculate_transformation(self, df, offset = True):
        if 'mess_id' not in df.columns:
            df['mess_id'] = df['point_id']
        deltaX, deltaY = self.origin
        if offset == False:
            coordinates = df.dropna().drop_duplicates(['mess_id', 'tachymeter_xyz'])
            mess_5g = [(row['mess_id'], row['tachymeter_xyz']) for _, row in coordinates.iterrows()]
            
        else:
            coordinates = df.dropna().drop_duplicates(['mess_id', '5g-antenne'])
            mess_5g = [(row['mess_id'], row['5g-antenne']) for _, row in coordinates.iterrows()]
        
        translatedCoords = []
        
        # Iterate through all the measurement coordinates (offset corrected)
        for mess_id, coords in mess_5g:
            if isinstance(coords, tuple):
                # x = -x + deltaX,          y = -y + deltaY
                translated = (round(deltaX - coords[0], 4), round(deltaY - coords[1], 4))
                translatedCoords.append((mess_id, translated))

        translatedDf = pd.DataFrame(translatedCoords, columns=['mess_id', 'local_xy'])
        
        # Add the translated coordinates column to the original dataframe 
        translatedDf = df.merge(translatedDf, on='mess_id')
        
        # # Export the ground truth as CSV and pickle
        # gt5G = translatedDf[['mess_id', 'tachymeter_xyz', 'local_xy']]
        # gt5G.to_csv('groundTruth.csv', index = False)
        # gt5G.to_pickle('groundTruth.pkl')
        
        return translatedDf