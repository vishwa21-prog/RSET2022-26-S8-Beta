# eligibility_screening_only.py
"""
Load a CSV, apply inclusion/exclusion criteria and an optional ML probability filter,
and save the shortlisted eligible patients to a CSV.

Configure thresholds in the CONFIG block below.
"""

import os
import pandas as pd
import numpy as np

# Optional: import xgboost if you want to use model-based filtering
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except Exception:
    XGB_AVAILABLE = False

# ---------------- CONFIG ----------------
DATA_CSV = "diabetes_test_with_formatted_id.csv"          # input CSV filename (change to your file)
MODEL_PATH = "xgb_diabetes_model.json"  # trained XGB model (set to None to skip)
OUTPUT_CSV = "eligible_patients_with_id.csv"    # output CSV
USE_MODEL_FILTER = True                 # set False to ignore model probability
P_THRESH = 0.5                          # ML probability threshold (if using model)

# Clinical criteria (customize per trial protocol)
MIN_AGE = 18
MAX_AGE = 75
HBA1C_MIN = 6.5          # percent
FBG_MIN = 126            # mg/dL (confirm units in your data)

# Missing-data policy:
# If a required numeric field is missing we send row to review (not auto eligible).
TREAT_MISSING_AS_FAIL = False
# ----------------------------------------

def to_float_safe(x):
    try:
        return float(x)
    except Exception:
        return np.nan

def to_bool_safe(x):
    if pd.isna(x):
        return False
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, np.integer)):
        return bool(x)
    s = str(x).strip().lower()
    return s in ("1", "true", "t", "yes", "y")

def load_model_if_available(path):
    if not XGB_AVAILABLE:
        print("[MODEL] xgboost not available - skipping model filter.")
        return None
    if path is None or not os.path.exists(path):
        print(f"[MODEL] Model path '{path}' not found - skipping model filter.")
        return None
    try:
        m = xgb.XGBClassifier()
        m.load_model(path)
        print(f"[MODEL] Loaded XGBoost model from: {path}")
        return m
    except Exception as e:
        print(f"[MODEL] Failed to load model: {e} - skipping model filter.")
        return None

def check_inclusion_row(row):
    """Return (inclusion_bool, notes_list)"""
    notes = []
    # Age
    age = row.get("Age", np.nan)
    if pd.isna(age):
        notes.append("Age missing")
        incl_age = False if TREAT_MISSING_AS_FAIL else None
    else:
        incl_age = (MIN_AGE <= age <= MAX_AGE)
        if not incl_age:
            notes.append(f"Age {age} outside [{MIN_AGE},{MAX_AGE}]")
        else:
            notes.append(f"Age {age} OK")
    # Glycemic criteria: HbA1c or fasting BG
    hb = row.get("HbA1c", np.nan)
    fbg = row.get("Fasting_Blood_Glucose", np.nan)
    hb_ok = False
    fbg_ok = False
    if pd.notna(hb):
        hb_ok = hb >= HBA1C_MIN
        notes.append(f"HbA1c={hb:.2f}" if not np.isnan(hb) else "HbA1c missing")
    else:
        notes.append("HbA1c missing")
    if pd.notna(fbg):
        fbg_ok = fbg >= FBG_MIN
        notes.append(f"FBG={fbg:.2f}" if not np.isnan(fbg) else "FBG missing")
    else:
        notes.append("FBG missing")

    # Determine glycemic inclusion
    if hb_ok or fbg_ok:
        gly_ok = True
        notes.append("Glycemic criterion met")
    else:
        if pd.isna(hb) and pd.isna(fbg):
            gly_ok = None  # missing both -> review
            notes.append("Both glycemic values missing -> review")
        else:
            gly_ok = False
            notes.append("Glycemic criterion NOT met")

    # Final inclusion decision: require age_ok and gly_ok True
    # if any is None (missing) we treat as review (not auto eligible)
    if (incl_age is None) or (gly_ok is None):
        return None, notes
    inclusion = bool(incl_age) and bool(gly_ok)
    return inclusion, notes

def check_exclusion_row(row):
    """Return (exclusion_bool, notes_list)"""
    notes = []
    excl = False
    # Example exclusion: heavy alcohol consumption
    if "Alcohol_Consumption_Heavy" in row.index and to_bool_safe(row["Alcohol_Consumption_Heavy"]):
        excl = True
        notes.append("Excluded: heavy alcohol consumption")
    # Example exclusion: pregnant (if column exists)
    if "Pregnant" in row.index and to_bool_safe(row["Pregnant"]):
        excl = True
        notes.append("Excluded: pregnant")
    # Add more exclusion checks here (e.g. severe liver disease, eGFR < threshold) if columns exist
    return excl, notes

