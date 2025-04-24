import streamlit as st

# 1) Global page configuration (must be first Streamlit call) 📑
st.set_page_config(
    page_title="Heartistry Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2) Declare each page under `pages/` with st.Page; mark `landing.py` as default 🏠
page_landing         = st.Page("pages/landing.py",       title="Welcome",           icon="🏠", default=True)
page_login           = st.Page("pages/login.py",         title="User Login",        icon="🔒")
page_signup          = st.Page("pages/signup.py",        title="Sign Up",           icon="✍️")
page_dashboard       = st.Page("pages/dashboard.py",     title="Dashboard",         icon="📊")
page_analysis        = st.Page("pages/analysis.py",      title="Analysis",          icon="🔬")
page_forgot_password = st.Page("pages/forgot_password.py", title="Forgot Password",  icon="❓")
page_admin_login     = st.Page("pages/admin_login.py",   title="Admin Login",       icon="🛡️")
page_admin_dashboard = st.Page("pages/admin_dashboard.py", title="Admin Panel",      icon="⚙️")

# 3) Build sidebar navigation in the desired order 🚀
navigator = st.navigation([
    page_landing,
    page_login,
    page_signup,
    page_dashboard,
    page_analysis,
    page_forgot_password,
    page_admin_login,
    page_admin_dashboard,
])

# 4) Run the selected page
navigator.run()