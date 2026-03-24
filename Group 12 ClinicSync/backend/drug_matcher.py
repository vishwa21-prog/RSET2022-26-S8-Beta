from typing import Dict, Any, Tuple, List
import json
import os
from copy import deepcopy
import pandas as pd
from datetime import datetime


# ============================================================
# DEFAULT PARAMETERS
# ============================================================

DEFAULT_PARAMS = {
    "decision_threshold": 0.60,
    "missing_egfr_safety_score": 0.75
}


# ============================================================
# CONFIG LOADER
# ============================================================

def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# CSV KEY MAP
# ============================================================

def _get_canonical_key_map() -> Dict[str, str]:
    return {
        "Patient_ID": "patient_id",
        "Age": "age",
        "BMI": "bmi",
        "Waist_Circumference": "waist",
        "Fasting_Blood_Glucose": "fbg",
        "HbA1c": "hba1c",
        "eGFR": "egfr",

        "Blood_Pressure_Systolic": "sbp",
        "Blood_Pressure_Diastolic": "dbp",

        "Cholesterol_Total": "chol_total",
        "Cholesterol_HDL": "hdl",
        "Cholesterol_LDL": "ldl",

        "GGT": "ggt",
        "Serum_Urate": "urate",
        "Dietary_Intake_Calories": "calories",

        "Family_History_of_Diabetes": "fh_diabetes",
        "Previous_Gestational_Diabetes": "gdm",

        "Sex_Female": "sex_female",
        "Sex_Male": "sex_male",

        "Physical_Activity_Level_High": "pa_high",
        "Physical_Activity_Level_Moderate": "pa_mod",
        "Physical_Activity_Level_Low": "pa_low",

        "Alcohol_Consumption_Heavy": "alc_heavy",
        "Alcohol_Consumption_Moderate": "alc_mod",
        "Alcohol_Consumption_Unknown": "alc_unknown",

        "Smoking_Status_Current": "smk_current",
        "Smoking_Status_Former": "smk_former",
        "Smoking_Status_Never": "smk_never",

        "Diabetes": "diabetes_label"
    }


# ============================================================
# PATIENT PARSER
# ============================================================

def patient_from_csv_row(row: Dict[str, Any],
                         key_map: Dict[str, str]) -> Dict[str, Any]:

    patient = {}

    bool_fields = {
        "fh_diabetes", "gdm", "sex_female", "sex_male",
        "pa_high", "pa_mod", "pa_low",
        "alc_heavy", "alc_mod", "alc_unknown",
        "smk_current", "smk_former", "smk_never"
    }

    for csv_k, canon_k in key_map.items():
        if csv_k in row and not pd.isna(row[csv_k]):
            val = row[csv_k]

            if canon_k in bool_fields:
                if isinstance(val, str):
                    patient[canon_k] = val.strip().lower() in ["1", "true", "yes"]
                else:
                    patient[canon_k] = bool(int(val))
            else:
                patient[canon_k] = val

    patient["is_diabetic"] = int(patient.get("diabetes_label", 0)) == 1
    return patient


# ============================================================
# VALIDATION
# ============================================================

def validate_patient(patient: Dict[str, Any]) -> Tuple[bool, List[str]]:
    missing = [k for k in ["age", "bmi", "hba1c"] if k not in patient]
    return len(missing) == 0, missing


# ============================================================
# DERIVED FLAGS
# ============================================================

def derive_flags(p: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "obese": p.get("bmi", 0) >= 27,
        "hypertensive": p.get("sbp", 0) >= 140 or p.get("dbp", 0) >= 90,
        "elderly": p.get("age", 0) >= 65,
        "alcohol_risk": p.get("alc_heavy", False) or p.get("ggt", 0) > 60,
        "cvd_risk": (
            (p.get("age", 0) >= 55) +
            (p.get("sbp", 0) >= 140) +
            (p.get("ldl", 0) >= 130) +
            p.get("smk_current", False)
        ) >= 2
    }


