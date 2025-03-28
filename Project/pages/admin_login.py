import streamlit as st
from db import get_db_connection
import bcrypt

def check_admin_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Query to check if the user exists and is an admin
    query = "SELECT * FROM users WHERE username=%s AND is_admin=1"
    cursor.execute(query, (username,))
    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    if admin and bcrypt.checkpw(password.encode(), admin["password"].encode()):
        return admin
    return None

def show(go_to_page):
    st.title("👑 Admin Login")
    st.markdown("Access restricted to authorized personnel only")
    
    with st.form("admin_login_form"):
        username = st.text_input("Admin Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            admin = check_admin_login(username, password)
            if admin:
                st.success("✅ Admin login successful! Redirecting...")
                st.session_state["admin"] = admin
                st.session_state["is_admin"] = True
                go_to_page("admin_dashboard")
            else:
                st.error("❌ Invalid admin credentials or insufficient privileges!")
                
    st.markdown("---")
    if st.button("Return to Main Site"):
        go_to_page("landing")