import streamlit as st
from tut import load_responses

st.title("Korean Language Exercise")

Responses = load_responses()
st.write("Here are all your previous responses:")
for response in Responses:
    st.write(response)

back = st.button("Go Back to Question")

if back:
    st.switch_page("tut.py")