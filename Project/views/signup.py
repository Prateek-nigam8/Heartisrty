import streamlit as st
import bcrypt
import re
from db import get_db_connection

def register_user(username, email, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Use dictionary=True to fetch rows as dict

    username = username.strip().lower()  # Remove leading/trailing spaces and lowercase
    email = email.strip().lower()  # Remove leading/trailing spaces and lowercase

    # Check if username or email already exists
    cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
    existing_user = cursor.fetchone()  # Fetch one matching row
    
    if existing_user:        
        return "Username or Email already exists!"

    # Hash password before storing
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Insert new user
    cursor.execute(
        "INSERT INTO users (username, email, password, is_admin) VALUES (%s, %s, %s, %s)",
        (username, email, hashed_password.decode(), 0)
    )  
    conn.commit()
    conn.close()
    return "success"

if "user" in st.session_state:
    st.session_state["notices"] = ["You are already logged in"]
    st.switch_page("views/dashboard.py")

st.title("🆕 Create an Account")

username = st.text_input("Choose a Username")
email = st.text_input("Email")
password = st.text_input("Create Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

if st.button("Sign Up"):
    username_stripped = username.strip()
    email_stripped = email.strip()
    error = False

    if not username_stripped:
        st.error("Username cannot be empty")
        error = True
    elif len(username_stripped) < 3:
        st.error("Username must be at least 3 characters")
        error = True

    # Email regex validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email_stripped:
        st.error("Email cannot be empty")
        error = True
    elif not re.match(email_pattern, email_stripped):
        st.error("Invalid email address")
        error = True

    if not password:
        st.error("Password cannot be empty")
        error = True
    elif len(password) < 6:
        st.error("Password must be at least 6 characters")
        error = True
    elif password != confirm_password:
        st.error("Passwords do not match")
        error = True

    if not error:
        result = register_user(username, email, password)
        if result == "success":
            st.success("Account created successfully! Please log in.")
            if st.button("Go to login page"):
                st.switch_page("views/login.py")
        else:
            st.error(result)