# ============================================================
# CONFIG-DRIVEN ELIGIBILITY
# ============================================================

def check_config_eligibility(patient, drug, config):

    drug_conf = config.get(drug, {})
    inclusion = drug_conf.get("inclusion", {})
    exclusion = drug_conf.get("exclusion", {})

    reasons = []

    age = patient.get("age")
    hba1c = patient.get("hba1c")
    bmi = patient.get("bmi")
    egfr = patient.get("egfr")

    if "age_range" in inclusion and age is not None:
        low, high = inclusion["age_range"]
        if not (low <= age <= high):
            reasons.append("Age outside inclusion range")

    if "hba1c_min" in inclusion and hba1c is not None:
        if hba1c < inclusion["hba1c_min"]:
            reasons.append("HbA1c below inclusion minimum")

    if "hba1c_range" in inclusion and hba1c is not None:
        low, high = inclusion["hba1c_range"]
        if not (low <= hba1c <= high):
            reasons.append("HbA1c outside inclusion range")

    if "bmi_min" in inclusion and bmi is not None:
        if bmi < inclusion["bmi_min"]:
            reasons.append("BMI below inclusion minimum")

    if "egfr_min" in inclusion and egfr is not None:
        if egfr < inclusion["egfr_min"]:
            reasons.append("eGFR below inclusion threshold")

    if "severe_renal_impairment_egfr" in exclusion and egfr is not None:
        if egfr < exclusion["severe_renal_impairment_egfr"]:
            reasons.append("Severe renal impairment")

    return len(reasons) == 0, reasons


# ============================================================
# SAFETY SCORE
# ============================================================

def compute_safety_score(patient, drug, params):

    flags = derive_flags(patient)
    reasons = []
    excluded = False

    egfr = patient.get("egfr")

    if egfr is None:
        reasons.append("Missing eGFR – safety penalty applied")
        return params["missing_egfr_safety_score"], reasons, False

    if drug == "metformin" and flags["alcohol_risk"]:
        reasons.append("Alcohol / liver risk")
        excluded = True

    if drug == "empagliflozin" and flags["elderly"] and flags["hypertensive"]:
        reasons.append("Volume depletion risk")
        excluded = True

    if excluded:
        return 0.0, reasons, True

    return 1.0, ["No absolute safety exclusions"], False


# ============================================================
# CALIBRATED SCORING
# ============================================================

def compute_efficacy_score(patient, drug):
    hba = patient.get("hba1c")
    if hba is None:
        return 0.5

    if drug == "metformin":
        return 0.8 if hba >= 6.5 else 0.5

    if drug == "sitagliptin":
        return 0.75 if 6.5 <= hba <= 10.0 else 0.5

    if drug == "empagliflozin":
        return 0.8 if hba >= 7.0 else 0.5

    return 0.5


def compute_patient_factor_score(patient, drug):
    flags = derive_flags(patient)
    score = 0.5

    if drug == "metformin" and flags["obese"]:
        score += 0.2

    if drug == "empagliflozin" and flags["cvd_risk"]:
        score += 0.25

    if drug == "sitagliptin":
        if flags["elderly"]:
            score += 0.3
        if not flags["cvd_risk"]:
            score += 0.1
        if not flags["obese"]:
            score += 0.15

    return min(score, 1.0)


def compute_guideline_score(patient, drug):

    flags = derive_flags(patient)

    if drug == "metformin":
        return 0.9

    if drug == "empagliflozin" and flags["cvd_risk"]:
        return 0.85

    if drug == "sitagliptin":
        return 0.75

    return 0.7


# ============================================================
# DRUG EVALUATION
# ============================================================

