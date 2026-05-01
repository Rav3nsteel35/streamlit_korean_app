import time
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import json, random
import pathlib
import base64
from pathlib import Path
import time
import re
from utils import load_css, get_base64_image  # Import utility functions

def clean_answer(ans):
    # Removes leading "to be ", "to ", "be " from answers to allow forgiving grading
    ans = ans.strip().lower()
    return re.sub(r'^(to be |to |be )', '', ans)
from datetime import datetime, date, timedelta
from auth_functions import logout_button


from dotenv import load_dotenv, dotenv_values

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

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if "user" not in st.session_state:
    st.session_state.user = None

# If not logged in, show auth page:
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("Home.py")  # Redirect to landing/home page
    st.stop()

user_id = st.session_state.user.id

if "word_progress" not in st.session_state:
    result = (
        supabase.table("WordProgress")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    st.session_state.word_progress = result.data

def get_user_streak(user_id):
    """Return the current streak of consecutive days with at least one answer."""
    responses = supabase.table("Responses").select("created_at").eq("user_id", user_id).execute()
    if not responses.data:
        return 0

    dates = set()
    for r in responses.data:
        date_str = r['created_at'][:10]  # YYYY-MM-DD
        dates.add(date_str)

    study_dates = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in dates])
    current_streak = 0
    today = date.today()
    check_date = today

    while check_date in study_dates:
        current_streak += 1
        check_date -= timedelta(days=1)

    return current_streak


# After user is verified, reset timer if it's absurd
if "start_time" in st.session_state:
    # If start_time is more than 1 hour old or negative, reset it
    if st.session_state.start_time < time.time() - 3600:  # 1 hour
        st.session_state.start_time = time.time()


if "streak_celebrated" not in st.session_state:
    current_streak = get_user_streak(user_id)

    if "last_login_date" in st.session_state:
        last = st.session_state.last_login_date
        today_date = date.today()
        if (today_date - last).days == 1 and current_streak > 0:
            st.balloons()
            st.success(f"🔥 {current_streak} day streak! Keep it up!")

    st.session_state.last_login_date = date.today()
    st.session_state.streak_celebrated = True

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


# if "streak_celebrated" not in st.session_state:
#     # Check if this is a new day and you have a streak
#     if "last_login_date" in st.session_state:
#         last = st.session_state.last_login_date
#         today = date.today()
#         if (today - last).days == 1:  # Logged in yesterday
#             # You have a streak!
#             st.balloons()
#             st.success(f"🔥 {current_streak} day streak! Keep it up!") #update the placeholder text later!!!
    
#     st.session_state.last_login_date = date.today()
#     st.session_state.streak_celebrated = True


# Welcome back toast message with streak info
if "just_logged_in" in st.session_state:
    current_streak = get_user_streak(user_id)
    if current_streak > 0:
        st.toast(f"🔥🔥🔥 Welcome back! You're on a {current_streak}-day streak!", icon="🌸")
    else:
        st.toast("🌸 Ready to learn some Korean?", icon="📚")
    del st.session_state.just_logged_in

# Display a randome koreann proverb per page load for motivation ㅎㅎㅎ
quotes = [
    ("천리길도 한 걸음부터", "A thousand-mile journey begins with one step"),
    ("시작이 반이다", "Well begun is half done"),
    ("호랑이에게 잡히려면 호랑이 굴에 들어가라", "If you want to catch a tiger, enter its cave"),
    ("공든 탑이 무너지랴", "A tower built with hard work will not collapse"),
    ("배보다 배꼽이 크다", "The belly button is bigger than the belly (the cost is more than the value)"),
]

quote = random.choice(quotes)
st.caption(f"💭 *{quote[0]}* — {quote[1]}")

# with open("korean_words.json", "r", encoding="utf-8") as f:
#     words = json.load(f)

@st.cache_data
def load_words():
    with open("korean_words.json", "r", encoding="utf-8") as f:
        return json.load(f)

words = load_words()

# --- Dropdown Filters ---
categories = ["All Categories"] + sorted(list(set(w.get("category", "") for w in words if w.get("category"))))
difficulties = ["All Difficulties"] + sorted(list(set(w.get("difficulty", "") for w in words if w.get("difficulty"))))

