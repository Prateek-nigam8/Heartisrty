import pandas as pd
import joblib
import numpy as np

# Load and preprocess dataset
df = pd.read_csv("heart1.csv")
df.drop(["HeartDisease"], axis=1, inplace=True)
category_cols = [
    "Sex",
    "ChestPainType",
    "RestingECG",
    "ExerciseAngina",
    "ST_Slope",
    "FastingBS",
]
df = pd.get_dummies(df, columns=category_cols)
features = df.columns.tolist()

# “Healthy” thresholds for quick flags
normal_ranges = {
    "RestingBP": 120,  # mmHg
    "Cholesterol": 200,  # mg/dL
    "MaxHR": 100,  # bpm (resting)
    "Oldpeak": 1.0,  # ST depression
}


def check_risk_factors(patient):
    """Return list of clinical parameters that exceed healthy thresholds."""
    flags = []
    if patient["RestingBP"] > normal_ranges["RestingBP"]:
        flags.append(f"RestingBP: {patient['RestingBP']}>120")
    if patient["Cholesterol"] > normal_ranges["Cholesterol"]:
        flags.append(f"Cholesterol: {patient['Cholesterol']}>200")
    if patient["MaxHR"] < normal_ranges["MaxHR"]:
        flags.append(f"MaxHR: {patient['MaxHR']}<100")
    if patient["Oldpeak"] > normal_ranges["Oldpeak"]:
        flags.append(f"Oldpeak: {patient['Oldpeak']}>1.0")
    return flags


def predict_heart_disease(patient, model_path="heart_disease_xgb_model.pkl"):
    """Load model, predict disease risk, risk level, and flag abnormal vitals."""
    model = joblib.load(model_path)

    # Prepare data for model
    x = pd.DataFrame([patient])
    x = pd.get_dummies(x)
    for col in features:
        if col not in x.columns:
            x[col] = 0
    x = x[features]

    # Predict probability & class
    prob = model.predict_proba(x)[:, 1][0]
    pred = int(prob > 0.5)
    if prob > 0.8:
        level = "Severe"
    elif prob > 0.4:
        level = "Moderate"
    else:
        level = "Healthy"

    flags = check_risk_factors(patient)
    return pred, prob, level, flags


def calculate_cardiovascular_age(patient):
    """Estimate cardiovascular age by adding years for each risk tier."""
    age = patient["Age"]
    extra = 0

    # RestingBP
    bp = patient["RestingBP"]
    if bp > 140:
        extra += 7
    elif bp > 130:
        extra += 5
    elif bp > 120:
        extra += 2

    # Cholesterol
    chol = patient["Cholesterol"]
    if chol > 280:
        extra += 8
    elif chol > 240:
        extra += 5
    elif chol > 200:
        extra += 3

    # Maximum heart rate under-exertion
    hr = patient["MaxHR"]
    if hr < 90:
        extra += 7
    elif hr < 120:
        extra += 4

    # ST-depression (Oldpeak)
    op = patient["Oldpeak"]
    if op > 2.0:
        extra += 7
    elif op > 1.0:
        extra += 4

    # Exercise-induced angina
    if patient["ExerciseAngina"] == "Yes":
        extra += 4

    # Fasting blood sugar
    if patient["FastingBS"] == 1:
        extra += 3

    # Cap the extra so it stays within a plausible range
    extra = min(extra, 20)
    return age + extra


# --- Example usage ---
patients = [
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

if __name__ == "__main__":
    for i, p in enumerate(patients, 1):
        actual_age = p["Age"]
        pred, prob, level, flags = predict_heart_disease(
            p, model_path="heart_disease_xgb_model.pkl"
        )
        cardio_age = calculate_cardiovascular_age(p)

        print(f"\nPatient {i}:")
        print(f" • Actual Age: {actual_age}   |   Cardiovascular Age: {cardio_age}", end="")
        print(f" • Heart Disease: {pred} (Prob:{prob:.3f}) – Risk Level: {level}")
        if flags:
            print(" • Abnormal Vitals:", ", ".join(flags))
        else:
            print(" • All vitals within normal thresholds.")