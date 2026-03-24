# backend/drug_matching.py

import os
from copy import deepcopy
import drug_matcher as dm


def process_uploaded_drug_csv(input_csv_path):
    """
    Takes uploaded CSV path,
    runs drug matching,
    returns output Excel path
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Set config path relative to backend
    config_path = os.path.join(BASE_DIR, "config", "drug_config.json")

    # Load config + params
    config = dm.load_config(config_path)
    params = deepcopy(dm.DEFAULT_PARAMS)

    # Run logic
    results = dm.run_from_csv(input_csv_path, config, params)

    # Output file path (like eligibility)
    output_path = os.path.join(
        BASE_DIR,
        "outputs",
        "drug_matching_results.xlsx"
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    dm.save_results_to_excel(results, output_path)

    return output_path