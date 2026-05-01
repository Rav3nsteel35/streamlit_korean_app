import streamlit as st
from auth_functions import logout_button
from auth_functions import deactivate_account
import pathlib
from utils import load_css
from datetime import datetime
import pandas as pd
from time import time
import os
from dotenv import load_dotenv


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

if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("Home.py")
    st.stop()

user_email = st.session_state.user.email
username = user_email.split("@")[0] if user_email else "User"
user_id = st.session_state.user.id
user_member_since = st.session_state.user.created_at.date()  # Extract date part

# Fetch user stats from Supabase
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get user's practice data
responses = supabase.table("Responses").select("*").eq("user_id", user_id).execute()
word_progress = supabase.table("WordProgress").select("*").eq("user_id", user_id).execute()

# Calculate stats
total_attempts = len(responses.data) if responses.data else 0
unique_words = len(set([r['word'] for r in responses.data])) if responses.data else 0
correct_answers = sum([1 for r in responses.data if r['correct']]) if responses.data else 0
accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0

if responses.data:
    dates = [r['created_at'] for r in responses.data]
    first_practice = min(dates)[:10]
    last_practice = max(dates)[:10]
    days_active = (datetime.now() - datetime.fromisoformat(first_practice)).days
else:
    first_practice = "N/A"
    last_practice = "N/A"
    days_active = 0


