import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db import get_db_connection

def get_user_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total_users FROM users WHERE is_admin=0")
    total_users = cursor.fetchone()["total_users"]

    cursor.execute("""
        SELECT COUNT(DISTINCT u.id) as users_with_heart_data 
        FROM users u JOIN heart_patient_data h ON u.id = h.user_id
    """)
    users_with_heart_data = cursor.fetchone()["users_with_heart_data"]

    cursor.execute("""
        SELECT u.id, u.username, u.email, h.Age, h.Sex, h.Cholesterol, h.RestingBP, h.sos_emergency_mail 
        FROM users u 
        JOIN heart_patient_data h ON u.id = h.user_id 
        ORDER BY h.id DESC LIMIT 5
    """)
    recent_heart_data_users = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "total_users": total_users,
        "users_with_heart_data": users_with_heart_data,
        "recent_heart_data_users": recent_heart_data_users
    }

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, username, email, created_at 
        FROM users 
        WHERE is_admin = 0 
        ORDER BY created_at DESC
    """)
    users = cursor.fetchall()

    cursor.close()
    conn.close()
    return users

def get_all_heart_patient_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT u.username, u.email, h.* 
        FROM users u 
        JOIN heart_patient_data h ON u.id = h.user_id 
        ORDER BY h.id DESC
    """)
    heart_data = cursor.fetchall()

    cursor.close()
    conn.close()
    return heart_data

def send_sos_email(to_email, patient_data):
    sender_email = "patrick8200402@gmail.com"
    password = "dulg zfxo qebd thbe"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = "Urgent: Potential Heart Health Concern"

    body = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h2 style="color: #e63946;">🚨 Urgent Medical Attention Required</h2>
            <p>Based on the recent health assessment, there are potential heart health concerns that require immediate attention.</p>
            <h3>🩺 Patient Health Details:</h3>
            <ul>
                <li><strong>Age:</strong> {patient_data.get('Age', 'N/A')}</li>
                <li><strong>Sex:</strong> {patient_data.get('Sex', 'N/A')}</li>
                <li><strong>Resting Blood Pressure:</strong> {patient_data.get('RestingBP', 'N/A')} mmHg</li>
                <li><strong>Cholesterol:</strong> {patient_data.get('Cholesterol', 'N/A')} mg/dL</li>
                <li><strong>Chest Pain Type:</strong> {patient_data.get('ChestPainType', 'N/A')}</li>
                <li><strong>Predicted Heart Disease Risk:</strong> {patient_data.get('risk_percentage', 'N/A')}%</li>
            </ul>
            <p style="color: #d00000;"><strong>Please consult with a healthcare professional as soon as possible.</strong></p>
            <hr style="margin:20px 0;">
            <p style="font-size: 12px; color: gray;">This is an automated message from <strong>Heartistry - Your Cardiovascular Wellness Companion</strong>.</p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending SOS email: {e}")
        return False

# -------------------- Streamlit UI --------------------

if "is_admin" not in st.session_state or not st.session_state["is_admin"]:
    st.error("Unauthorized access!")
    if st.button("Go to Admin Login"):
        st.switch_page("views/admin_login.py")
else:
    st.title("👑 Admin Dashboard")

    if "notices" in st.session_state:
        for i in st.session_state["notices"]:
            st.success(i)
        del st.session_state["notices"]

    # Admin Top Panel
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"Welcome, {st.session_state['admin']['username']}!")
    with col2:
        if st.button("Logout", key="admin_logout"):
            del st.session_state["admin"]
            del st.session_state["is_admin"]
            st.switch_page("views/admin_login.py")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Dashboard Overview", "User Management", "Heart Patient Data"])

    with tab1:
        stats = get_user_stats()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", stats["total_users"])
        with col2:
            st.metric("Users with Heart Data", stats["users_with_heart_data"])
        with col3:
            st.metric("New This Week", "Feature coming soon")

        st.subheader("Recent Users with Heart Data")
        if stats["recent_heart_data_users"]:
            recent_df = pd.DataFrame(stats["recent_heart_data_users"])
            st.dataframe(recent_df, use_container_width=True)
        else:
            st.info("No heart data found.")

    with tab2:
        st.subheader("User Management")

        users = get_all_users()

        if users:
            users_df = pd.DataFrame(users)
            search_term = st.text_input("Search Users", placeholder="Enter username or email")

            if search_term:
                users_df = users_df[
                    users_df['username'].str.contains(search_term, case=False) | 
                    users_df['email'].str.contains(search_term, case=False)
                ]

            st.dataframe(users_df, hide_index=True, use_container_width=True)
        else:
            st.info("No users found.")

    with tab3:
        st.subheader("Heart Patient Data Management")

        heart_data = get_all_heart_patient_data()

        if heart_data:
            for idx, data in enumerate(heart_data):
                with st.expander(f"Patient: {data['username']} (ID: {data['id']})"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"*Email:* {data['email']}")
                        st.write(f"*Age:* {data['Age']}")
                        st.write(f"*Sex:* {data['Sex']}")
                        st.write(f"*Resting BP:* {data['RestingBP']} mmHg")
                        st.write(f"*Cholesterol:* {data['Cholesterol']} mg/dL")

                        risk = data.get('risk_percentage', None)
                        if risk is not None:
                            if risk >= 70:
                                st.error(f"*Risk %:* {risk}% 🚨 High Risk!")
                            else:
                                st.info(f"*Risk %:* {risk}%")
                        else:
                            st.warning("*Risk %:* Not Analyzed Yet")

                    with col2:
                        if data['sos_emergency_mail']:
                            if st.button(f"Send SOS Email", key=f"sos_{data['id']}"):
                                if send_sos_email(data['sos_emergency_mail'], data):
                                    st.success(f"SOS email sent to {data['sos_emergency_mail']}!")
                                else:
                                    st.error("Failed to send SOS email.")
        else:
            st.info("No heart patient data found.")
