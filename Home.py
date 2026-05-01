import streamlit as st
import pathlib
import base64
from pathlib import Path
from utils import load_css, get_base64_image  # Import utility functions
from dotenv import load_dotenv
import os

# Must be the first Streamlit command
st.set_page_config(
    page_title="Korean Quest",
    page_icon="🌸",
    layout="centered"
)

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir.endswith('pages'):
    # We're in a page file, go up one level
    project_root = os.path.dirname(current_dir)
else:
    # We're in the root directory
    project_root = current_dir

load_dotenv(override=True)

css_path = os.path.join(project_root, "assets", "styles.css")
load_css(css_path)

# st.write(f"CSS Path: {css_path}")
# st.write(f"File exists: {os.path.exists(css_path)}")

# Custom CSS specific to landing page
st.markdown("""
<style>
    /* Center everything vertically */
    .main {
        display: flex;
        align-items: center;
        min-height: 80vh;
    }
            
    .navbar-row {
        max-width: 1000px;
        margin: 0 auto 10px auto;
        padding: 8px 20px !important;
    }
    
    .nav-title {
        font-size: 24px !important;  /* Slightly smaller */
        white-space: nowrap;
    }
    
    /* Hero section */
    .hero {
        text-align: center;
        padding: 2rem;
        background: rgba(255, 245, 245, 0.3);
        backdrop-filter: blur(8px);
        border-radius: 40px;
        margin: 2rem auto;
        max-width: 800px;
    }
    
    .hero h1 {
        font-size: 4rem;
        color: #c85f4a;
        margin-bottom: 0.5rem;
    }
    
    .hero h2 {
        font-size: 1.8rem;
        color: #5a355a;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .hero p {
        font-size: 1.2rem;
        color: #2f2f2f;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
            
    /* Section title */
    .section-title {
        text-align: center;
        color: #5a355a;
        font-size: 1.5rem;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Feature cards */
    .features {
        display: flex;
        gap: 1.5rem;
        justify-content: center;
        gap: 0.8rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        border-radius: 24px;
        padding: 1.5rem;
        width: 160px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
            
    .feature-card:hover {
        transform: translateY(-8px);
        background: rgba(255, 255, 255, 0.35);
        box-shadow: 0 12px 25px rgba(0,0,0,0.1);
    }
            
    .feature-card h3 {
        color: #c85f4a;
        margin-bottom: 0.5rem;
    }
    
    .feature-card p {
        color: #2f2f2f;
        font-size: 1.0rem;
        margin: 0;
        font-weight: 700;
        line-height: 1.3;
    }
            
    .feature-emoji {
        font-size: 2rem;
        margin-bottom: 0.3rem;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }
    
    /* CTA Buttons */
    .cta-buttons {
        width: 250px !important;
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 2rem 0;
    }
    
    .cta-buttons .stButton button {
        width: 250px !important;
        background-color: #74cc77 !important;
        color: white !important;
        font-size: 1.3rem !important;
        padding: 0.75rem 2.5rem !important;
        border-radius: 40px !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    .cta-buttons .stButton button:hover {
        background-color: #327535 !important;
        transform: scale(1.05);
    }
    
    .secondary-button .stButton button {
        background: rgba(255, 235, 235, 0.65) !important;
        color: #5a355a !important;
        font-size: 1.3rem !important;
        padding: 0.75rem 2.5rem !important;
        border-radius: 40px !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    .secondary-button .stButton button:hover {
        background: rgba(255, 225, 225, 0.8) !important;
        color: #c85f4a !important;
    }
    
    /* Mascot on landing */
    .landing-mascot {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        opacity: 0.9;
    }
    
    .landing-mascot img {
        width: 150px;
        height: auto;
        filter: drop-shadow(0 8px 16px rgba(0,0,0,0.2));
    }
            
    .landing-mascot img:hover {
        transform: rotate(-5deg) scale(1.1);
    }
            
    /* Footer */
    .footer {
        text-align: center;
        color: #5a355a;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(90, 53, 90, 0.2);
    }
    
    /* Fix Streamlit default spacing */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* Center content */
    .stApp {
        background: linear-gradient(135deg, #ff9a9e, #fad0c4, #ffd1ff);
    }
            
</style>
""", unsafe_allow_html=True)

# st.markdown('<div class="navbar-row">', unsafe_allow_html=True)

# col1, col2, col3 = st.columns([3, 1, 1])
# with col1:
#     st.markdown('<div class="nav-title">Korean Quest 🌸</div>', unsafe_allow_html=True)
# with col2:
#     if st.button("Practice", key="nav_practice_home", use_container_width=True):
#         st.switch_page("pages/1_Practice.py")
# with col3:
#     if st.button("Dashboard", key="nav_dashboard_home", use_container_width=True):
#         st.switch_page("pages/1_Dashboard.py")

# st.markdown('</div>', unsafe_allow_html=True)

# Check if user is already logged in
if "user" in st.session_state and st.session_state.user is not None:
    st.switch_page("pages/1_Practice.py")  # Go straight to practice if logged in

# Hero Section
# st.markdown("<h2>Master Korean vocabulary, one word at a time</h2>", unsafe_allow_html=True)
# st.markdown("""
# <p>
# Learn Korean with spaced repetition, track your progress, 
# and build your vocabulary with our cute and friendly learning app.
# </p>
# """, unsafe_allow_html=True)

#Hero Section with better styling
st.markdown('<div class="hero-text">', unsafe_allow_html=True)
st.markdown("<h2>🌸 Master Korean vocabulary,<br>one word at a time</h2>", unsafe_allow_html=True)  # Added flower here
st.markdown("""
<p>
Learn Korean with spaced repetition, track your progress, 
and build your vocabulary with our cute and friendly learning app.
</p>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title"><h3>🌸 Why Choose Korean Quest?</h3></div>', unsafe_allow_html=True)

# Features Section
st.markdown('<div class="features">', unsafe_allow_html=True)

# Create 4 columns for feature cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🎯 Smart Learning</h3>
        <p>Spaced repetition helps you remember</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Track Progress</h3>
        <p>Detailed stats and insights</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>🎮 Fun Practice</h3>
        <p>Cute design, engaging experience</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <h3>🚀 Free Forever</h3>
        <p>Start learning today</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# CTA Buttons
st.markdown('<div class="cta-buttons">', unsafe_allow_html=True)

cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
with cta_col2:
    inner_col1, inner_col2 = st.columns(2)
    with inner_col1:
        if st.button("🚀 Start Learning", key="start_btn", use_container_width=True):
            st.switch_page("pages/1_Login.py")
    
    with inner_col2:
        if st.button("🌸 Learn More", key="learn_btn", use_container_width=True):
            st.info("✨ More features coming soon! For now, just start learning! 😊")

st.markdown('</div>', unsafe_allow_html=True)

# Add mascot
try:
    mascot_base64 = get_base64_image("assets/download.jpg")
    st.markdown(
        f"""
        <div class="landing-mascot">
            <img src="data:image/jpeg;base64,{mascot_base64}" alt="Mascot">
        </div>
        """,
        unsafe_allow_html=True
    )
except:
    pass  # Skip if mascot image not found

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #5a355a;'>🌸 Made with love for Korean learners 🌸</p>", unsafe_allow_html=True)