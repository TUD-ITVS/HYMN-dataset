# Data preprocessing
This folder contains the preprocessing scripts for the data.

## Installation
python -m pip install -r preprocessing/requirements.txt        
python -m pip install -e preprocessing        

## Preprocessing Pipeline

### Overview
The preprocessing pipeline transforms raw measurement data from multiple wireless positioning technologies into a unified, structured dataset suitable for analysis and modeling. The pipeline processes five different wireless technologies: WiFi, Bluetooth Low Energy (BLE), Ultra-Wideband (UWB), GNSS, and 5G NR.

### Pipeline Architecture
The preprocessing follows a modular approach with dedicated preprocessing scripts for each technology. Data is then merged into one unified dataset using a common timestamp.

1. **Individual Technology Preprocessing** - Each wireless technology is processed independently
2. **Data Merging** - All preprocessed datasets are combined based on timestamps


### Technology-Specific Processing

#### GNSS Preprocessing
- **Purpose**: Process GNSS RINEX observation files and associated navigation data
- **Key Operations**:
    - Parse RINEX observation files using specialized GNSS processing libraries
    - Calculate satellite positions, pseudoranges, and clock corrections
    - Associate measurements with ground truth positions
    - Generate final formatted output with satellite IDs, positions, and timing data
- 

#### BLE/UWB/WiFi/5G NR Preprocessing
- **Purpose**: Process ranging measurements from respective technologies
- **Key Operations**:
    - Extract technology-specific measurements (ranges, RSSI, signal parameters)
    - Apply timestamp synchronization and duplicate removal
    - Associate measurements with reference positions

### Data Integration and Quality Assurance

#### Point mapping
During the original measurement campaign, an existing point scheme was used. In order to facilitate structured data
evaluation, the point scheme was mapped to a new point scheme using _A_ and _B_ axis. Additional points which are in the
transition area between indoor and outdoor environment were added and labeled using the scheme _T_.

#### Timestamp Synchronization
All measurements are synchronized using timestamps. The association of each measurement to a specific point was done using the logged time
intervals.

Points 202 and 310 have been repeatedly measured due to malfunction in the first measurement run. The sets 202_2 and
310_2 are valid, while the sets 202 and 310 are left for evaluation, but removed from the merged set.

#### Ground Truth Association
Each measurement is associated with known reference positions to enable supervised learning and performance evaluation of positioning algorithms.

#### Data Validation
- Remove invalid or corrupted measurements
- Ensure consistent data structures across technologies
- Filter measurements that don't meet minimum quality criteria

### Output Format
The pipeline generates multiple output formats:
- **Pickle files** (.pkl) for Python-native processing
- **CSV files** for general analysis tools
- **Parquet files** for efficient storage and data processing

### Parallel Processing
The pipeline uses concurrent execution to process multiple technologies simultaneously, reducing overall preprocessing time while maintaining data integrity.