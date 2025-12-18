# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 16:50:10 2025

@author: M.Ammad
"""

import numpy as np
import georinex as gr
import gnss_lib_py as glp
import pandas as pd


def get_iono_parameters(rinex_path: str):
    nav_file = gr.load(rinex_path)
    return nav_file.ionospheric_corr_GPS


# MIT License
#
# Copyright (c) 2022 Stanford NAV Lab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# The following functions are adapted from the gnss_lib_py project
# (https://github.com/Stanford-NavLab/gnss_lib_py)
# Original file: utils/gnss_models.py
# License: MIT License
def calculate_iono_delay(gps_millis, iono_params, rx_ecef,
                          sv_pos, constellation="gps"):
    """Calculate the ionospheric delay in pseudorange using the Klobuchar
    model Section 5.3.2 [1]_.

    Parameters
    ----------
    gps_millis : int
        Time at which measurements are needed, measured in milliseconds
        since start of GPS epoch [ms].
    iono_params : np.ndarray
        Ionospheric atmospheric delay parameters for Klobuchar model,
        passed in 2x4 array, use None if not available.
    rx_ecef : np.ndarray
        3x1 receiver position in ECEF frame of reference [m], use None
        if not available.
    ephem : gnss_lib_py.navdata.navdata.NavData
        Satellite ephemeris parameters for measurement SVs, use None if
        using satellite positions instead.
    sv_posvel : gnss_lib_py.navdata.navdata.NavData
        Precomputed positions of satellites corresponding to the input
        `gps_millis`, set to None if not available.
    constellation : string
        Constellation used for the ionospheric parameters addition.

    Returns
    -------
    iono_delay : np.ndarray
        Estimated delay caused by the ionosphere [m].

    Notes
    -----
    Based on code written by J. Makela.
    AE 456, Global Navigation Sat Systems, University of Illinois
    Urbana-Champaign. Fall 2017

    References
    ----------
    ..  [1] Misra, P. and Enge, P,
        "Global Positioning System: Signals, Measurements, and Performance."
        2nd Edition, Ganga-Jamuna Press, 2006.

    """
    _, gps_tow = glp.gps_millis_to_tow(gps_millis)

    #Reshape receiver position to 3x1
    rx_ecef = np.reshape(rx_ecef, [3,1])

    # Determine the satellite locations
    sv_pos = sv_pos.reshape(3, -1)
    el_az = glp.ecef_to_el_az(rx_ecef, sv_pos)
    el_r = np.deg2rad(el_az[0, :])
    az_r = np.deg2rad(el_az[1, :])

    # Calculate the WGS-84 latitude/longitude of the receiver
    wgs_llh = glp.ecef_to_geodetic(rx_ecef)
    lat_r = np.deg2rad(wgs_llh[0, :])
    lon_r = np.deg2rad(wgs_llh[1, :])

    # Parse the ionospheric parameters
    alpha = iono_params[constellation][0,:]
    beta = iono_params[constellation][1,:]

    # Calculate the psi angle
    psi = 0.1356/(el_r+0.346) - 0.0691

    # Calculate the ionospheric geodetic latitude
    lat_i = lat_r + psi * np.cos(az_r)

    # Make sure values are in bounds
    ind = np.argwhere(np.abs(lat_i) > 1.3090)
    if len(ind) > 0:
        lat_i[ind] = 1.3090 * np.sign(lat_i[ind])  # pragma: no cover
    # Calculate the ionospheric geodetic longitude
    lon_i = lon_r + psi * np.sin(az_r)/np.cos(lat_i)

    # Calculate the solar time corresponding to the gps_tow
    solar_time = 1.3751e4 * lon_i + gps_tow

    # Make sure values are in bounds
    solar_time = np.mod(solar_time,86400)

    # Calculate the geomagnetic latitude (semi-circles)
    lat_m = (lat_i + 2.02e-1 * np.cos(lon_i - 5.08))/np.pi
    # Calculate the period
    period = beta[0]+beta[1]*lat_m+beta[2]*lat_m**2+beta[3]*lat_m**3

    # Make sure values are in bounds
    ind = np.argwhere(period < 72000).flatten()
    if len(ind) > 0:
        period[ind] = 72000  # pragma: no cover

    # Calculate the local time angle
    theta = 2*np.pi*(solar_time - 50400) / period

    # Calculate the amplitude term
    amp = (alpha[0]+alpha[1]*lat_m+alpha[2]*lat_m**2+alpha[3]*lat_m**3)

    # Make sure values are in bounds
    ind = np.argwhere(amp < 0).flatten()
    if len(ind) > 0:
        amp[ind] = 0  # pragma: no cover

    # Calculate the slant factor
    slant_fact = 1.0 + 5.16e-1 * (1.6755-el_r)**3

    # Calculate the ionospheric delay
    iono_delay = slant_fact * 5.0e-9
    ind = np.argwhere(np.abs(theta) < np.pi/2.).flatten()
    if len(ind) > 0:
        iono_delay[ind] = slant_fact[ind]* \
            (5e-9+amp[ind]*(1-theta[ind]**2/2.+theta[ind]**4/24.))

    # Convert ionospheric delay to equivalent meters
    iono_delay = glp.consts.C*iono_delay
    return iono_delay

def calculate_tropo_delay(gps_millis, rx_ecef, sv_pos):
    """Calculate tropospheric delay
    
    Parameters
    ----------
    gps_millis : int
        Time at which measurements are needed, measured in milliseconds
        since start of GPS epoch [ms].
    rx_ecef : np.ndarray
        3x1 array of ECEF rx_pos position [m].
    sv_pos : gnss_lib_py.navdata.navdata.NavData
        Precomputed positions of satellites, set to None if not available.
    
    Returns
    -------
    tropo_delay : np.ndarray
        Tropospheric corrections to pseudorange measurements [m].
    
    Notes
    -----
    Based on code written by J. Makela.
    AE 456, Global Navigation Sat Systems, University of Illinois
    Urbana-Champaign. Fall 2017
    
    """
    # Make sure that receiver position is 3x1
    rx_ecef = np.reshape(rx_ecef, [3,1])

    # Reshape satellite positions to 3xN
    sv_pos = sv_pos.reshape(3, 1)
    
    # compute elevation and azimuth
    el_az = glp.ecef_to_el_az(rx_ecef, sv_pos)
    el_r  = np.deg2rad(el_az[0, :])
    
    # Calculate the WGS-84 latitude/longitude of the receiver
    rx_lla = glp.ecef_to_geodetic(rx_ecef)
    height = rx_lla[2, :]
    
    # Force height to be positive
    ind = np.argwhere(height < 0).flatten()
    if len(ind) > 0:  # pragma: no cover
        height[ind] = 0
    
    # Calculate the delay
    tr_delay_c1 = 2.47
    tr_delay_c2 = 0.0121
    tr_delay_c3 = 1.33e-4
    C = 299792458.
    
    tropo_delay = tr_delay_c1/(np.sin(el_r)+tr_delay_c2) * np.exp(-height*tr_delay_c3)/C

    # Convert tropospheric delaly in equivalent meters
    tropo_delay = C * tropo_delay
    
    return tropo_delay


def calculate_athmospheric_corrected_pseudorange(data: pd.DataFrame, rinex_nav_iono: str = 'RawData/LEIJ00DEU_R_20242970000_01D_MN.rnx',
                                                 ):
    """Calculate the ionospheric and tropospheric errors in the GNSS ephemeris.

    Parameters
    ----------
    data : pd.DataFrame
        GNSS ephemeris containing the satellite positions and pseudoranges.

    Returns
    -------
    ephemeris : pd.DataFrame
        GNSS ephemeris with corrected pseudoranges.

    """

    rinex_nav = glp.RinexNav(rinex_nav_iono)
    if "gps" not in rinex_nav.iono_params.keys():
        iono_params = rinex_nav.iono_params[list(rinex_nav.iono_params.keys())[0]]
    else:
        iono_params = rinex_nav.iono_params
    rx_coord_global = np.array([51.5710, 13.0034, 0]).reshape(-1, 1)
    rx_ecef = glp.geodetic_to_ecef(rx_coord_global)
    rx_ecef = rx_ecef.ravel()
    # add column for corrected ranges with empty list
    data['corr_pr_m'] = np.empty((len(data), 0)).tolist()
    for idx, row in data.iterrows():
        iono = np.array([calculate_iono_delay(row['gps_millis'], iono_params, rx_ecef, np.array(s))
                         for s in zip(np.array(row['x_sv_m']),
                                               np.array(row['y_sv_m']),
                                               np.array(row['z_sv_m']))])
        tropo = np.array([calculate_tropo_delay(row['gps_millis'], rx_ecef, np.array(s))
                          for s in zip(np.array(row['x_sv_m']),
                                       np.array(row['y_sv_m']),
                                       np.array(row['z_sv_m']))])
        corr_pr = np.reshape(np.array(row['raw_pr_m']), (-1, 1)) - iono - tropo
        corr_pr = [x[0] for x in corr_pr]
        data.at[idx, 'corr_pr_m'] = corr_pr
    return data

