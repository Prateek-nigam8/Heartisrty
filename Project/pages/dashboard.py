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
    """Save health data to the heart_patient_data table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if "user" not in st.session_state or "id" not in st.session_state["user"]:
            st.error("User not logged in or user ID not found!")
            return False
        
        user_id = st.session_state["user"]["id"]
        
        # Ensure that no required field is empty
        required_fields = [
            'Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 
            'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 
            'Oldpeak', 'ST_Slope', 'SOSEmail'
        ]
        
        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in health_data or not health_data[field]]
        if missing_fields:
            st.error(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False
        
        # Prepare SQL query to insert health data
        query = """
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
        
        # Values to insert into the database
        values = (
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
        
        # Execute the query and commit the transaction
        cursor.execute(query, values)
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
    st.write("Upload your medical report as a PDF...")

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
                    st.session_state["extracted_metrics"] = extracted_metrics
                    st.session_state['pdf_processing_complete'] = True
                    progress_bar.progress(100)
                    progress_text.text("Scan complete!")
                    time.sleep(3)
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
    st.subheader("Manual Health Data Entry")
    st.write("⚠️ All fields are required. Please enter valid data for each.")
    pre_filled = st.session_state.get("extracted_metrics", {})
    # Define options for all selectboxes
    select_fields = {
        "Sex": ["", "Male", "Female"],
        "ChestPainType": ["", "Typical Angina", "Atypical Angina", "Non-Anginal Pain", "Asymptomatic"],
        "RestingECG": ["", "Normal", "ST-T Wave Abnormality", "Left Ventricular Hypertrophy"],
        "ST_Slope": ["", "Upsloping", "Flat", "Downsloping"],
        "ExerciseAngina": ["", "No", "Yes"]
    }

    # Pre-fill selectbox indices based on document values
    select_indices = {}
    for field, options in select_fields.items():
        value = pre_filled.get(field, "")
        index = options.index(value) if value in options else 0
        select_indices[field] = index

    if pre_filled:
        st.info("Fields pre-filled from uploaded document. Please review and complete all.")

    with st.form("health_metrics_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.text_input("Age", value=str(pre_filled.get("Age", "")))
            sex = st.selectbox("Sex", select_fields["Sex"], index=select_indices["Sex"])
            resting_bp = st.text_input("Resting BP (mmHg)", value=str(pre_filled.get("RestingBP", "")))
            cholesterol = st.text_input("Cholesterol (mg/dL)", value=str(pre_filled.get("Cholesterol", "")))
            fasting_bs = st.text_input("Fasting Blood Sugar (mg/dL)", value=str(pre_filled.get("FastingBS", "")))
            sos_email = st.text_input("Emergency Contact Email", value=pre_filled.get("SOSEmail", ""))

        with col2:
            max_hr = st.text_input("Maximum Heart Rate (bpm)", value=str(pre_filled.get("MaxHR", "")))
            chest_pain_type = st.selectbox("Chest Pain Type", select_fields["ChestPainType"], index=select_indices["ChestPainType"])
            resting_ecg = st.selectbox("Resting ECG", select_fields["RestingECG"], index=select_indices["RestingECG"])
            oldpeak = st.text_input("Oldpeak (ST depression)", value=str(pre_filled.get("Oldpeak", "")))
            st_slope = st.selectbox("ST Slope", select_fields["ST_Slope"], index=select_indices["ST_Slope"])
            exercise_angina = st.selectbox("Exercise Angina", select_fields["ExerciseAngina"], index=select_indices["ExerciseAngina"])

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
                    st.error(f"❌ {field}: #{msg}")
            else:
                # Convert to proper types now (safe after validation)
                health_data.update({
                    "Age": int(age),
                    "RestingBP": int(resting_bp),
                    "Cholesterol": int(cholesterol),
                    "FastingBS": float(fasting_bs),
                    "MaxHR": int(max_hr),
                    "Oldpeak": float(oldpeak)                    
                })                
                
                if save_health_data_to_db(health_data):
                    st.success("✅ Health data saved successfully!")
                    if st.button("Go to analysis tab"):
                        st.switch_page("pages/analysis.py")


col1, col2 = st.columns([8, 1])  # Adjust the middle ratio as needed

with col1:
    st.markdown("# 📊 Dashboard")  # Title on the left

with col2:
    if "user" in st.session_state and "id" in st.session_state["user"]:
        if st.button("Log out"):
            del st.session_state["user"]
            st.switch_page("pages/login.py")

if "notices" in st.session_state:
    for i in st.session_state["notices"]:
        st.success(i)
    del st.session_state["notices"]

if "user" not in st.session_state:
    st.error("You are not logged in!")
    if st.button("Go to Login"):
        st.switch_page("pages/login.py")
else:
    st.success(f"Welcome, {st.session_state['user']['username']}!")

    if 'pdf_processing_complete' not in st.session_state:
        st.session_state['pdf_processing_complete'] = False

    # Section 1: Upload and extract
    st.header("📤 Upload Medical Document")
    show_upload_tab()  # Handles file upload and sets session_state["extracted_metrics"]

    # Separator line
    st.markdown("---")

    # Section 2: Manual Entry Form
    st.header("📝 Manual Health Data Entry")
    show_manual_entry_tab()