col_f1, col_f2 = st.columns(2)
with col_f1:
    selected_category = st.selectbox("Category", categories, key="selected_category")
with col_f2:
    selected_difficulty = st.selectbox("Difficulty", difficulties, key="selected_difficulty")

filtered_words = [
    w for w in words 
    if (selected_category == "All Categories" or w.get("category") == selected_category) and 
       (selected_difficulty == "All Difficulties" or w.get("difficulty") == selected_difficulty)
]
if not filtered_words:
    st.warning("No words match this filter. Showing all words.")
    filtered_words = words

# Ensure current_word matches filter if already loaded, else grab a new one
if "current_word" in st.session_state:
    cw = st.session_state.current_word
    if (selected_category != "All Categories" and cw.get("category") != selected_category) or \
       (selected_difficulty != "All Difficulties" and cw.get("difficulty") != selected_difficulty):
        st.session_state.current_word = random.choice(filtered_words)
        st.session_state.attempts = 0

if "current_word" not in st.session_state:
    st.session_state.current_word = random.choice(filtered_words)
    st.session_state.start_time = time.time()    # Start the timer when the word is first displayed
    st.session_state.attempts = 0  # Initialize attempts for the current word

if "show_next" not in st.session_state:
    st.session_state.show_next = False  # Hidden at first

if 'attempts' not in st.session_state:
    st.session_state.attempts = 0

word = st.session_state.current_word
print("this is a randomly selected word from the json file of korean words: ", word.get("korean"))
difficulty = word.get("difficulty")
category = word.get("category")
word_type = word.get("word_type")
word_length = len(word.get("korean"))
num_syllables = len(word.get("korean"))
word_frequency = word.get("frequency")

# st.markdown(
#     f"<h1 style='text-align:center; font-size:70px;'>{word.get('korean')}</h1>",
#     unsafe_allow_html=True
# )

# Create a styled card for the Korean word
st.markdown(
    f'<div class="word-card">{word.get("korean")}</div>',
    unsafe_allow_html=True
)



st.markdown(
    '<p class="translation-prompt">Enter the English translation</p>',
    unsafe_allow_html=True
)


# st.write("Difficulty Level:", difficulty)
# st.write("Category:", category)
# st.write("Word Type:", word_type)

if "answer_input" not in st.session_state:
    st.session_state.answer_input = ""

# answer = st.text_input("enter english translation here:")

# st.markdown(f'<div class="attempts-badge">Attempts: {st.session_state.attempts}</div>', unsafe_allow_html=True)

# st.markdown('<div class="answer-box">', unsafe_allow_html=True)

# answer = st.text_input("", key="answer_input")

st.markdown('<div class="input-row">', unsafe_allow_html=True)

row_left, row_right = st.columns([1, 4], vertical_alignment="center")

with row_left:
    st.markdown(
        f'<div class="attempts-wrap"><div class="attempts-badge">Attempts: {st.session_state.attempts}</div></div>',
        unsafe_allow_html=True
    )

def set_submitted():
    st.session_state.submitted = True

with row_right:
    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
    answer = st.text_input("", placeholder="Type English eg. eat, see, cheap", key="answer_input", on_change=set_submitted)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


mascot_base64 = get_base64_image("assets/download.jpg")

st.markdown(
    f"""
    <div class="floating-mascot">
        <img src="data:image/jpeg;base64,{mascot_base64}" alt="Mascot">
    </div>
    """,
    unsafe_allow_html=True
)

correct = clean_answer(answer) == clean_answer(word.get("english"))

def add_response(user_id, word, user_answer, difficulty, correct, response_time, attempts, category, word_type, word_length, num_syllables, word_frequency):
    
    supabase.table("Responses").insert({
        "user_id": user_id,
        "word": word,
        "user_answer": user_answer,
        "correct": correct,
        "response_time": response_time,
        "difficulty": difficulty,
        "attempt_number": attempts,
        "category": category,
        "word_type": word_type,
        "word_length": word_length,
        "num_syllables": num_syllables,
        "word_frequency": word_frequency
    }).execute()

