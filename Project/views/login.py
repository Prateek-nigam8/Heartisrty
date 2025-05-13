import streamlit as st
from db import get_db_connection
import bcrypt

def check_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE username=%s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
        return user  
    return None  

if "user" in st.session_state:
    st.session_state["notices"] = ["You are already logged in"]
    st.switch_page("views/dashboard.py")

st.title("🔐 Login to Heartistry")

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

    if submitted:
        user = check_login(username, password)
        if user:
            st.success("✅ Login successful! Redirecting...")
            st.session_state["user"] = user  
            if "admin" in st.session_state: del st.session_state["admin"]
            if "is_admin" in st.session_state: del st.session_state["is_admin"]
            st.switch_page("views/dashboard.py")
        else:
            st.error("❌ Invalid username or password!")

st.write("")

col1, col2 = st.columns([1, 1])

with col1:
    st.write("Don't have an account?")
    if st.button("Create an Account", use_container_width=True):
        st.switch_page("views/signup.py")

with col2:
    st.write("Forgot your password?")
    if st.button("Reset Password", use_container_width=True):
        st.switch_page("views/forgot_password.py")
