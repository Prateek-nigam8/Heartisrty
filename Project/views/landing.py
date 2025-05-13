import streamlit as st

st.title("❤️ Heartistry: The Art of Cardiovascular Wellness")
st.markdown("""
    ### 🏥 Revolutionizing Cardiovascular Wellness with Technology  
    Heart disease is one of the leading causes of mortality worldwide, making early detection and proactive monitoring crucial.
    **Heartistry** is an innovative tool that bridges the gap between **technology and healthcare**, leveraging advanced
    **machine learning algorithms** to assess heart disease risk based on health data.
""")

st.subheader("✨ Key Features of Heartistry")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    - **🩺 Personal Risk Assessment**: Predict cardiovascular risks based on health metrics.
    - **📊 Live Body Monitoring**: Real-time insights for proactive health tracking.
    - **📈 Behavior Analysis**: Understand how lifestyle choices impact heart health.
    """)

with col2:
    st.markdown("""
    - **🚨 Emergency Alerts**: Get rapid notifications for critical situations.
    - **📅 Progress Tracking**: Monitor your heart health improvements over time.
    - **🌍 Community Integration**: Connect with others to share experiences and insights.
    """)

st.markdown("---")
st.markdown("**💡 Start Your Heart Health Journey Today!**")

if st.button("Get Started 🚀"):
    st.switch_page("views/login.py")
    
# Add a small admin access link at the bottom
st.markdown("---")
col1, col2, col3 = st.columns([3, 1, 1])
with col3:
    if st.button("Admin Access", key="admin_access"):
        st.switch_page("views/admin_login.py")