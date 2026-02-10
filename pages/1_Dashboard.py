import streamlit as st
from supabase import create_client
import os
import pandas as pd

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_responses(user_id):
    res = supabase.table("Responses").select("*").eq("user_id", user_id).execute()
    return pd.DataFrame(res.data)

st.title("Dashboard")

df = load_responses(st.session_state.user.id)
st.write(df.head(10))