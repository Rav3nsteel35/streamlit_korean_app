import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load .env inside this file too
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if "user" not in st.session_state:
    st.session_state.user = None

def auth_ui():
    st.header("Login / Signup")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        try:
            supabase.auth.sign_up({"email": email, "password": password})
            st.success("Account created! Check your email.")
        except Exception as e:
            st.error(str(e))

    if st.button("Log In"):
        try:
            session = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            st.session_state.user = session.user
            st.rerun()
        except Exception as e:
            st.error(str(e))

def logout_button():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()
