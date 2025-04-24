import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db import get_db_connection

def get_user_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get total number of users
    cursor.execute("SELECT COUNT(*) as total_users FROM users WHERE is_admin=0")
    total_users = cursor.fetchone()["total_users"]
    
    # Get users with heart data
    cursor.execute("SELECT COUNT(DISTINCT u.id) as users_with_heart_data FROM users u JOIN heart_patient_data h ON u.id = h.user_id")
    users_with_heart_data = cursor.fetchone()["users_with_heart_data"]
    
    # Get recent users with heart data
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
    """Fetch all non-admin users from the database"""
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
    # Email configuration
    sender_email = "patrick8200402@gmail.com"
    password = "dulg zfxo qebd thbe"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = "Urgent: Potential Heart Health Concern"
    
    # Compose email body
    body = f"""
    <html>
    <body>
        <h2>Urgent Medical Attention Required</h2>
        <p>Based on the recent health assessment, there are potential heart health concerns that require immediate attention.</p>
        
        <h3>Patient Details:</h3>
        <ul>
            <li><strong>Age:</strong> {patient_data.get('Age', 'N/A')}</li>
            <li><strong>Sex:</strong> {patient_data.get('Sex', 'N/A')}</li>
            <li><strong>Resting Blood Pressure:</strong> {patient_data.get('RestingBP', 'N/A')} mmHg</li>
            <li><strong>Cholesterol:</strong> {patient_data.get('Cholesterol', 'N/A')} mg/dL</li>
            <li><strong>Chest Pain Type:</strong> {patient_data.get('ChestPainType', 'N/A')}</li>
        </ul>
        
        <p>Please consult with a healthcare professional as soon as possible.</p>
        
        <p>This is an automated message from Heartistry - Your Cardiovascular Wellness Companion.</p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(body, 'html'))
    
    try:
        # Connect to Gmail's SMTP server
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


if "is_admin" not in st.session_state or not st.session_state["is_admin"]:
    st.error("Unauthorized access!")
    if st.button("Go to Admin Login"):
        st.switch_page("pages/admin_login.py")
else:

    st.title("👑 Admin Dashboard")

    if "notices" in st.session_state:
        for i in st.session_state["notices"]:
            st.success(i)
            del st.session_state["notices"]
    # Admin Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"Welcome, {st.session_state['admin']['username']}!")
    with col2:
        if st.button("Logout", key="admin_logout"):
            del st.session_state["admin"]
            del st.session_state["is_admin"]
            st.switch_page("pages/admin_login.py")

    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["Dashboard Overview", "User Management", "Heart Patient Data"])

    with tab1:
        # Dashboard Overview Tab
        stats = get_user_stats()
        
        # Display stats in cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", stats["total_users"])
        with col2:
            st.metric("Users with Heart Data", stats["users_with_heart_data"])
        with col3:
            st.metric("New This Week", "Feature coming soon")
        
        # Recent users with heart data
        st.subheader("Recent Users with Heart Data")
        if stats["recent_heart_data_users"]:
            recent_df = pd.DataFrame(stats["recent_heart_data_users"])
            st.dataframe(recent_df, use_container_width=True)
        else:
            st.info("No heart data found")

    with tab2:
        # User Management Tab
        st.subheader("User Management")
        
        # Get all users
        users = get_all_users()
        
        if users:
            # Convert to DataFrame for display
            users_df = pd.DataFrame(users)
            
            # Option to sort or search users
            search_term = st.text_input("Search Users", placeholder="Enter username or email")
            
            # Apply search filter
            if search_term:
                users_df = users_df[
                    users_df['username'].str.contains(search_term, case=False) | 
                    users_df['email'].str.contains(search_term, case=False)
                ]
            
            # Display users
            st.dataframe(users_df, hide_index=True, use_container_width=True)
        else:
            st.info("No users found")

    with tab3:
        # Heart Patient Data Tab
        st.subheader("Heart Patient Data Management")
        
        # Get all heart patient data
        heart_data = get_all_heart_patient_data()
        
        if heart_data:
            # Convert to DataFrame for better display
            heart_data_df = pd.DataFrame(heart_data)
            
            # Display heart data with actions
            for idx, data in enumerate(heart_data):
                with st.expander(f"Patient: {data['username']} (ID: {data['id']})"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"*Email:* {data['email']}")
                        st.write(f"*Age:* {data['Age']}")
                        st.write(f"*Sex:* {data['Sex']}")
                        st.write(f"*Resting BP:* {data['RestingBP']} mmHg")
                        st.write(f"*Cholesterol:* {data['Cholesterol']} mg/dL")
                    with col2:
                        # Send SOS Email button
                        if data['sos_emergency_mail']:
                            if st.button(f"Send SOS Email", key=f"sos_{data['id']}"):
                                if send_sos_email(data['sos_emergency_mail'], data):
                                    st.success(f"SOS email sent to {data['sos_emergency_mail']}!")
                                else:
                                    st.error("Failed to send SOS email.")
        else:
            st.info("No heart patient data found")