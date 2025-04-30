import streamlit as st
import bcrypt
from db import get_db_connection

def register_user(username, email, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Use dictionary=True to fetch rows as dict

    username = username.strip()  # Remove leading/trailing spaces
    email = email.strip()

    # Check if username or email already exists
    cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
    existing_user = cursor.fetchone()  # Fetch one matching row
    
    if existing_user:
        st.warning(f"Debug: Found existing user -> {existing_user}")  # Debugging line
        return "Username or Email already exists!"

    # Hash password before storing
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Insert new user
    cursor.execute(
    "INSERT INTO users (username, email, password, is_admin) VALUES (%s, %s, %s, %s)",
    (username, email, hashed_password.decode(),0)
)  
    conn.commit()
    conn.close()
    return "success"

if "user" in st.session_state:
    st.session_state["notices"] = ["You are already logged in"]
    st.switch_page("pages/dashboard.py")

st.title("🆕 Create an Account")

username = st.text_input("Choose a Username")
email = st.text_input("Email")
password = st.text_input("Create Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

if st.button("Sign Up"):
    if password != confirm_password:
        st.error("Passwords do not match!")
    else:
        result = register_user(username, email, password)
        if result == "success":
            st.success("Account created successfully! Please log in.")
            if st.button("Go to login page"):
                st.switch_page("pages/login.py")
        else:
            st.error(result)
