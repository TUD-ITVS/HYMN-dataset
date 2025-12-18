

# HYMN dataset

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

---

## Description
The HYMN dataset is a comprehensive collection of wireless positioning measurements gathered using multiple technologies, including WiFi, Bluetooth Low Energy (BLE), Ultra-Wideband (UWB), GNSS, and 5G NR. 
The dataset is designed to facilitate research and development in the field of indoor and outdoor positioning systems.
## Repository Structure
* `/data`: Contains the processed dataset files.
* `/preprocessing`: Contains scripts and tools used for data preprocessing.
* `/examples`: Example script demonstrating how to iterate over the dataset.

## Installation & usage
1. Clone the repository:
   ```bash
   git clone https://github.com/TUD-ITVS/HYMN-dataset 

2. Install dependencies
    ```bash
   pip install -r requirements.txt
   
3. Explore the dataset using the example script:
    ```bash
   python examples/explore_dataset.py
     
4. Optional: Run the preprocessing script
    ```bash
   pip install -r preprocessing/requirements.txt
    python -m preprocessing.main


## Questions and issues
Please raise an issue on the GitHub Issue tracker for any questions or problems you encounter.
For other inquiries, please visit our [Organization Page](https://tu-dresden.de/bu/verkehr/vis/itvs) or contact the corresponding author as listed in the associated IEEE Data Description paper.

## Citation
 tbd
 
## License

This project is dual-licensed:
- The **source code** (including the preprocessing scripts) is licensed under the [MIT License](LICENSE-CODE.txt).
- The **dataset** is licensed under the [Creative Commons Attribution 4.0 International (CC-BY 4.0) License](LICENSE-DATA.txt).