def evaluate_drug(patient, drug, weights, params, config):

    eligible_config, config_reasons = check_config_eligibility(patient, drug, config)
    if not eligible_config:
        return {"eligible": False, "scores": {}, "reasons": config_reasons}

    s, s_reason, excluded = compute_safety_score(patient, drug, params)
    if excluded:
        return {"eligible": False, "scores": {}, "reasons": s_reason}

    e = compute_efficacy_score(patient, drug)
    p = compute_patient_factor_score(patient, drug)
    g = compute_guideline_score(patient, drug)

    s_w = round(s * weights["safety_profile"], 3)
    e_w = round(e * weights["efficacy_match"], 3)
    p_w = round(p * weights["patient_factors"], 3)
    g_w = round(g * weights["clinical_guidelines"], 3)

    composite = round(s_w + e_w + p_w + g_w, 3)

    return {
        "eligible": True,
        "scores": {
            "safety_weighted": s_w,
            "efficacy_weighted": e_w,
            "patient_weighted": p_w,
            "guideline_weighted": g_w,
            "composite": composite
        },
        "reasons": s_reason
    }


# ============================================================
# PIPELINE
# ============================================================

def run_from_csv(input_path, config, params):

    df = pd.read_csv(input_path)
    key_map = _get_canonical_key_map()
    weights = config["scoring_weights"]
    results = []

    for _, row in df.iterrows():

        patient = patient_from_csv_row(row.to_dict(), key_map)

        if not patient.get("is_diabetic"):
            continue

        valid, _ = validate_patient(patient)
        if not valid:
            continue

        drug_results = {
            d: evaluate_drug(patient, d, weights, params, config)
            for d in ["metformin", "sitagliptin", "empagliflozin"]
        }

        eligible = {k: v for k, v in drug_results.items() if v["eligible"]}

        if eligible:
            recommendation = max(
                eligible.items(),
                key=lambda x: x[1]["scores"]["composite"]
            )[0]
            global_exclusion_summary = "No global exclusion – recommendation generated"
        else:
            recommendation = "No eligible drug – clinical review required"
            exclusion_msgs = []
            for drug, info in drug_results.items():
                reason_text = "; ".join(info["reasons"])
                exclusion_msgs.append(f"{drug}: {reason_text}")
            global_exclusion_summary = " | ".join(exclusion_msgs)

        results.append({
            "patient_id": patient.get("patient_id"),
            "recommendation": recommendation,
            "global_exclusion_summary": global_exclusion_summary,
            "details": drug_results
        })

    return results


# ============================================================
# EXCEL EXPORT
# ============================================================

def save_results_to_excel(results, output_path):

    rows = []

    for r in results:
        row = {"Patient_ID": r["patient_id"]}

        for drug in ["metformin", "sitagliptin", "empagliflozin"]:
            info = r["details"][drug]

            if info["eligible"]:
                row[f"{drug}_Safety"] = info["scores"]["safety_weighted"]
                row[f"{drug}_Efficacy"] = info["scores"]["efficacy_weighted"]
                row[f"{drug}_Patient"] = info["scores"]["patient_weighted"]
                row[f"{drug}_Guideline"] = info["scores"]["guideline_weighted"]
                row[f"{drug}_Total"] = info["scores"]["composite"]
                row[f"{drug}_Reason"] = "Eligible – no exclusion"
            else:
                row[f"{drug}_Safety"] = "Excluded"
                row[f"{drug}_Efficacy"] = "Excluded"
                row[f"{drug}_Patient"] = "Excluded"
                row[f"{drug}_Guideline"] = "Excluded"
                row[f"{drug}_Total"] = "Excluded"
                row[f"{drug}_Reason"] = "\n".join(info["reasons"])

        row["Global_Exclusion_Summary"] = r["global_exclusion_summary"]
        row["Recommended_Drug"] = r["recommendation"]

        rows.append(row)

    pd.DataFrame(rows).to_excel(output_path, index=False)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    config = load_config("config/drug_config.json")
    params = deepcopy(DEFAULT_PARAMS)

    results = run_from_csv(
        "data/eligible_patients_with_id.csv",
        config,
        params
    )

    os.makedirs("outputs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with open(f"outputs/drug_recommendations_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    save_results_to_excel(
        results,
        f"outputs/drug_recommendations_{timestamp}.xlsx"
    )

    print("✅ Explainable drug matching completed.")