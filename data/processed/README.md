# Processed Data

This directory contains the processed positioning measurements from the HYMN dataset. The data is available in three different formats and categorized by technology.

## Format Overview

The processed data is provided in the following formats:

- CSV (.csv): Human-readable comma-separated values. Ideal for quick inspection and compatibility with a wide range of tools.
- Parquet (.parquet): A columnar storage format that provides efficient data compression and encoding. Recommended for large-scale data analysis with tools like Pandas, Dask, or Spark.
- Pickle (.pkl): Serialized Python objects. Preserves Python-specific data types (like NumPy arrays) and is the fastest for loading directly into Python environments.

## Data Dictionary

The following table describes the common and technology-specific columns found in the processed files.

| Column Name | Units | Description                                                                                                                                             |
| --- | --- |---------------------------------------------------------------------------------------------------------------------------------------------------------|
| point_id | - | Unique identifier for the measurement location. Coordinates can be found in reference file.                                                             |
| ts | ms | Unix timestamp in milliseconds.                                                                                                                         |
| anchor_ids | - | List of identifiers for the anchors (e.g., BLE beacons, WiFi APs, UWB anchors, or NR5G RUs) involved in the measurement. Present for BLE/WiFi/UWB/NR5G. |
| ranges | m | List of measured distances to the anchors corresponding to `anchor_ids`. Present for BLE/WiFi/UWB.                                                      |
| pos | m | Estimated local position `(x, y)` as a tuple, specific to NR5G.                                                                                         |
| SNR | dB | Signal-to-noise ratio per NR5G RU, specific to NR5G.                                                                                                    |
| X_LOCAL_[TECH] | m | Ground-truth X-coordinate in the local reference frame for the given technology (e.g., X_LOCAL_BLE).                                                    |
| Y_LOCAL_[TECH] | m | Ground-truth Y-coordinate in the local reference frame for the given technology.                                                                        |
| Z_LOCAL_[TECH] | m | Ground-truth Z-coordinate in the local reference frame for the given technology.                                                                        |
                                          

### GNSS specifics

GNSS data (`gnss.csv`) differs from the other technologies. Each row represents a single epoch but contains lists of observations from all visible satellites. Many columns therefore store arrays, where each entry corresponds to one satellite in `gnss_sv_id`.

Additional GNSS-specific columns:

| Column Name | Units | Description |
| --- | --- | --- |
| gnss_sv_id | - | List of Satellite Vehicle IDs (e.g., Gxx, Exx, Cxx, Rxx). |
| observation_code | - | Signal tracking code (e.g., 1C, 7Q, 5Q). |
| raw_pr_m | m | Raw pseudorange measurements per satellite. |
| corr_pr_m | m | Corrected pseudorange measurements per satellite. |
| carrier_phase | cycles | Carrier phase measurements per satellite. |
| raw_doppler_hz | Hz | Raw Doppler frequency per satellite. |
| cn0_dbhz | dB-Hz | Carrier-to-noise density ratio per satellite. |
| x_sv_m, y_sv_m, z_sv_m | m | Satellite ECEF position at transmit time. |
| vx_sv_mps, vy_sv_mps, vz_sv_mps | m/s | Satellite ECEF velocity at transmit time. |
| b_sv_m | m | Satellite clock bias. |
| b_dot_sv_mps | m/s | Satellite clock drift. |
| X_ECEF_GNSS | m | Ground-truth X-coordinate in ECEF.                                                                                                 |
| Y_ECEF_GNSS | m | Ground-truth Y-coordinate in ECEF.                                                                                                 |
| Z_ECEF_GNSS | m | Ground-truth Z-coordinate in ECEF.                                                                                                 |

## Synchronized Merged File

The `merged.csv` file (and its Parquet/Pickle counterparts) provides a synchronized view of all technologies. Its primary purpose is to act as a central index for multi-modal analysis.

**Rationale:**
Instead of duplicating the full data from each technology, the merged file contains only:
- `ts`: The common Unix timestamp used for synchronization.
- `idx_[tech]`: The row index of the corresponding measurement in the respective technology-specific file (e.g., `idx_ble`, `idx_wifi`).

This allows users to easily align data from different sensors by using these indices to look up the detailed measurements in the individual technology files.

## Files in this directory

- csv/ble.csv, csv/wifi.csv, csv/uwb.csv, csv/nr5g.csv, csv/gnss.csv, csv/merged.csv
- parquet/*.parquet: Same content as CSV counterparts in Parquet format.
- pickle/*.pkl: Same content as CSV counterparts in Python pickle format.
