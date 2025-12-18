import pickle
import pandas as pd


frequency_lookup = {
    "b1" : 1561.098e6,
    "b2a" : 1176.45e6,
    "b2b" : 1207.14e6,
    "e1" : 1575.42e6,
    "e5" : 1191.795e6,
    "e5a" : 1176.45e6,
    "e5b" : 1207.14e6,
    "g1" : 1602e6,
    "g2" : 1246e6,
    "l1" : 1575.42e6,
    "l2" : 1227.60e6,
    "l5" : 1176.45e6
}

upper_l_bank = {
    "b1" : True,
    "b2a" : False,
    "b2b" : False,
    "e1" : True,
    "e5" : False,
    "e5a" : False,
    "e5b" : False,
    "g1" : True,
    "g2" : False,
    "l1" : True,
    "l2" : False,
    "l5" : False
}



def iono_free_lc(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the ionosphere-free linear combination of the pseudoranges
    :param data: pd.DataFrame
    :return: pd.DataFrame
    """
    # Calculate the ionosphere-free linear combination
    data['iono_free'] = 1.0 * data['C1'] - 1.0 * data['P2']

    return data


def filter_upper_l_band(df: pd.DataFrame) -> pd.DataFrame:
    """Filter df for upper L band frequencies"""
    return df[df['signal_type'].apply(lambda x: upper_l_bank[x])]

