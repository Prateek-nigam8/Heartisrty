import streamlit as st

# 1) Global page configuration (must be first Streamlit call) 📑
st.set_page_config(
    page_title="Heartistry Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2) Declare each page under `views/` with st.Page; mark `landing.py` as default 🏠
page_landing         = st.Page("views/landing.py",       title="Welcome",           icon="🏠", default=True)
page_login           = st.Page("views/login.py",         title="User Login",        icon="🔒")
page_signup          = st.Page("views/signup.py",        title="Sign Up",           icon="✍️")
page_dashboard       = st.Page("views/dashboard.py",     title="Dashboard",         icon="📊")
page_analysis        = st.Page("views/analysis.py",      title="Analysis",          icon="🔬")
page_forgot_password = st.Page("views/forgot_password.py", title="Forgot Password",  icon="❓")
page_admin_login     = st.Page("views/admin_login.py",   title="Admin Login",       icon="🛡️")
page_admin_dashboard = st.Page("views/admin_dashboard.py", title="Admin Panel",      icon="⚙️")

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