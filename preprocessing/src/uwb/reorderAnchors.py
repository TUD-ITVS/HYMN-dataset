# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 14:52:58 2024

@author: M.Ammad
"""

class AnchorReorderer:
    anchor_ids_order = ['9A', 'AB', '97', '98', '94', '89', '92', '9B', '95', '9C']

    def __init__(self, df):
        self.df = df

    @classmethod
    def reorder_anchors(cls, anchor_ids, ranges):
        """
        Reorders anchor_ids and ranges based on the predefined anchor_ids_order.
        
        Parameters:
        - anchor_ids: List of anchor IDs.
        - ranges: List of ranges associated with the anchor IDs.
        
        Returns:
        - Tuple (newAnchors, newRanges): Reordered anchor IDs and corresponding ranges.
        """
        anchorDict = dict(zip(anchor_ids, ranges))
        
        # Reordering based on anchor_ids_order
        newAnchors = [item for item in cls.anchor_ids_order if item in anchorDict]
        newRanges = [anchorDict[item] for item in newAnchors]
        
        return newAnchors, newRanges

    def reorder(self):
        """
        Reorders the anchor_ids and ranges in the DataFrame based on the specified order.
        
        Returns:
        - DataFrame: Updated DataFrame with reordered anchor_ids and ranges columns.
        """
        self.df[['anchor_ids', 'ranges']] = self.df.apply(
            lambda row: self.reorder_anchors(row['anchor_ids'], row['ranges']),
            axis=1, result_type='expand'
        )
        return self.df
