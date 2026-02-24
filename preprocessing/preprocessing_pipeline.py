import concurrent.futures
import subprocess
import sys

from preprocessing.src.merge_data import data_merge

preprocessing_modules = {
    "wifi": "preprocessing.src.preprocess_wifi",
    "ble": "preprocessing.src.preprocess_ble",
    "uwb": "preprocessing.src.preprocess_uwb",
    "gnss": "preprocessing.src.preprocess_gnss",
    "nr5g": "preprocessing.src.preprocess_nr5g",
}

preprocessed_data_paths = {
    'wifi': 'data/processed/pickle/wifi.pkl',
    'ble': 'data/processed/pickle/ble.pkl',
    'uwb': 'data/processed/pickle/uwb.pkl',
    'gnss': 'data/processed/pickle/gnss.pkl',
    'nr5g': 'data/processed/pickle/nr5g.pkl'
}


def run_module(module_name: str) -> tuple[str, str, str, int]:
    python_path = sys.executable
    result = subprocess.run(
        [python_path, "-m", module_name],
        capture_output=True,
        text=True,
    )
    return module_name, result.stdout, result.stderr, result.returncode


def run_preprocessing_scripts(systems: list[str]) -> None:
    """
    Runs preprocessing scripts provided in the list concurrently.
    Only scripts that exist in the `preprocessing_script_paths` are executed.

    :param scripts: List of scripts to be executed. Each script should correspond to
        an entry in the `preprocessing_script_paths` dictionary.
    :type scripts: list[str]
    :return: None
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(run_module, preprocessing_modules[system])
            for system in systems
            if system in preprocessing_modules
        ]
        for future in concurrent.futures.as_completed(futures):
            module_name, stdout, stderr, rc = future.result()
            if rc != 0:
                print(f"Errors in {module_name}:")
                if stdout:
                    print(stdout)
                if stderr:
                    print(stderr)
            else:
                print(f"{module_name} finished successfully.\n")


def run_preprocessing_pipeline() -> None:
    """
    Execute the entire preprocessing pipeline for multiple systems.

    This function initializes a list of systems and executes preprocessing
    scripts for these systems. It then merges the preprocessed data paths
    related to the systems.

    :return: None
    """
    systems = ['wifi', 'ble', 'uwb', 'gnss', 'nr5g']
    run_preprocessing_scripts(systems)
    data_merge(systems, preprocessed_data_paths)

if __name__ == '__main__':
    run_preprocessing_pipeline()