st.markdown('<div class="navbar-row">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([3, 1.2, 1.5, 1.2])
with col1:
    st.markdown('<div class="nav-title">Korean Quest 🌸</div>', unsafe_allow_html=True)
with col2:
    if st.button("Practice", key="nav1", use_container_width=True):
        st.switch_page("pages/1_Practice.py")  # This is the current page
with col3:
    if st.button("Dashboard", key="nav2", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")
with col4:
    if st.button("Profile", key="nav3", use_container_width=True):
        st.switch_page("pages/1_Profile.py")

# st.markdown('<h1 class="custom-title">K Kards</h1>', unsafe_allow_html=True)

# Profile Header with avatar placeholder
col1, col2 = st.columns([1, 3])
with col1:
    # Simple avatar circle with first letter of email
    first_letter = user_email[0].upper() if user_email else "?"
    st.markdown(f"""
    <div style="
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ff9a9e, #c85f4a);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        color: white;
        font-weight: bold;
        margin: 0 auto;
    ">{first_letter}</div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="padding: 1rem 0;">
        <h2 style="color: #c85f4a; margin: 0;">{username}</h2>
        <p style="color: #5a355a;">Member since: {first_practice}</p>
        <p style="color: #5a355a;">Days active: {days_active}</p>
    </div>
    """, unsafe_allow_html=True)

# Display user info
st.markdown(f"""
<div style="background: rgba(255, 245, 245, 0.45); 
            backdrop-filter: blur(8px); 
            border-radius: 30px; 
            padding: 2rem; 
            margin: 1rem 0;">
    <h3 style="color: #c85f4a;">Account Information</h3>
    <p><strong>Email:</strong> {user_email}</p>
    <p><strong>Member since:</strong> {user_member_since}</p>
</div>
""", unsafe_allow_html=True)

# Account Stats Section
st.markdown("""
<div style="
    background: rgba(255, 245, 245, 0.45);
    backdrop-filter: blur(8px);
    border-radius: 30px;
    padding: 1.5rem;
    margin: 1.5rem 0;
">
    <h3 style="color: #c85f4a; margin-top: 0;">📊 Learning Statistics</h3>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Attempts", total_attempts)
with col2:
    st.metric("Words Learned", unique_words)
with col3:
    st.metric("Accuracy", f"{accuracy:.1f}%")
with col4:
    st.metric("Days Active", days_active)

st.markdown('</div>', unsafe_allow_html=True)

st.caption("💡 Tip: Those little popups when hovering are just your browser's way of showing it recognizes text. Nothing to worry about!")

# Achievement Badges
st.markdown("""
<div style="
    background: rgba(255, 245, 245, 0.45);
    backdrop-filter: blur(8px);
    border-radius: 30px;
    padding: 1.5rem;
    margin: 1.5rem 0;
">
    <h3 style="color: #c85f4a; margin-top: 0;">🏆 Achievements</h3>
""", unsafe_allow_html=True)

# Calculate achievements
badges = []

if total_attempts >= 10:
    badges.append("🌱 Beginner")
if total_attempts >= 100:
    badges.append("📚 Dedicated Learner")
if accuracy >= 90 and total_attempts >= 50:
    badges.append("🎯 Master")
if accuracy >= 80 and total_attempts >= 25:
    badges.append("🎯 Sharp Shooter")
if unique_words >= 20:
    badges.append("🗣️ Vocabulary Builder")
if days_active >= 7:
    badges.append("🔥 Week Warrior")
if days_active >= 30:
    badges.append("⭐ Monthly Master")

if badges:
    badge_html = ""
    for badge in badges:
        badge_html += f'<span style="background: #c85f4a; color: white; padding: 0.5rem 1rem; border-radius: 30px; margin: 0.25rem; display: inline-block;">{badge}</span>'
    st.markdown(f'<div style="margin: 1rem 0;">{badge_html}</div>', unsafe_allow_html=True)
else:
    st.info("Keep practicing to earn achievements!")

st.markdown('</div>', unsafe_allow_html=True)

# ===== FEEDBACK SECTION =====
# Feedback form
with st.form("feedback_form"):
    feedback_type = st.selectbox(
        "What kind of feedback?",
        ["🐛 Bug Report", "💡 Feature Idea", "📝 Word Suggestion", "❤️ General Feedback"]
    )
    
    feedback_message = st.text_area(
        "Your feedback",
        placeholder="e.g., 'The streak counter is motivating!' or 'Can you add more food words?' or 'The buttons on login page are not full width on mobile...'",
        height=150
    )
    
    # Optional: rating
    rating = st.slider("How would you rate your experience?", 1, 5, 5, help="1 = needs work, 5 = love it!")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        submitted = st.form_submit_button("Send Feedback 🌸", use_container_width=True)
    
    if submitted:
        if feedback_message:
            # Option 1: Email (you can set up a simple email notification)
            # For now, we'll just save to session state and show confirmation
            st.session_state.last_feedback = {
                "type": feedback_type,
                "message": feedback_message,
                "rating": rating,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.success("✨ Thanks for your feedback! It really helps me improve the app.")
            st.balloons()
            
            # Option 2: If you want to save to Supabase (optional)
            # You'd need to create a feedback table first
        #     """
        #     try:
        #         supabase.table("Feedback").insert({
        #             "user_id": user_id,
        #             "user_email": user_email,
        #             "feedback_type": feedback_type,
        #             "message": feedback_message,
        #             "rating": rating,
        #             "created_at": datetime.now().isoformat()
        #         }).execute()
        #         st.success("✨ Thanks for your feedback!")
        #     except Exception as e:
        #         st.error(f"Could not save feedback: {e}")
        #     """
        # else:
        #     st.warning("Please write something before sending!")

# Optional: Show last feedback if exists
if "last_feedback" in st.session_state:
    with st.expander("📬 Your last feedback (for reference)"):
        st.write(f"**Type:** {st.session_state.last_feedback['type']}")
        st.write(f"**Message:** {st.session_state.last_feedback['message']}")
        st.write(f"**Rating:** {'⭐' * st.session_state.last_feedback['rating']}")
        st.caption(f"Sent: {st.session_state.last_feedback['timestamp']}")



# Logout button
if st.button("Log Out", use_container_width=True):
    logout_button()

# Optional: Add stats or settings
with st.expander("⚙️ Account Settings"):
    st.markdown("### Change Password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Update Password"):
        if new_password and new_password == confirm_password:
            try:
                supabase.auth.update_user({"password": new_password})
                st.success("Password updated successfully!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Passwords don't match or are empty")
    
# st.markdown("---")
# st.markdown("### Danger Zone")

# if st.button("✅ Yes, Delete Everything", use_container_width=True):
#     with st.spinner("Deleting your data..."):
#         success, message = deactivate_account(user_id)  # Use deactivate_account instead
#         if success:
#             st.success("Your data has been deleted. Redirecting...")
#             # time.sleep(2)
#             st.switch_page("Home.py")
#         else:
#             st.error(f"Error: {message}")
#             st.session_state.show_final_delete = False


st.markdown("---")
st.markdown('<p class="footer">Made with ❤️ by Merv</p>', unsafe_allow_html=True)