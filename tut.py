import time
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

    st.session_state.start_time = time.time()    # Start the timer when the word is first displayed

    st.session_state.attempts = 0  # Initialize attempts for the current word

if "show_next" not in st.session_state:
    st.session_state.show_next = False  # Hidden at first

if 'attempts' not in st.session_state:
    st.session_state.attempts = 0

word = st.session_state.current_word
print("this is a randomly selected word from the json file of korean words: ", word.get("korean"))
difficulty = word.get("difficulty")

st.write("Translate the following word:", word.get("korean"))
st.write("Difficulty Level:", difficulty)

answer = st.text_input("enter english translation here:")

st.write(f"Attempts: {st.session_state.attempts}")  # Display the number of attempts for the current word

def add_response(user_id, word, user_answer, difficulty, correct, response_time, attempts):
    supabase.table("Responses").insert({
        "user_id": user_id,
        "word": word,
        "user_answer": user_answer,
        "correct": correct,
        "response_time": response_time,  # Placeholder for response time
        "difficulty": difficulty,
        "attempt_number": attempts
    }).execute()

if st.button("Submit"):
    correct = (answer.strip().lower() == word.get("english").strip().lower())
    response_time = time.time() - st.session_state.start_time

    st.session_state.attempts += 1  # Increment attempts for the current word

    if not answer:
        st.error("Please enter an answer before submitting.")
    else:
        add_response(user_id=user_id, word=word.get("korean"), user_answer=answer, difficulty=difficulty, correct=correct, response_time=response_time, attempts=st.session_state.attempts)

    st.write(f"Your response time: {response_time:.2f} seconds")
    # st.switch_page("pages/1_Answer.py")

    if correct:
        st.success("Correct!")
        st.session_state.show_next = True
    else:
        st.error(f"Incorrect! - try again!")
        st.stop()

def get_new_word(words, current_word):
    new_word = random.choice(words)
    while new_word == current_word:
        new_word = random.choice(words)
        
    return new_word

if st.session_state.show_next:
    if st.button("Next Word"):
        st.session_state.current_word = get_new_word(words, st.session_state.current_word)
        st.session_state.show_next = False
        st.session_state.start_time = time.time()  # Reset the timer for the new word
        st.session_state.attempts = 0  # Reset attempts for the new word
        st.rerun()

if st.button("Log Out"):
    logout_button()
    st.rerun()
