import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def auth_ui():
    """Display login/signup UI - used by login page"""
    st.header("Login / Signup")

    # Disable autocorrect and autocapitalize for email on mobile
    email = st.text_input(
        "Email", 
        placeholder="email@example.com",
        autocomplete="email",
        key="email_input"
    )
    
    password = st.text_input(
        "Password", 
        type="password",
        placeholder="Enter your password",
        autocomplete="current-password",
        key="password_input"
    )
    st.caption("Note: Password must be at least 6 characters long for new accounts.")
    if st.button("Sign Up"):
        if email and password:
            try:
                # Clean the email (remove any whitespace and lowercase)
                email_clean = email.strip().lower()
                
                response = supabase.auth.sign_up({
                    "email": email_clean, 
                    "password": password
                })
                
                if response.user and not response.user.email_confirmed_at:
                    st.success("""
                    ✨ **Check your email!** ✨
                    
                    We've sent a verification link to your email address.
                    Click the link in the email to activate your account.
                    
                    After confirming, you can log in below.
                    """)
                else:
                    st.success("Account created! You can now log in.")
                    
            except Exception as e:
                st.error(f"Sign up error: {str(e)}")
        else:
            st.warning("Please enter both email and password")

    # Log In button
    if st.button("Log In"):
        if email and password:
            try:
                # Clean the email (remove any whitespace and lowercase)
                email_clean = email.strip().lower()
                
                session = supabase.auth.sign_in_with_password(
                    {"email": email_clean, "password": password}
                )
                st.session_state.user = session.user
                st.session_state.just_logged_in = True
                st.rerun()
            except Exception as e:
                st.error("Invalid email or password")
        else:
            st.warning("Please enter both email and password")

def logout_button():
    """Log out and completely wipe session - FIXED VERSION"""
    supabase.auth.sign_out()
    
    # CRITICAL: Clear ALL session state keys
    keys_to_delete = ['user', 'start_time', 'current_word', 'attempts', 
                      'show_next', 'last_correct', 'last_response_time',
                      'word_progress', 'answer_input', 'streak_celebrated',
                      'last_login_date', 'first_load', 'login_success',
                      'nav1', 'nav2']
    
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    
    # Also try to clear any remaining keys
    remaining_keys = list(st.session_state.keys())
    for key in remaining_keys:
        if key not in ['_is_running', '_script_run_once']:  # Keep Streamlit internal keys
            del st.session_state[key]

    st.rerun()

    print("Logout - Session keys after cleanup:", list(st.session_state.keys()))

def deactivate_account(user_id):
    """Remove user data but keep anonymous stats (no admin keys needed)"""
    try:
        # 1. Delete user's responses
        supabase.table("Responses").delete().eq("user_id", user_id).execute()
        
        # 2. Delete user's word progress
        supabase.table("WordProgress").delete().eq("user_id", user_id).execute()
        
        # 3. Sign out
        supabase.auth.sign_out()
        
        # 4. Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
            
        return True, "Account data deleted successfully"
        
    except Exception as e:
        return False, str(e)