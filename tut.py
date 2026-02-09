import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import json, random

from auth import auth_ui, logout_button


from dotenv import load_dotenv, dotenv_values
load_dotenv(override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("URL:", SUPABASE_URL)
print("KEY:", SUPABASE_KEY)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if "user" not in st.session_state:
    st.session_state.user = None


# If not logged in, show auth page:
if "user" not in st.session_state or st.session_state.user is None:
    auth_ui()
    st.stop()

user_id = st.session_state.user.id

st.title("Korean Language Exercise")

with open("korean_words.json", "r", encoding="utf-8") as f:
    words = json.load(f)

if "current_word" not in st.session_state:
    st.session_state.current_word = random.choice(words)

if "show_next" not in st.session_state:
    st.session_state.show_next = False  # Hidden first

word = st.session_state.current_word
print("this is a randomly selected word from the json file of korean words: ", word.get("korean"))

difficulty = word.get("difficulty")

st.write("Translate the following word:", word.get("korean"))
st.write("Difficulty Level:", difficulty)

answer = st.text_input("enter english translation here:")

def add_response(user_id, word, user_answer, difficulty, correct):
    supabase.table("Responses").insert({
        "user_id": user_id,
        "word": word,
        "user_answer": user_answer,
        "correct": correct,
        "response_time": 5,  # Placeholder for response time
        "difficulty": difficulty
    }).execute()

if st.button("Submit"):
    correct = (answer.strip().lower() == word.get("english").strip().lower())

    if answer:
        add_response(user_id=user_id, word=word.get("korean"), user_answer=answer, difficulty=difficulty, correct=correct)
    else:
        st.error("Please enter an answer before submitting.")

    st.write("Thank you for your submission!")
    # st.switch_page("pages/1_Answer.py")

    if correct:
        st.success("Correct!")
    else:
        st.error(f"Incorrect! The correct answer is: {word.get('english')}")

    st.session_state.show_next = True  # Show the next button

def get_new_word(words, current_word):
    new_word = random.choice(words)
    while new_word == current_word:
        new_word = random.choice(words)
    return new_word

if st.session_state.show_next:
    if st.button("Next Word"):
        st.session_state.current_word = get_new_word(words, st.session_state.current_word)
        st.session_state.show_next = False
        st.rerun()

if st.button("Log Out"):
    logout_button()
    st.rerun()


def load_responses():
    responses = supabase.table("Responses").select("*").execute()
    return responses.data





# with st.form(key="my_form"):
    
#     name = st.text_input("Enter your name:")
#     age = st.number_input("Enter your age:")

#     print(name, age)
#     st.form_submit_button("Submit")
