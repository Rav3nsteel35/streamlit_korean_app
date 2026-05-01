# utils.py
import base64
from pathlib import Path
import streamlit as st
import time

def get_base64_image(image_path):
    """Convert image to base64 string for embedding in HTML"""
    data = Path(image_path).read_bytes()
    return base64.b64encode(data).decode()

def load_css(file_path):
    """Load CSS file into Streamlit"""
    import streamlit as st
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def show_loading(message="Loading...", duration=0.5):
    """Simple loading spinner"""
    with st.spinner(message):
        time.sleep(duration)