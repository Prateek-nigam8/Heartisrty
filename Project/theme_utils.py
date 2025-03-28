import streamlit as st

def get_theme_toggle():
    """Returns the theme toggle component and initializes theme state if needed"""
    # Initialize session state for theme if it doesn't exist
    if 'theme' not in st.session_state:
        st.session_state.theme = "light"
    
    # Create columns for right-aligned toggle
    cols = st.columns([6, 1])
    with cols[1]:
        if st.button("🌓" if st.session_state.theme == "light" else "☀️", key="theme_toggle"):
            # Toggle theme
            if st.session_state.theme == "light":
                st.session_state.theme = "dark"
            else:
                st.session_state.theme = "light"
            st.rerun()

def apply_theme_css():
    """Apply the CSS for the current theme"""
    if st.session_state.theme == "dark":
        # Dark theme
        st.markdown("""
            <style>
            .stApp {
                background-color: #121212;
                color: #f0f0f0;
            }
            .stButton button {
                background-color: #2e2e2e;
                color: #f0f0f0;
                border: 1px solid #444;
            }
            .stTextInput input, .stNumberInput input {
                background-color: #2e2e2e;
                color: #f0f0f0;
                border: 1px solid #444;
            }
            .stSelectbox, .stMultiselect {
                background-color: #2e2e2e;
                color: #f0f0f0;
            }
            .stTab, .stTabContent {
                background-color: #2e2e2e !important;
                color: #f0f0f0 !important;
            }
            .stDataFrame {
                background-color: #2e2e2e;
            }
            .stExpander {
                background-color: #2e2e2e;
                border: 1px solid #444;
            }
            .stSuccess {
                background-color: #105021;
                color: #f0f0f0;
            }
            .stError {
                background-color: #5e1515;
                color: #f0f0f0;
            }
            .stWarning {
                background-color: #5e4a15;
                color: #f0f0f0;
            }
            .stInfo {
                background-color: #153a5e;
                color: #f0f0f0;
            }
            /* Specific styling for Heartistry */
            h1, h2, h3, h4, h5, h6 {
                color: #f0f0f0;
            }
            .main .block-container {
                background-color: #121212;
            }
            div[data-testid="stForm"] {
                background-color: #1e1e1e;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #333;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        # Light theme (default)
        st.markdown("""
            <style>
            .stApp {
                background-color: #ffffff;
                color: #000000;
            }
            /* Reset any dark mode specific styles */
            h1, h2, h3, h4, h5, h6 {
                color: inherit;
            }
            .main .block-container {
                background-color: #ffffff;
            }
            div[data-testid="stForm"] {
                background-color: #f7f7f7;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
            </style>
        """, unsafe_allow_html=True)