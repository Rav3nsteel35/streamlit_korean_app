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

col1, col2, col3 = st.columns(3)

accuracy = df['correct'].mean() * 100
avrg_res_time = df['response_time'].mean()
attempts = df['attempt_number'].mean()


with col1:
    col1.metric("Accuracy", f"{accuracy:.1f}%")
with col2:
    col2.metric("Avg. Response Time", f"{avrg_res_time:.2f}s")
with col3:
    col3.metric("Avg. Attempts", f"{attempts:.1f}")