def update_word_stats(user_id, word, times_seen_before, times_correct_before, times_wrong_before, last_seen_at, next_review_at, ease_factor, interval_days):
        
        supabase.table("WordProgress").upsert({
        "user_id": user_id,
        "word": word,
        "times_seen_before": times_seen_before,
        "times_correct_before": times_correct_before,
        "times_wrong_before": times_wrong_before,
        "last_seen_at": last_seen_at,
        "next_review_at": next_review_at,
        "ease_factor": ease_factor,
        "interval_days": interval_days
    }, on_conflict="user_id, word").execute() 
        
# st.write("DEBUG show_next:", st.session_state.show_next)
# print("DEBUG show_next:", st.session_state.show_next)

next_word = False
logout = False

# UI layout with three columns to center the content and place buttons below the input field:
left, center, right = st.columns([1,2,1])

with center:

    if not st.session_state.show_next:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Submit"):
                st.session_state.submitted = True

        with col2:
            logout = st.button("Log Out")

    else:
        col1, col2 = st.columns(2)

        with col1:
            next_word = st.button("Next Word")

        with col2:
            logout = st.button("Log Out")

if st.session_state.get("submitted", False):
    st.session_state.submitted = False # reset immediately

    with st.spinner('🌸 Checking your answer...'):
        time.sleep(1)  # Simulates loading - remove in production

        correct = clean_answer(answer) == clean_answer(word.get("english"))
        response_time = time.time() - st.session_state.start_time
        st.session_state.attempts += 1  # Increment attempts for the current word

        # Sanity check - if it's more than 5 minutes, something's wrong
        if response_time > 180:  # 5 minutes in seconds
            response_time = 0  # Or set to a reasonable default
            st.warning("Response time reset due to session issue")

        if not answer:
            st.error("Please enter an answer before submitting.")
            st.stop()

        add_response(user_id=user_id,
                        word=word.get("korean"),
                        user_answer=answer,
                        difficulty=difficulty,
                        correct=correct,
                        response_time=response_time,
                        attempts=st.session_state.attempts, 
                        category=category,
                        word_type=word_type,
                        word_length=word_length,
                        num_syllables=num_syllables,
                        word_frequency=word_frequency)

        if "word_progress" not in st.session_state:
            result = supabase.table("WordProgress").select("*").eq("user_id", user_id).execute()
            st.session_state.word_progress = result.data 

        # words_seen = supabase.table("WordProgress").select("*").eq("user_id", user_id).execute()
        words_seen = st.session_state.word_progress
        seen_words = [w['word'] for w in words_seen]
        now = int(time.time())
        if word.get("korean") not in seen_words: # if the word has not been seen before, we create a new entry in the WordProgress table

            update_word_stats(user_id=user_id,
                            word=word.get("korean"),
                            times_seen_before= 1,  # First time seeing the word
                            times_correct_before=1 if correct else 0,  # <<< FIXED
                            times_wrong_before=0 if correct else 1,    # <<< FIXED
                            last_seen_at = datetime.now().isoformat(),
                            next_review_at = (datetime.now() + timedelta(days=1)).isoformat(),
                            ease_factor= 2.5,  # Placeholder for ease factor
                            interval_days= 1)  # Placeholder for interval days

            result = (
                supabase.table("WordProgress")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )

            st.session_state.word_progress = result.data

            # result = supabase.table("WordProgress").select("*").eq("user_id", user_id).execute()
            # st.session_state.word_progress = result.data

        elif word.get("korean") in seen_words and correct: # if the word has been seen before and this is the first attempt at answering it, we update the existing entry in the WordProgress table with the new stats
            existing_stats = next((w for w in words_seen if w['word'] == word.get("korean")), None)
            
            if existing_stats:
                times_seen_before = existing_stats['times_seen_before'] + 1
                times_correct_before= existing_stats["times_correct_before"] + (1 if correct else 0)
                times_wrong_before= existing_stats["times_wrong_before"] + (0 if correct else 1)
                last_seen_at = datetime.now().isoformat()
                next_review_at = (datetime.now() + timedelta(days=1)).isoformat()
                ease = existing_stats['ease_factor']  # This would ideally be updated based on performance
                interval = existing_stats['interval_days']  # This would ideally be updated based on performance

                if correct:
                    if interval == 1:
                        interval = 3
                    else:
                        interval = round(interval * ease)

                    ease = max(1.3, ease + 0.1)
                else:
                    interval = 1
                    ease = max(1.3, ease - 0.2)

                next_review = datetime.now() + timedelta(days=interval)

                update_word_stats(user_id=user_id,
                                word=word.get("korean"),
                                times_seen_before=times_seen_before,
                                times_correct_before=times_correct_before,
                                times_wrong_before=times_wrong_before,
                                last_seen_at=last_seen_at,
                                next_review_at= next_review.isoformat(),
                                ease_factor= ease,
                                interval_days = interval
                )
        else:
            pass  # If the word has been seen before but this is not the first attempt, we do not update the WordProgress stats to avoid skewing the data with multiple attempts for the same word in one session
            

        st.write(f"Your response time: {response_time:.2f} seconds")
        # st.switch_page("pages/1_Answer.py")

        if correct:
            # st.success("Correct!")
            # st.session_state.show_next = True
            # st.rerun()
            st.session_state.last_correct = True
            st.session_state.last_response_time = response_time
            st.session_state.show_next = True
            st.rerun()

        else:
            st.error(f"Incorrect! - try again!")
            # st.stop()

