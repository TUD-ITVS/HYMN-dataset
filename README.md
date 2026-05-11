# HYMN dataset

[![DOI](https://zenodo.org/badge/1115026300.svg)](https://doi.org/10.5281/zenodo.17979434)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)
![Python 3.11-<3.13](https://img.shields.io/badge/python-3.11--%3C3.13-blue.svg)

---

## Description
The HYMN dataset is a comprehensive collection of wireless positioning measurements gathered using multiple technologies, including WiFi, Bluetooth Low Energy (BLE), Ultra-Wideband (UWB), GNSS, and 5G NR. 
The dataset is designed to facilitate research and development in the field of indoor-outdoor positioning systems.

A data description paper detailing the dataset collection, structure, and potential applications has been published in IEEE Data Descriptions.
The paper can be found [here](https://doi.org/10.1109/IEEEDATA.2026.3691044).

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
      ```
2. Optional: Create a virtual Python environment using `venv`.

    Windows (assuming python 3.12): 
    ```bash
    py -3.12 -m venv venv
    venv\Scripts\activate
    ```
    Mac/Linux (assuming python 3.12):
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate    
   ```

3. Explore the dataset using the example scripts.

   Poetry (recommended):
   ```bash
   poetry -C examples install
   python examples/example_iterator.py
   ```

   pip (backward compatibility, generated from `examples/poetry.lock`):
   ```bash
   python -m pip install -r examples/requirements.txt
   python examples/example_iterator.py
   ```

4. Optional: Run the preprocessing pipeline.

   Poetry (recommended):
   ```bash
   poetry -C preprocessing install
   poetry -C preprocessing run python -m preprocessing.preprocessing_pipeline
   ```

   pip (backward compatibility, generated from `preprocessing/poetry.lock`):
   ```bash
   python -m pip install -r preprocessing/requirements.txt
   python -m preprocessing.preprocessing_pipeline
   ```

   Supported Python versions for `examples/` and `preprocessing/`: `>=3.11,<3.13`.

## Questions and issues
Please raise an issue on the GitHub Issue tracker for any questions or problems you encounter.
For other inquiries, please visit our [Organization Page](https://tu-dresden.de/bu/verkehr/vis/itvs) or contact the corresponding author as listed in the associated IEEE Data Description paper.

## Citation
Please cite the following paper if you use the dataset:

```M. Ammad, A. Michler, P. Schwarzbach, J. Ninnemann, H. Ußler and O. Michler, "Descriptor: A Hybrid Indoor and Indoor-Outdoor Positioning Multi-Technology Dataset (HYMN)," in IEEE Data Descriptions, doi: 10.1109/IEEEDATA.2026.3691044. keywords: {HYMN dataset;Radio localization dataset;signals of opportunity;seamless positioning;Ultra-Wideband (UWB);Bluetooth Low Energy (BLE);WiFi;5G New Radio (NR);GNSS}, ```
 
You can find the paper on [IEEE Xplore](https://doi.org/10.1109/IEEEDATA.2026.3691044) (open access) or on [arXiv](https://arxiv.org/abs/2604.20349) as preprint.

You can use the following BibTeX entry:
````bibtex
@ARTICLE{11512962,
  author={Ammad, Muhammad and Michler, Albrecht and Schwarzbach, Paul and Ninnemann, Jonas and Ußler, Hagen and Michler, Oliver},
  journal={IEEE Data Descriptions}, 
  title={Descriptor: A Hybrid Indoor and Indoor-Outdoor Positioning Multi-Technology Dataset (HYMN)}, 
  year={2026},
  volume={},
  number={},
  pages={1-9},
  keywords={HYMN dataset;Radio localization dataset;signals of opportunity;seamless positioning;Ultra-Wideband (UWB);Bluetooth Low Energy (BLE);WiFi;5G New Radio (NR);GNSS},
  doi={10.1109/IEEEDATA.2026.3691044}}

````

## License

This project is dual-licensed:
- The **source code** (including the preprocessing scripts) is licensed under the [MIT License](LICENSE-CODE).
- The **dataset** is licensed under the [Creative Commons Attribution 4.0 International (CC-BY 4.0) License](LICENSE-DATA).