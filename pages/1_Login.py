import streamlit as st
from auth_functions import auth_ui  # Import from new file
import pathlib
import time
from utils import load_css
from utils import load_css, show_loading
from dotenv import load_dotenv
import os

st.set_page_config(page_title="Login - Korean Quest", page_icon="🌸", layout="centered")

# Get the correct path for CSS
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir.endswith('pages'):
    project_root = os.path.dirname(current_dir)
else:
    project_root = current_dir

load_dotenv(override=True)

# Load CSS
css_path = os.path.join(project_root, "assets", "styles.css")
load_css(css_path)

# Check if already logged in
if "user" in st.session_state and st.session_state.user is not None:
    st.switch_page("pages/1_Practice.py")

st.markdown('<div class="back-button">', unsafe_allow_html=True)
if st.button("← Back to Home", key="back_to_landing"):
    st.switch_page("Home.py")
st.markdown('</div>', unsafe_allow_html=True)

# Inject inline CSS for login page buttons
st.markdown("""
<style>
    /* Ensure the entire login container is full width */
    .login-page {
        width: 100%;
    }
    /* Force the form (if any) to be full width */
    .login-page form {
        width: 100% !important;
    }
    /* Make the button container full width */
    .login-page .stButton,
            
    .login-page div[data-testid="stFormSubmitButton"] {
        width: 500px !important;
        display: block !important;
    }
            
    /* Make the actual button fill its container */
    .login-page .stButton button,
    .login-page button {
        width: 500px !important;
        display: block !important;
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.markdown('<div class="login-page">', unsafe_allow_html=True)

# Title
st.markdown('<h1 class="login-title">🌸 Korean Quest</h1>', unsafe_allow_html=True)
st.markdown('<p class="login-subtitle">Sign in to continue your journey</p>', unsafe_allow_html=True)

# Auth UI
auth_ui()

st.markdown('</div>', unsafe_allow_html=True)  # Close login-page

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #5a355a; font-size: 0.9rem;'>🌸 Ready to master Korean? 🌸</p>", unsafe_allow_html=True)