if "last_correct" in st.session_state:
    st.write(f"Your response time: {st.session_state.last_response_time:.2f} seconds")

    if st.session_state.last_correct:
        st.success("Correct!")
    else:
        st.error("Incorrect — try again!")


def get_new_word(filtered_words, current_word):

    srs_word = get_next_srs_word(user_id)

    print("SRS picked:", srs_word)

    # If SRS selected something
    if srs_word:
        # find the full word object
        for w in filtered_words:
            if w["korean"] == srs_word:
                return w

    seen_words = [w['word'] for w in st.session_state.word_progress]

    unseen_words = [w for w in filtered_words if w["korean"] not in seen_words]

    if unseen_words:
        new_word = random.choice(unseen_words)
    else:
        new_word = random.choice(filtered_words)

    # avoid repeating same word if possible
    if len(filtered_words) > 1:
        while new_word["korean"] == current_word.get("korean", ""):
            new_word = random.choice(filtered_words)

    return new_word

def get_next_srs_word(user_id):
    now = datetime.now().isoformat()
    srs_words = (
        supabase.table("WordProgress")
        .select("*")
        .eq("user_id", user_id)
        .lte("next_review_at", now)
        .execute()
    )
    
    #If some words are overdue → pick earliest ones
    if srs_words.data:
        # sort overdue words by next_review_at ASC
        sorted_overdue = sorted(srs_words.data, key=lambda w: w["next_review_at"])
        return sorted_overdue[0]["word"]   # highest priority word

    # If no SRS words due → fallback to NEW words
    return None

# if st.session_state.show_next:
#     if st.button("Next Word"):

#         if "answer_input" in st.session_state:
#             del st.session_state["answer_input"]

#         st.session_state.current_word = get_new_word(words, st.session_state.current_word)
#         st.session_state.show_next = False
#         st.session_state.start_time = time.time()
#         st.session_state.attempts = 0

#         st.rerun()

if next_word:

    with st.spinner('📚 Loading next word...'):

        if "answer_input" in st.session_state:
            del st.session_state["answer_input"]

        st.session_state.pop("last_correct", None)
        st.session_state.pop("last_response_time", None)

        st.session_state.current_word = get_new_word(filtered_words, st.session_state.current_word)
        st.session_state.show_next = False
        st.session_state.start_time = time.time()
        st.session_state.attempts = 0

        st.rerun()

if logout:
    logout_button()
    st.rerun()

# import os
# st.write("Current working directory:", os.getcwd())
# st.write("Files in current directory:", os.listdir())

# from streamlit.source_util import get_pages
# st.write("Available pages:", list(get_pages("Home.py").keys()))
# st.write("Page names:", [page["page_name"] for page in get_pages("Home.py").values()])