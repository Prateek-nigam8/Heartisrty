import streamlit as st
import pandas as pd
import io
import sys
import os
import time

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from ocr import extract_medical_data
import bcrypt
def save_health_data_to_db(health_data):
    """Save health data to the heart_patient_data table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Ensure user_id is available in the session
        if "user" not in st.session_state or "id" not in st.session_state["user"]:
            st.error("User not logged in or user ID not found!")
            return False
        
        user_id = st.session_state["user"]["id"]
        
        # Prepare the SQL query to insert heart patient data
        query = """
        INSERT INTO heart_patient_data (
            user_id, Age, Sex, ChestPainType, RestingBP, 
            Cholesterol, FastingBS, RestingECG, MaxHR, 
            ExerciseAngina, Oldpeak, ST_Slope, Smoking, 
            sos_emergency_mail
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s
        )
        """
        
        # Map the health_data to match the database schema
        values = (
            user_id,  # Add user_id here
            health_data.get('Age', None),
            health_data.get('Sex', 'Male'),  # Default to 'Male'
            {
                'Typical Angina': 'TA', 
                'Atypical Angina': 'ATA', 
                'Non-Anginal Pain': 'NAP', 
                'Asymptomatic': 'ASY'
            }.get(health_data.get('ChestPainType', 'Typical Angina'), 'TA'),
            health_data.get('RestingBP', None),
            health_data.get('Cholesterol', None),
            1 if health_data.get('FastingBloodSugar', 0) > 120 else 0,
            {
                'Normal': 'Normal', 
                'ST-T Wave Abnormality': 'ST', 
                'Left Ventricular Hypertrophy': 'LVH'
            }.get(health_data.get('RestingECG', 'Normal'), 'Normal'),
            health_data.get('MaxHeartRate', None),
            'Yes' if health_data.get('ExerciseAngina', 'No') == 'Yes' else 'No',
            health_data.get('Oldpeak', None),
            {
                'Upsloping': 'Up', 
                'Flat': 'Flat', 
                'Downsloping': 'Down'
            }.get(health_data.get('ST_Slope', 'Upsloping'), 'Up'),
            'Yes' if health_data.get('Smoking', 'No') == 'Yes' else 'No',
            health_data.get('SOSEmail', None)
        )
        
        cursor.execute(query, values)
        conn.commit()
        st.success("Health data saved successfully to database!")
        return True
    except Exception as e:
        st.error(f"Error saving health data: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def show(go_to_page):
    st.title("📊 Dashboard")
    
    if "user" in st.session_state:
        st.success(f"Welcome, {st.session_state['user']['username']}!")
        
        # Initialize session state for tracking PDF processing
        if 'pdf_processing_complete' not in st.session_state:
            st.session_state['pdf_processing_complete'] = False
        
        tab1, tab2 = st.tabs(["Upload Document (PDF)", "Manual Entry"])
        
        with tab1:
            st.subheader("Upload Medical Document for Scanning")
            st.write("Upload your medical report as a PDF and we'll extract the relevant heart health metrics.")
            
            uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
            
            if uploaded_file is not None:
                st.write("PDF detected.")
                
                file_details = {"Filename": uploaded_file.name, "File Size": f"{uploaded_file.size / 1024:.2f} KB"}
                st.write(file_details)
                
                if st.button("Extract Data from PDF"):
                    # Create a placeholder for progress updates
                    progress_text = st.empty()
                    progress_bar = st.progress(0)
                    
                    try:
                        # Simulate OCR scanning process
                        progress_text.text("Initiating OCR scan...")
                        time.sleep(1)
                        
                        progress_bar.progress(25)
                        progress_text.text("Preparing document for scanning...")
                        time.sleep(1)
                        
                        # Save uploaded file temporarily
                        with open("temp_uploaded.pdf", "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        progress_bar.progress(50)
                        progress_text.text("Scanning medical document...")
                        time.sleep(1)
                        
                        # Use OCR to extract medical data
                        extracted_metrics = extract_medical_data("temp_uploaded.pdf")
                        
                        progress_bar.progress(75)
                        progress_text.text("Processing extracted data...")
                        time.sleep(1)
                        
                        if extracted_metrics:
                            # Ensure numeric values are non-zero or use default
                            if 'trestbps' not in extracted_metrics or extracted_metrics['trestbps'] < 80:
                                extracted_metrics['trestbps'] = 120
                            
                            st.session_state["extracted_metrics"] = extracted_metrics
                            st.session_state['pdf_processing_complete'] = True
                            
                            progress_bar.progress(100)
                            progress_text.text("Scan complete!")
                            
                            # Wait for 10 seconds and then switch to manual entry tab
                            time.sleep(10)
                            st.query_params(tab="Manual Entry")

                            st.experimental_rerun()
                        else:
                            st.warning("No health metrics could be extracted from the PDF.")
                    
                    except Exception as e:
                        st.error(f"Error processing PDF: {e}")
                    
                    finally:
                        # Clean up temporary file
                        if os.path.exists("temp_uploaded.pdf"):
                            os.remove("temp_uploaded.pdf")
        
        with tab2:
            st.subheader("Manual Health Data Entry")
            st.write("Please fill in your cardiovascular health metrics:")
            
            pre_filled = {}
            if "extracted_metrics" in st.session_state:
                pre_filled = st.session_state["extracted_metrics"]
                st.info("Some fields have been pre-filled with data extracted from your uploaded document.")
            
            with st.form("health_metrics_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Set default or pre-filled value for Resting BP to ensure it's >= min_value
                    default_resting_bp = max(80, int(pre_filled.get("trestbps", 120)))
                    
                    age = st.number_input(
                        "Age", 
                        min_value=18, 
                        max_value=120, 
                        value=int(pre_filled.get("Age", 40)) if "Age" in pre_filled else 40
                    )
                    
                    sex = st.selectbox(
                        "Sex", 
                        ["Male", "Female"], 
                        index=0 if pre_filled.get("Sex", "Male") == "Male" else 1
                    )
                    
                    resting_bp = st.number_input(
                        "Resting Blood Pressure (mmHg)", 
                        min_value=80, 
                        max_value=220, 
                        value=default_resting_bp
                    )
                    
                    cholesterol = st.number_input(
                        "Cholesterol (mg/dL)", 
                        min_value=100, 
                        max_value=600, 
                        value=int(pre_filled.get("chol", 200))
                    )
                    
                    fasting_blood_sugar = st.number_input(
                        "Fasting Blood Sugar (mg/dL)", 
                        min_value=50, 
                        max_value=400, 
                        value=max(50, int(pre_filled.get("fbs", 100)))
                    )
                
                with col2:
                    max_heart_rate = st.number_input(
                        "Maximum Heart Rate (bpm)", 
                        min_value=60, 
                        max_value=220, 
                        value=int(pre_filled.get("MaxHeartRate", 150))
                    )
                    
                    chest_pain_type = st.selectbox(
                        "Chest Pain Type", 
                        ["Typical Angina", "Atypical Angina", "Non-Anginal Pain", "Asymptomatic"],
                        index=pre_filled.get("cp", 0) if "cp" in pre_filled else 0
                    )
                    
                    oldpeak = st.number_input(
                        "Oldpeak (ST depression)", 
                        min_value=0.0, 
                        max_value=10.0, 
                        value=float(pre_filled.get("Oldpeak", 0.0))
                    )
                    
                    st_slope = st.selectbox(
                        "ST Slope", 
                        ["Upsloping", "Flat", "Downsloping"],
                        index=pre_filled.get("ST_Slope", 0) if "ST_Slope" in pre_filled else 0
                    )
                    
                    exercise_angina = st.selectbox(
                        "Exercise Induced Angina",
                        ["No", "Yes"],
                        index=0 if pre_filled.get("ExerciseAngina", "No") == "No" else 1
                    )
                    
                    smoking = st.selectbox(
                        "Smoking Status",
                        ["No", "Yes"],
                        index=0 if pre_filled.get("Smoking", "No") == "No" else 1
                    )
                    
                    sos_email = st.text_input(
                        "Emergency Contact Email", 
                        placeholder="Enter email for emergency contact",
                        value=pre_filled.get("SOSEmail", "")
                    )
                
                # Add the form submit button
                submit_button = st.form_submit_button("Save Health Data")
                
                if submit_button:
                    # Prepare health data dictionary
                    health_data = {
                        "Age": age,
                        "Sex": sex,
                        "ChestPainType": chest_pain_type,
                        "RestingBP": resting_bp,
                        "Cholesterol": cholesterol,
                        "FastingBloodSugar": fasting_blood_sugar,
                        "MaxHeartRate": max_heart_rate,
                        "RestingECG": "Normal",  # Default value, can be modified if needed
                        "ExerciseAngina": exercise_angina,
                        "Oldpeak": oldpeak,
                        "ST_Slope": st_slope,
                        "Smoking": smoking,
                        "SOSEmail": sos_email
                    }
                    
                    # Save health data to database
                    result = save_health_data_to_db(health_data)
                    
                    if result:
                        st.success("Health data saved successfully!")
        
        if st.button("Logout"):
            del st.session_state["user"]
            go_to_page("landing")
    else:
        st.error("You are not logged in!")
        if st.button("Go to Login"):
            go_to_page("login")