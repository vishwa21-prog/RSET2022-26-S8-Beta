# backend/eligibility.py
import pandas as pd
from eligibility_screening_only import main as run_eligibility

def process_uploaded_csv(input_csv_path):
    """
    Takes uploaded CSV path,
    runs eligibility screening,
    returns output CSV path
    """
    # Temporarily override input/output
    import eligibility_screening_only as es

    es.DATA_CSV = input_csv_path
    es.OUTPUT_CSV = "backend/outputs/eligible_patients_with_id.csv"

    es.main()

    return es.OUTPUT_CSV