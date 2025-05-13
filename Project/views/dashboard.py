import streamlit as st
import pandas as pd
import io
import sys
import os
import time
import re

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from ocr import extract_medical_data
from validations import validate_health_data

import bcrypt

def save_health_data_to_db(health_data):
    st.write(health_data)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if "user" not in st.session_state or "id" not in st.session_state["user"]:
            st.error("User not logged in or user ID not found!")
            return False
        user_id = st.session_state["user"]["id"]
        required_fields = [
            'Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 
            'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 
            'Oldpeak', 'ST_Slope', 'SOSEmail'
        ]
        missing_fields = [field for field in required_fields if field not in health_data or not health_data[field]]
        if missing_fields:
            st.error(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False

        # Check if a record exists for the user_id
        cursor.execute("SELECT COUNT(*) FROM heart_patient_data WHERE user_id = %s", (user_id,))
        record_count = cursor.fetchone()[0]
        cursor.fetchall()  # Consume any remaining results to prevent "Unread result found"

        if record_count > 0:
            # Update existing record
            update_query = """
            UPDATE heart_patient_data
            SET 
                Age = %s,
                Sex = %s,
                ChestPainType = %s,
                RestingBP = %s,
                Cholesterol = %s,
                FastingBS = %s,
                RestingECG = %s,
                MaxHR = %s,
                ExerciseAngina = %s,
                Oldpeak = %s,
                ST_Slope = %s,
                sos_emergency_mail = %s
            WHERE user_id = %s
            """
            update_values = (
                health_data.get('Age'),
                health_data.get('Sex'),
                health_data.get('ChestPainType'),
                health_data.get('RestingBP'),
                health_data.get('Cholesterol'),
                health_data.get('FastingBS'),
                health_data.get('RestingECG'),
                health_data.get('MaxHR'),
                health_data.get('ExerciseAngina'),
                health_data.get('Oldpeak'),
                health_data.get('ST_Slope'),
                health_data.get('SOSEmail'),
                user_id
            )
            cursor.execute(update_query, update_values)
            st.info("Existing health data updated successfully.")
        else:
            # Insert new record
            insert_query = """
            INSERT INTO heart_patient_data (
                user_id, Age, Sex, ChestPainType, RestingBP, 
                Cholesterol, FastingBS, RestingECG, MaxHR, 
                ExerciseAngina, Oldpeak, ST_Slope, 
                sos_emergency_mail
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s
            )
            """
            insert_values = (
                user_id,
                health_data.get('Age'),
                health_data.get('Sex'),
                health_data.get('ChestPainType'),
                health_data.get('RestingBP'),
                health_data.get('Cholesterol'),
                health_data.get('FastingBS'),
                health_data.get('RestingECG'),
                health_data.get('MaxHR'),
                health_data.get('ExerciseAngina'),
                health_data.get('Oldpeak'),
                health_data.get('ST_Slope'),
                health_data.get('SOSEmail')
            )
            cursor.execute(insert_query, insert_values)
            st.info("New health data inserted successfully.")

        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error saving health data: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def show_upload_tab():
    st.subheader("Upload Medical Document for Scanning")
    st.write("Upload your medical report such as Heart report, Blood report, Complete blood count report, Lipid profile, Diabetic profile etc. as a PDF...")

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    
    if uploaded_file:
        st.write({"Filename": uploaded_file.name, "Size": f"{uploaded_file.size / 1024:.2f} KB"})
        
        if st.button("Extract Data from PDF"):
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            try:
                progress_text.text("Initiating OCR scan...")
                time.sleep(1)
                progress_bar.progress(25)
                
                with open("temp_uploaded.pdf", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                progress_bar.progress(50)
                progress_text.text("Scanning document...")
                time.sleep(1)
                
                extracted_metrics = extract_medical_data("temp_uploaded.pdf")
                
                progress_bar.progress(75)
                progress_text.text("Processing data...")
                time.sleep(1)
                
                if extracted_metrics:
                    st.session_state['pdf_processing_complete'] = True
                    for key in list(validate_health_data(extracted_metrics).keys()):
                        extracted_metrics.pop(key, None)
                    st.session_state["extracted_metrics"] = extracted_metrics                    
                    progress_bar.progress(100)
                    progress_text.text("Scan complete!")  
                    st.write(extracted_metrics)
                else:
                    st.warning("No data extracted.")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if os.path.exists("temp_uploaded.pdf"):
                    os.remove("temp_uploaded.pdf")


def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def show_manual_entry_tab():
    st.subheader("📝 Manual Health Data Entry")
    st.write("Please fill out each field below. All entries are required to assess your heart health accurately.")
    pre_filled = st.session_state.get("extracted_metrics", {})

    # Options for select boxes
    select_fields = {
        "Sex": ["Select Sex", "Male", "Female"],
        "ChestPainType": ["Select Chest Pain Type", "Typical Chest Pain During Activity", "Unusual Chest Pain", "Discomfort around Chest Area", "No Chest Pain / Silent Symptoms"],
        "RestingECG": ["Select ECG Result", "Normal", "ST-T Wave Abnormality", "Left Ventricular Hypertrophy"],
        "ST_Slope": ["Select ST Segment Slope", "Upsloping", "Flat", "Downsloping"],
        "ExerciseAngina": ["Select Exercise-Induced Chest Pain", "Yes", "No"]
    }

    # Compute selectbox indexes for pre-filled data
    select_indices = {}
    for field, options in select_fields.items():
        value = pre_filled.get(field, "")
        select_indices[field] = options.index(value) if value in options else 0

    if pre_filled:
        st.info("✅ We’ve pre-filled some fields from your uploaded report. Please review and correct if needed.")

    # Track save state
    if "data_saved" not in st.session_state:
        st.session_state["data_saved"] = False

    with st.form("health_metrics_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.text_input(
                "Age (years)",
                value=str(pre_filled.get("Age", "")),
                placeholder="e.g. 45",
                help="Enter your age in whole years (must be between 18 and 120)."
            )
            sex = st.selectbox(
                "Biological Sex",
                select_fields["Sex"],
                index=select_indices["Sex"],
                help="Select the sex assigned at birth."
            )
            resting_bp = st.text_input(
                "Resting Blood Pressure (mmHg)",
                value=str(pre_filled.get("RestingBP", "")),
                placeholder="e.g. 120",
                help="Enter your resting systolic blood pressure in mmHg (80–220)."
            )
            cholesterol = st.text_input(
                "Cholesterol Level (mg/dL)",
                value=str(pre_filled.get("Cholesterol", "")),
                placeholder="e.g. 200",
                help="Enter your fasting cholesterol in mg/dL (100–600)."
            )
            fasting_bs = st.text_input(
                "Fasting Blood Sugar (mg/dL)",
                value=str(pre_filled.get("FastingBS", "")),
                placeholder="e.g. 85",
                help="Enter your fasting blood sugar level in mg/dL (50–400)."
            )
            sos_email = st.text_input(
                "Emergency Contact Email",
                value=pre_filled.get("SOSEmail", ""),
                placeholder="e.g. friend@example.com",
                help="Provide a valid email for your emergency contact."
            )

        with col2:
            max_hr = st.text_input(
                "Maximum Heart Rate (bpm)",
                value=str(pre_filled.get("MaxHR", "")),
                placeholder="e.g. 150",
                help="Enter the maximum heart rate recorded during exercise (60–220 bpm)."
            )
            chest_pain_type = st.selectbox(
                "Chest Pain Type",
                select_fields["ChestPainType"],
                index=select_indices["ChestPainType"],
                help="Choose the type of chest discomfort you experience."                

            )
            resting_ecg = st.selectbox(
                "Resting ECG Result",
                select_fields["RestingECG"],
                index=select_indices["RestingECG"],
                help="Select the ECG classification at rest (Heart's Electrical Reading)."
            )
            oldpeak = st.text_input(
                "ST Depression (Oldpeak)",
                value=str(pre_filled.get("Oldpeak", "")),
                placeholder="e.g. 1.2",
                help="Enter the ST depression induced by exercise relative to rest (0.0–10.0)."
            )
            st_slope = st.selectbox(
                "ST Segment Slope",
                select_fields["ST_Slope"],
                index=select_indices["ST_Slope"],
                help="Direction of ECG Reading During Stress (Up / Flat / Down)."
            )
            exercise_angina = st.selectbox(
                "Exercise-Induced Chest Pain",
                select_fields["ExerciseAngina"],
                index=select_indices["ExerciseAngina"],
                help="Did you experience chest pain during exercise?"
            )

        submitted = st.form_submit_button("Save Health Data")

        if submitted:
            health_data = {
                "Age": age,
                "Sex": sex,
                "ChestPainType": chest_pain_type,
                "RestingBP": resting_bp,
                "Cholesterol": cholesterol,
                "FastingBS": fasting_bs,
                "MaxHR": max_hr,
                "Oldpeak": oldpeak,
                "ST_Slope": st_slope,
                "ExerciseAngina": exercise_angina,
                "RestingECG": resting_ecg,
                "SOSEmail": sos_email
            }

            errors = validate_health_data(health_data)
            if errors:
                for field, msg in errors.items():
                    st.error(f"❌ {field}: {msg}")
            else:
                # Safe type conversions
                health_data.update({
                    "Age": int(age),
                    "RestingBP": float(resting_bp),
                    "Cholesterol": float(cholesterol),
                    "FastingBS": float(fasting_bs),
                    "MaxHR": float(max_hr),
                    "Oldpeak": float(oldpeak)
                })
                if save_health_data_to_db(health_data):
                    st.success("✅ Health data saved successfully!")
                    st.session_state["data_saved"] = True
                else:
                    st.session_state["data_saved"] = False

    # After saving, navigate to analysis
    if st.session_state.get("data_saved"):
        if st.button("➡️ Go to analysis tab"):
            st.session_state["data_saved"] = False
            st.switch_page("views/analysis.py")



col1, col2 = st.columns([8, 1])  # Adjust the middle ratio as needed

with col1:
    st.markdown("# 📊 Dashboard")  # Title on the left

with col2:
    if "user" in st.session_state and "id" in st.session_state["user"]:
        if st.button("Log out"):
            del st.session_state["user"]
            st.switch_page("views/login.py")

if "notices" in st.session_state:
    for i in st.session_state["notices"]:
        st.success(i)
    del st.session_state["notices"]

if "user" not in st.session_state:
    st.error("You are not logged in!")
    if st.button("Go to Login"):
        st.switch_page("views/login.py")
else:
    st.success(f"Welcome, {st.session_state['user']['username']}!")

    if 'pdf_processing_complete' not in st.session_state:
        st.session_state['pdf_processing_complete'] = False

    # Section 1: Upload and extract    
    show_upload_tab()  # Handles file upload and sets session_state["extracted_metrics"]

    # Separator line
    st.markdown("---")

    # Section 2: Manual Entry Form
    show_manual_entry_tab()
