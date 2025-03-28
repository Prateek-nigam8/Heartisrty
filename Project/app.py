import streamlit as st
from pages import landing, login, signup, dashboard, forgot_password, admin_login, admin_dashboard

# Set page configuration
st.set_page_config(page_title="Heartistry - The Art of Cardiovascular Wellness", layout="wide")

# Navigation Handler
if "page" not in st.session_state:
    st.session_state["page"] = "landing"

def go_to_page(page_name):
    st.session_state["page"] = page_name
    st.rerun()

# Render pages dynamically
if st.session_state["page"] == "landing":
    landing.show(go_to_page)
elif st.session_state["page"] == "login":
    login.show(go_to_page)
elif st.session_state["page"] == "signup":
    signup.show(go_to_page)
elif st.session_state["page"] == "dashboard":
    dashboard.show(go_to_page)
elif st.session_state["page"] == "forgot_password":
    forgot_password.show(go_to_page)
# Admin routes
elif st.session_state["page"] == "admin_login":
    admin_login.show(go_to_page)
elif st.session_state["page"] == "admin_dashboard":
    admin_dashboard.show(go_to_page)