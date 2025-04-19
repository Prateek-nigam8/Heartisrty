import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load and preprocess dataset
df = pd.read_csv("heart1.csv")
df.drop(["HeartDisease"], axis=1, inplace=True)
category = [
    "Sex",
    "ChestPainType",
    "RestingECG",
    "ExerciseAngina",
    "ST_Slope",
    "FastingBS",
]
df = pd.get_dummies(df, columns=category)
features = df.columns

# Normal/Healthy thresholds
normal_ranges = {
    "RestingBP": 120,  # mmHg
    "Cholesterol": 200,  # mg/dL
    "MaxHR": 100,  # bpm
    "Oldpeak": 1.0,  # ST depression
}


def check_risk_factors(patient):
    """
    Compares patient values to normal thresholds and returns a list of flagged features.
    """
    flags = []
    if patient.get("RestingBP", 0) > normal_ranges["RestingBP"]:
        flags.append(
            f"RestingBP ({patient['RestingBP']} > {normal_ranges['RestingBP']})"
        )
    if patient.get("Cholesterol", 0) > normal_ranges["Cholesterol"]:
        flags.append(
            f"Cholesterol ({patient['Cholesterol']} > {normal_ranges['Cholesterol']})"
        )
    if patient.get("MaxHR", 0) > normal_ranges["MaxHR"]:
        flags.append(f"MaxHR ({patient['MaxHR']} > {normal_ranges['MaxHR']})")
    if patient.get("Oldpeak", 0) > normal_ranges["Oldpeak"]:
        flags.append(f"Oldpeak ({patient['Oldpeak']} > {normal_ranges['Oldpeak']})")
    return flags


def predict_heart_disease(
    new_patient_data, features, model_path="heart_disease_xgb_model.pkl"
):
    """
    Predicts heart disease and flags any abnormal health metrics.
    """
    model = joblib.load(model_path)
    actual = new_patient_data.pop("HeartDisease", None)
    new_patient_df = pd.DataFrame([new_patient_data])
    new_patient_df = pd.get_dummies(new_patient_df)

    for col in features:
        if col not in new_patient_df.columns:
            new_patient_df[col] = 0

    new_patient_df = new_patient_df[features]

    prob = model.predict_proba(new_patient_df)[:, 1]
    prediction = int(prob[0] > 0.5)

    if prob[0] > 0.8:
        risk_level = "Severe"
    elif 0.4 <= prob[0] <= 0.7:
        risk_level = "Moderate"
    else:
        risk_level = "Healthy"

    # Check all values regardless of prediction
    flagged = check_risk_factors(new_patient_data)

    return actual, prediction, prob[0], risk_level, flagged


# Sample patients
patient_data_list = [
    {
        "Age": 30,
        "Sex": "Male",
        "ChestPainType": "ATA",
        "RestingBP": 120,
        "Cholesterol": 200,
        "FastingBS": 0,
        "RestingECG": "Normal",
        "MaxHR": 180,
        "ExerciseAngina": "No",
        "Oldpeak": 0.2,
        "ST_Slope": "Up",
        "HeartDisease": 0,
    },
    {
        "Age": 50,
        "Sex": "Female",
        "ChestPainType": "ASY",
        "RestingBP": 200,
        "Cholesterol": 300,
        "FastingBS": 1,
        "RestingECG": "ST",
        "MaxHR": 150,
        "ExerciseAngina": "Yes",
        "Oldpeak": 3.5,
        "ST_Slope": "Down",
        "HeartDisease": 1,
    },
    {
        "Age": 60,
        "Sex": "Female",
        "ChestPainType": "ATA",
        "RestingBP": 110,
        "Cholesterol": 168,
        "FastingBS": 0,
        "RestingECG": "Normal",
        "MaxHR": 80,
        "ExerciseAngina": "No",
        "Oldpeak": 0.2,
        "ST_Slope": "Up",
        "HeartDisease": 0,
    },
]

# Predict for each patient
for i, patient in enumerate(patient_data_list, 1):
    actual, predicted, probability, risk_lv, caution_flags = predict_heart_disease(
        patient.copy(), features
    )
    print(f"\n🩺 Patient {i}:")
    print(
        f"  Actual: {actual}, Predicted: {predicted} (Prob: {probability:.4f}), Risk Level: {risk_lv}"
    )
    if caution_flags:
        print(f"  ⚠️  Caution! Abnormal Parameters: {', '.join(caution_flags)}")
    else:
        print("  ✅ All vital parameters within normal range.")
