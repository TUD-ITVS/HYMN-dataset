

# HYMN dataset

[![DOI](https://zenodo.org/badge/1115026300.svg)](https://doi.org/10.5281/zenodo.17979434)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)
![Python 3.8-<3.13](https://img.shields.io/badge/python-3.8--%3C3.13-blue.svg)

---

## Description
The HYMN dataset is a comprehensive collection of wireless positioning measurements gathered using multiple technologies, including WiFi, Bluetooth Low Energy (BLE), Ultra-Wideband (UWB), GNSS, and 5G NR. 
The dataset is designed to facilitate research and development in the field of indoor and outdoor positioning systems.
## Repository Structure
* [`/data`](data): Contains the dataset files.
  * [`/data/processed`](data/processed): Processed positioning measurements. See [Processed Data README](data/processed/README.md) for format details and data dictionary.
  * [`/data/reference`](data/reference): Reference information for anchors, points, and timing. See [Reference Data README](data/reference/README.md) for coordinate systems and rationale.
* [`/preprocessing`](preprocessing): Contains scripts and tools used for data preprocessing. See [Preprocessing README](preprocessing/README.md) for details.
* [`/examples`](examples): Example script demonstrating how to iterate over the dataset. See [Example Usage README](examples/README.md) for details.

## Installation & usage
1. Clone the repository:
   ```bash
   git clone https://github.com/TUD-ITVS/HYMN-dataset 
2. Optional: Create a virtual python environment using venv. Note that you will need to use python 3.9.-3.12. if you want to use the preprocessing scripts, as gnss_lib_py does not support newer versions yet. You may check compatibility [here](https://pypi.org/project/gnss-lib-py/).

    Windows (assuming python 3.12): 
    ```bash
    py -3.12 -m venv venv
    venv\Scripts\activate
    ```
    Mac/Linux (assuming python 3.12):
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate 

3. Explore the dataset using the example script:
    ```bash
   pip install -r examples/requirements.txt
   python examples/example_iterator.py
     
4. Optional: Run the preprocessing script
    ```bash
   pip install -r preprocessing/requirements.txt
   python -m preprocessing.preprocessing_pipeline


## Questions and issues
Please raise an issue on the GitHub Issue tracker for any questions or problems you encounter.
For other inquiries, please visit our [Organization Page](https://tu-dresden.de/bu/verkehr/vis/itvs) or contact the corresponding author as listed in the associated IEEE Data Description paper.

## Citation
 Will be added once the paper is published.
 
## License

This project is dual-licensed:
- The **source code** (including the preprocessing scripts) is licensed under the [MIT License](LICENSE-CODE).
- The **dataset** is licensed under the [Creative Commons Attribution 4.0 International (CC-BY 4.0) License](LICENSE-DATA).