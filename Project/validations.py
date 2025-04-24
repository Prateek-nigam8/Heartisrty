import re

def validate_health_data(data: dict) -> dict:
    """
    Validates the health data dictionary.

    Args:
        data (dict): Dictionary containing health data fields.

    Returns:
        tuple: A tuple containing a boolean indicating overall validity and a dictionary of error messages.
    """
    errors = {}

    def is_int(value):
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False

    def is_float(value):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    # Age: Required, Integer between 18 and 120
    age = data.get("Age")
    if not age:
        errors["Age"] = "Age is required."
    elif not is_int(age) or not (18 <= int(age) <= 120):
        errors["Age"] = "Age must be an integer between 18 and 120."

    # Sex: Required
    sex = data.get("Sex")
    if not sex:
        errors["Sex"] = "Sex is required."
    elif sex not in ["Male", "Female"]:
        errors["Sex"] = "Sex must be 'Male' or 'Female'."

    # Chest Pain Type
    chest_pain = data.get("ChestPainType")
    valid_chest_pain_types = ["Typical Angina", "Atypical Angina", "Non-Anginal Pain", "Asymptomatic"]
    if not chest_pain:
        errors["ChestPainType"] = "Chest Pain Type is required."
    elif chest_pain not in valid_chest_pain_types:
        errors["ChestPainType"] = f"Chest Pain Type must be one of: {', '.join(valid_chest_pain_types)}."

    # Resting Blood Pressure
    resting_bp = data.get("RestingBP")
    if not resting_bp:
        errors["RestingBP"] = "Resting Blood Pressure is required."
    elif not is_int(resting_bp) or not (80 <= int(resting_bp) <= 220):
        errors["RestingBP"] = "Resting Blood Pressure must be an integer between 80 and 220."

    # Cholesterol
    cholesterol = data.get("Cholesterol")
    if not cholesterol:
        errors["Cholesterol"] = "Cholesterol is required."
    elif not is_int(cholesterol) or not (100 <= int(cholesterol) <= 600):
        errors["Cholesterol"] = "Cholesterol must be an integer between 100 and 600."

    # Fasting Blood Sugar
    fasting_bs = data.get("FastingBS")
    if not fasting_bs:
        errors["FastingBS"] = "Fasting Blood Sugar is required."
    elif not is_int(fasting_bs) or not (50 <= int(fasting_bs) <= 400):
        errors["FastingBS"] = "Fasting Blood Sugar must be an integer between 50 and 400."

    # Max Heart Rate
    max_hr = data.get("MaxHR")
    if not max_hr:
        errors["MaxHR"] = "Maximum Heart Rate is required."
    elif not is_int(max_hr) or not (60 <= int(max_hr) <= 220):
        errors["MaxHR"] = "Maximum Heart Rate must be an integer between 60 and 220."

    # Oldpeak
    oldpeak = data.get("Oldpeak")
    if not oldpeak:
        errors["Oldpeak"] = "Oldpeak is required."
    elif not is_float(oldpeak) or not (0.0 <= float(oldpeak) <= 10.0):
        errors["Oldpeak"] = "Oldpeak must be a float between 0.0 and 10.0."

    # ST Slope
    st_slope = data.get("ST_Slope")
    valid_st_slopes = ["Upsloping", "Flat", "Downsloping"]
    if not st_slope:
        errors["ST_Slope"] = "ST Slope is required."
    elif st_slope not in valid_st_slopes:
        errors["ST_Slope"] = f"ST Slope must be one of: {', '.join(valid_st_slopes)}."

    # Exercise Angina
    exercise_angina = data.get("ExerciseAngina")
    if not exercise_angina:
        errors["ExerciseAngina"] = "Exercise Angina is required."
    elif exercise_angina not in ["Yes", "No"]:
        errors["ExerciseAngina"] = "Exercise Angina must be 'Yes' or 'No'."

    # RestingECG
    resting_ecg = data.get("RestingECG")
    valid_resting_ecg = ["Normal", "ST-T Wave Abnormality", "Left Ventricular Hypertrophy"]
    if not resting_ecg:
        errors["RestingECG"] = "Resting ECG is required."
    elif resting_ecg not in valid_resting_ecg:
        errors["RestingECG"] = f"Resting ECG must be one of: {', '.join(valid_resting_ecg)}."

    # Emergency Email
    sos_email = data.get("SOSEmail")
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not sos_email:
        errors["SOSEmail"] = "Emergency Contact Email is required."
    elif not re.match(email_pattern, sos_email):
        errors["SOSEmail"] = "Emergency Contact Email must be a valid email address."
    
    return errors