def main():
    # Use a local flag so we can modify it safely
    use_model = bool(USE_MODEL_FILTER)
    # 1) Load CSV
    if not os.path.exists(DATA_CSV):
        raise FileNotFoundError(f"Input file '{DATA_CSV}' not found. Change DATA_CSV or place the file here.")
    df = pd.read_csv(DATA_CSV)
    print(f"[LOAD] Loaded {len(df)} rows from '{DATA_CSV}'")

    # 2) Normalize numeric fields
    for col in ["Age", "HbA1c", "Fasting_Blood_Glucose"]:
        if col in df.columns:
            df[col] = df[col].apply(to_float_safe)

    # 3) Prepare Sex column if one-hot present
    if "Sex" not in df.columns and ("Sex_Male" in df.columns or "Sex_Female" in df.columns):
        def infer_sex(r):
            if "Sex_Male" in r and to_bool_safe(r["Sex_Male"]):
                return "Male"
            if "Sex_Female" in r and to_bool_safe(r["Sex_Female"]):
                return "Female"
            return np.nan
        df["Sex"] = df.apply(infer_sex, axis=1)

    # 4) Load model if requested
    model = None
    if use_model:
        model = load_model_if_available(MODEL_PATH)
        if model is None:
            print("[MODEL] Disabling model filter due to load failure.")
            use_model = False

    # 5) If model present, produce probabilities
    if use_model and model is not None:
        # assume model expects same feature columns as present in CSV except target
        feature_cols = [c for c in df.columns if c != "Diabetes"]
        # align column order robustly (fill missing cols with zeros if any)
        # If your model was trained with a fixed feature list, prefer to load that list and reorder.
        X = df.reindex(columns=feature_cols, fill_value=0).fillna(0)
        try:
            probs = model.predict_proba(X)[:, 1]
            df["model_prob"] = probs
            print("[MODEL] Predicted probabilities added as 'model_prob' column.")
        except Exception as e:
            print(f"[MODEL] Prediction failed: {e} - disabling model filter.")
            use_model = False
            df["model_prob"] = np.nan
    else:
        df["model_prob"] = np.nan

    # 6) Apply inclusion/exclusion + ML threshold
    eligible_indices = []
    review_indices = []
    excluded_indices = []
    not_eligible_indices = []
    reasons_list = []

    for idx, row in df.iterrows():
        notes = []
        inclusion, incl_notes = check_inclusion_row(row)
        excl_flag, excl_notes = check_exclusion_row(row)
        notes.extend(incl_notes)
        notes.extend(excl_notes)

        # ML check
        ml_ok = True
        if use_model:
            prob = row.get("model_prob", np.nan)
            if pd.isna(prob):
                notes.append("No model_prob -> review")
                ml_ok = None
            else:
                if prob >= P_THRESH:
                    notes.append(f"Model prob {prob:.3f} >= {P_THRESH}")
                    ml_ok = True
                else:
                    notes.append(f"Model prob {prob:.3f} < {P_THRESH} -> review")
                    ml_ok = False

        # Decision logic
        # If excluded -> excluded
        if excl_flag:
            excluded_indices.append(idx)
            reason = ["EXCLUDED"] + notes
            reasons_list.append("; ".join(reason))
            continue

        # If inclusion is None (missing critical values) -> review
        if inclusion is None:
            review_indices.append(idx)
            reason = ["REVIEW (missing fields)"] + notes
            reasons_list.append("; ".join(reason))
            continue

        # If inclusion == False -> not eligible
        if not inclusion:
            not_eligible_indices.append(idx)
            reason = ["NOT_ELIGIBLE (inclusion failed)"] + notes
            reasons_list.append("; ".join(reason))
            continue

        # inclusion True here
        if use_model:
            if ml_ok is None:
                review_indices.append(idx)
                reason = ["REVIEW (model prob missing)"] + notes
                reasons_list.append("; ".join(reason))
            elif ml_ok is False:
                review_indices.append(idx)
                reason = ["REVIEW (model prob below threshold)"] + notes
                reasons_list.append("; ".join(reason))
            else:
                eligible_indices.append(idx)
                reason = ["ELIGIBLE"] + notes
                reasons_list.append("; ".join(reason))
        else:
            # No model filter: inclusion True and not excluded => eligible
            eligible_indices.append(idx)
            reason = ["ELIGIBLE (model not used)"] + notes
            reasons_list.append("; ".join(reason))

    # attach reason and flags
    df["eligibility_reason"] = reasons_list
    df["eligible"] = False
    df.loc[eligible_indices, "eligible"] = True
    df["needs_review"] = False
    df.loc[review_indices, "needs_review"] = True
    df["excluded"] = False
    df.loc[excluded_indices, "excluded"] = True

    # Create output CSV of eligible patients
    df_eligible = df[df["eligible"] == True].copy()
    print(f"[RESULT] Eligible patients: {len(df_eligible)} / {len(df)}")
    print(f"[RESULT] Needs manual review: {len(review_indices)}")
    print(f"[RESULT] Excluded: {len(excluded_indices)}")
    print(f"[RESULT] Not eligible (failed inclusion): {len(not_eligible_indices)}")

    df_eligible.to_csv(OUTPUT_CSV, index=False)
    print(f"[SAVE] Saved eligible patients to '{OUTPUT_CSV}'")

if __name__ == "__main__":
    main()