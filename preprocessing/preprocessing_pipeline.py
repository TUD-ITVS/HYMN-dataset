import concurrent.futures
import os
import subprocess
import sys

from preprocessing.src.merge_data import data_merge

preprocessing_script_paths = {
    'wifi': 'preprocessing/src/preprocess_wifi.py',
    'ble': 'preprocessing/src/preprocess_ble.py',
    'uwb': 'preprocessing/src/preprocess_uwb.py',
    'gnss': 'preprocessing/src/preprocess_gnss.py',
    'nr5g': 'preprocessing/src/preprocess_nr5g.py'
}

preprocessed_data_paths = {
    'wifi': 'data/processed/pickle/wifi.pkl',
    'ble': 'data/processed/pickle/ble.pkl',
    'uwb': 'data/processed/pickle/uwb.pkl',
    'gnss': 'data/processed/pickle/gnss.pkl',
    'nr5g': 'data/processed/pickle/nr5g.pkl'
}


def run_script(script_path: str) -> tuple[str, str, str]:
    python_path = sys.executable  # Get current Python interpreter path
    result = subprocess.run([python_path, script_path],
                          capture_output=True, 
                          text=True)
    return script_path, result.stdout, result.stderr

def run_preprocessing_scripts(scripts: list[str]) -> None:
    """
    Runs preprocessing scripts provided in the list concurrently.
    Only scripts that exist in the `preprocessing_script_paths` are executed.

    :param scripts: List of scripts to be executed. Each script should correspond to
        an entry in the `preprocessing_script_paths` dictionary.
    :type scripts: list[str]
    :return: None
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(run_script, preprocessing_script_paths[script]):
                       script for script in scripts if script in preprocessing_script_paths}
        for future in concurrent.futures.as_completed(futures):
            script = futures[future]
            try:
                script, stdout, stderr = future.result()
                if stderr:
                    print(f"Errors in {script} script:")
                    print(stderr)
                else:
                    print(f"Script {script} finished successfully.\n")
            except Exception as exc:
                print(f"Script {script} generated an exception: {exc}")


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
