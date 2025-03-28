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

def show(go_to_page):
    st.title("🔐 Login to Heartistry")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Login", key="login_button", use_container_width=True):
            user = check_login(username, password)
            if user:
                st.success("✅ Login successful! Redirecting...")
                st.session_state["user"] = user  
                go_to_page("dashboard")
            else:
                st.error("❌ Invalid username or password!")
    
    st.write("")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("Don't have an account?")
        if st.button("Create an Account", use_container_width=True):
            go_to_page("signup")
    
    with col2:
        st.write("Forgot your password?")
        if st.button("Reset Password", use_container_width=True):
            go_to_page("forgot_password")