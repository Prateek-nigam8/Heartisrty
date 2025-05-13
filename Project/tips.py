# tips.py

def generate_health_tips(user_data: dict) -> list[str]:
    """
    Generates a list of markdown-formatted health tips based on user_data.

    Args:
        user_data (dict): Dictionary containing keys:
            'Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol',
            'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina',
            'Oldpeak', 'ST_Slope', 'SOSEmail'

    Returns:
        List of markdown strings with actionable tips.
    """
    tips = []

    # Cholesterol
    if user_data.get("Cholesterol", 0) > 200:
        tips.append(
            "- Your cholesterol is high. Consider reducing saturated fats, "
            "increasing soluble fiber, exercising regularly, and speaking "
            "to your doctor about statin therapy."
        )

    # Resting Blood Pressure
    if user_data.get("RestingBP", 0) > 120:
        tips.append(
            "- Elevated blood pressure can increase your risk. "
            "Reduce salt intake, practice stress-reduction techniques, "
            "and follow medical guidance on antihypertensive medications."
        )

    # Maximum Heart Rate
    max_hr = user_data.get("MaxHR", 0)
    if max_hr > 100:
        tips.append(
            "- Your maximum heart rate is elevated. While this can be normal "
            "for active individuals, consistently high MaxHR may indicate overexertion. "
            "Monitor during workouts and consult a healthcare professional if concerned."
        )
    elif max_hr and max_hr < 60:
        tips.append(
            "- A low maximum heart rate could signal chronotropic incompetence "
            "or high fitness. If you’re not an athlete, check for conduction or medication effects."
        )

    # Oldpeak (ST depression)
    if user_data.get("Oldpeak", 0) > 1.0:
        tips.append(
            "- Your ST depression is higher than normal and may indicate myocardial strain. "
            "Consider a follow-up stress imaging or cardiology consult."
        )

    # Fasting Blood Sugar
    if user_data.get("FastingBS") == 1:
        tips.append(
            "- High fasting blood sugar is a diabetes risk. "
            "Consider cutting back on simple sugars and refined carbs, "
            "and discuss glycemic control strategies with your provider."
        )

    # Age
    age = user_data.get("Age", 0)
    if age >= 60:
        tips.append(
            "- Age ≥ 60 raises cardiovascular risk. "
            "Ensure annual lipid panels, blood pressure checks, and discuss "
            "aspirin or statin therapy candidacy with your doctor."
        )

    # Sex
    sex = user_data.get("Sex")
    if sex is not None:
        if sex == "Male":
            tips.append(
                "- As a man, your risk of sudden cardiac events is higher. "
                "Adhere to regular cardiovascular screenings and heart-healthy lifestyle habits."
            )
        else:
            tips.append(
                "- As a woman, heart disease symptoms can be subtler. "
                "Report any atypical symptoms (e.g., nausea, jaw pain) immediately."
            )

    # Chest Pain Type
    cp = user_data.get("ChestPainType")
    if cp == "TA":
        tips.append(
            "- Typical angina detected. Prompt cardiology evaluation and stress testing are recommended."
        )
    elif cp == "ATA":
        tips.append(
            "- Atypical chest pain noted. If cardiac causes are excluded, consider GI or musculoskeletal workup."
        )
    elif cp == "NAP":
        tips.append(
            "- Non-anginal pain pattern. Investigate alternative causes such as GERD or costochondritis."
        )
    elif cp == "ASY":
        tips.append(
            "- Asymptomatic ECG changes—consider routine follow-up with ECG or Holter monitoring."
        )

    # Resting ECG
    recg = user_data.get("RestingECG")
    if recg in ["ST", "LVH"]:
        tips.append(
            "- Abnormal resting ECG (ST-T changes or LVH): "
            "Consider echocardiography or ambulatory ECG monitoring."
        )

    # ST Slope
    slope = user_data.get("ST_Slope")
    if slope == "Flat":
        tips.append(
            "- Flat ST slope correlates with moderate risk—consider stress imaging."
        )
    elif slope == "Down":
        tips.append(
            "- Down-sloping ST segment indicates high risk—urgent advanced ischemia workup is advised."
        )

    # Exercise-induced Angina
    if user_data.get("ExerciseAngina") == "Yes":
        tips.append(
            "- Exercise-induced angina suggests possible ischemia. "
            "Optimize antianginal therapy (e.g., β-blockers), tailor exercise intensity, "
            "and arrange cardiology review."
        )

    return tips
