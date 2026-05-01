import streamlit as st
from supabase import create_client
import os
import pandas as pd
import altair as alt
from auth_functions import logout_button
import pathlib
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
import json



# st.set_page_config(layout="centered")

load_dotenv()

def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

# --- CONNECT TO SUPABASE ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

def generate_insights(df, current_streak):  # Add current_streak parameter
    insights = []
    
    # 1. Accuracy trend
    recent_df = df.sort_values('created_at').tail(10)
    recent_acc = recent_df['correct'].mean()
    overall_acc = df['correct'].mean()
    
    if recent_acc > overall_acc + 0.1:
        insights.append("📈 **You're improving!** Your last 10 answers are {:.0%} accurate, better than your overall {:.0%}".format(
            recent_acc, overall_acc))
    elif recent_acc < overall_acc - 0.1:
        insights.append("📉 **Your accuracy has dropped.** Take a break or review some old words!")
    
    # 2. Specific word recommendations
    struggling_words = df[df['correct'] == False].groupby('word').size().sort_values(ascending=False).head(3)
    if not struggling_words.empty:
        words_list = ', '.join(struggling_words.index)
        insights.append(f"🔍 **Practice these:** {words_list} - you missed them the most")
    
    # 3. Time-based insights
    avg_time = df['response_time'].mean()
    if avg_time > 60:
        insights.append("⏱️ **Take your time!** No rush - accuracy matters more than speed")
    elif avg_time < 10:
        insights.append("⚡ **You're quick!** Try challenging yourself with harder words")
    
    # 4. Study streak - USE current_streak, not study_days
    if current_streak > 0:
        insights.append(f"🔥 **{current_streak} day streak!** Keep it going!")
    else:
        insights.append("🌱 **Start a streak!** Practice today to begin your streak.")
    
    # 5. Category weakness
    cat_acc = df.groupby('category')['correct'].mean()
    if not cat_acc.empty:
        weakest_cat = cat_acc.idxmin()
        weakest_acc = cat_acc.min()
        if weakest_acc < 0.6:
            insights.append(f"🎯 **Focus on {weakest_cat}** - you're at {weakest_acc:.0%} accuracy")
    
    return insights

# LOAD DATA
def load_responses(user_id):
    res = supabase.table("Responses").select("*").eq("user_id", user_id).execute()
    if not res.data:
        return pd.DataFrame()
    
    df = pd.DataFrame(res.data)

    # If 'english' column is missing, add it by mapping from the Korean words
        #load english translations if not present
    with open('korean_words.json', 'r', encoding='utf-8') as f:
        word_list = json.load(f)

    word_to_eng = {w['korean']: w['english'] for w in word_list}

    df['english'] = df['word'].map(word_to_eng)
    
    return df

st.markdown('<h1 class="custom-title">📊 Korean Learning Dashboard</h1>', unsafe_allow_html=True)
# Must be logged in
if "user" not in st.session_state or st.session_state.user is None:
    st.error("You must be logged in to view the dashboard.")
    st.stop()

user_id = st.session_state.user.id
df = load_responses(user_id)

if not df.empty:
    # ===== STREAK COUNTER =====
    st.markdown("""
    <style>
        .streak-container {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin: 1rem 0 2rem 0;
        }
        .streak-card {
            background: rgba(255, 245, 245, 0.45);
            backdrop-filter: blur(8px);
            border-radius: 30px;
            padding: 1rem 2rem;
            text-align: center;
            min-width: 150px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            margin-bottom: 1rem !important;
        }
        .streak-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #c85f4a;
            line-height: 1.2;
        }
        .streak-label {
            color: #5a355a;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .goal-progress {
            margin-top: 0.5rem;
            height: 8px;
            background: rgba(200, 95, 74, 0.2);
            border-radius: 10px;
            overflow: hidden;
        }
        .goal-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff9a9e, #c85f4a);
            border-radius: 10px;
            transition: width 0.3s ease;
        }
                
        input::placeholder {
            color: #2f2f2f !important;
            opacity: 0.7 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Calculate streak
    df['date'] = pd.to_datetime(df['created_at']).dt.date
    study_dates = sorted(df['date'].unique())

   # Calculate current streak
    current_streak = 0
    today = date.today()
    check_date = today
    
    while check_date in study_dates:
        current_streak += 1
        check_date = check_date - timedelta(days=1)
    
    # Calculate longest streak
    longest_streak = 0
    current = 0
    prev_date = None
    
    for d in sorted(study_dates):
        if prev_date is None or (d - prev_date).days == 1:
            current += 1
        else:
            current = 1
        longest_streak = max(longest_streak, current)
        prev_date = d

    # Daily goal
    daily_goal = 10  # Default goal
    if "daily_goal" in st.session_state:
        daily_goal = st.session_state.daily_goal

    # Words studied today
    today_words = len(df[df['date'] == today]['word'].unique())
    goal_progress = min(today_words / daily_goal, 1.0) * 100

else: 
    # NEW USERS - no data yet
    current_streak = 0
    longest_streak = 0
    daily_goal = 10
    if "daily_goal" in st.session_state:
        daily_goal = st.session_state.daily_goal
    today_words = 0
    goal_progress = 0

# ===== DISPLAY THE STREAK CARDS =====
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="streak-card">
        <div class="streak-value">{current_streak}</div>
        <div class="streak-label">🔥 Current Streak</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="streak-card">
        <div class="streak-value">{longest_streak}</div>
        <div class="streak-label">🏆 Best Streak</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="streak-card">
        <div class="streak-value">{today_words}/{daily_goal}</div>
        <div class="streak-label">📅 Today's Goal</div>
        <div class="goal-progress">
            <div class="goal-progress-fill" style="width: {goal_progress}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Add goal setting option
with st.expander("🎯 Set Daily Goal"):
    new_goal = st.number_input("Words per day:", min_value=1, max_value=50, value=daily_goal)
    if st.button("Update Goal"):
        st.session_state.daily_goal = new_goal
        st.rerun()

st.divider()

# If no data yet
if df.empty:
    st.info("You haven't answered any questions yet — go practice!")
    st.stop()

# Ensure correct types
df["correct"] = df["correct"].astype(int)
df["attempt_number"] = df["attempt_number"].astype(int)

generated_insights = generate_insights(df, current_streak)  # Add current_streak here

for insight in generated_insights:
    st.write(f"💡 {insight}")

# --- HIGH-LEVEL METRICS ---
col1, col2, col3 = st.columns(3)

accuracy = df["correct"].mean() * 100
avg_time = df["response_time"].mean()
avg_attempts = df["attempt_number"].mean()

col1.metric("Accuracy", f"{accuracy:.1f}%")
col2.metric("Avg Response Time", f"{avg_time:.2f}s")
col3.metric("Avg Attempts", f"{avg_attempts:.1f}")

st.divider()

st.subheader("🔍 Search Your Words")

# Load the master word list for translations
import json
with open("korean_words.json", "r", encoding="utf-8") as f:
    master_words = json.load(f)
# Create lookup dictionaries
korean_to_english = {w['korean']: w['english'] for w in master_words}
english_to_korean = {w['english'].lower(): w['korean'] for w in master_words}

word_search = st.text_input("Search by Korean or English word, see how you did! (partial matches work too)", 
                           placeholder="e.g., 학교, school, 사랑, love...")

if word_search:
    search_term = word_search.lower().strip()
    
    # Find matching Korean words
    korean_matches = [w for w in df['word'].unique() if search_term in w.lower()]
    
    # Find matching English words (look up in the JSON)
    english_matches = []
    for eng, kor in english_to_korean.items():
        if search_term in eng:
            english_matches.append(kor)
    
    # Combine all matching Korean words
    all_matches = set(korean_matches + english_matches)
    
    if all_matches:
        # Filter dataframe for these words
        filtered = df[df['word'].isin(all_matches)]
        
        # Add English translation column from master list
        filtered = filtered.copy()
        filtered['english'] = filtered['word'].map(korean_to_english)
        
        # Display results
        display_df = filtered[['word', 'english', 'correct', 'response_time', 
                              'attempt_number', 'difficulty', 'category', 'created_at']].copy()
        
        # Format columns
        display_df['correct'] = display_df['correct'].map({1: "✅ Correct", 0: "❌ Incorrect"})
        display_df['response_time'] = display_df['response_time'].round(2)
        
        # Sort by most recent first
        sorted_df = display_df.sort_values('created_at', ascending=False).drop(columns=['created_at'])
        
        st.dataframe(
            sorted_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "word": "Korean",
                "english": "English",
                "correct": "Result",
                "response_time": "Time (s)",
                "attempt_number": "Attempts",
                "difficulty": "Difficulty",
                "category": "Category"
            }
        )
        
        st.caption(f"Found {len(filtered)} entries for '{word_search}'")
        
        col1, col2 = st.columns(2)
        with col1:
            word_accuracy = filtered['correct'].mean() * 100
            st.metric(f"Accuracy", f"{word_accuracy:.1f}%")
        
        with col2:
            avg_time = filtered['response_time'].mean()
            st.metric(f"Avg Response Time", f"{avg_time:.2f}s")
        
        unique_words = filtered['word'].nunique()
        st.info(f"📚 Found {unique_words} unique word(s) matching your search")
        
    else:
        st.info(f"No entries found for '{word_search}'")

st.divider()

st.subheader("Stats for Nerds ㅎㅎㅎ (Advanced Analytics)")

# ==========================
# 📌 Accuracy by Difficulty
# ==========================
st.subheader("Accuracy by Difficulty")

acc_diff = df.groupby("difficulty")["correct"].mean() * 100
st.bar_chart(acc_diff)

st.divider()


# ==========================
# 📌 Accuracy by Category
# ==========================
st.subheader("Accuracy by Category")

acc_cat = df.groupby("category")["correct"].mean() * 100
st.bar_chart(acc_cat)

st.divider()


# ==========================
# 📌 Hardest & Easiest Words
# ==========================
st.subheader("Most Difficult Words (Highest Attempts)")

weak_words = (
    df.groupby("word")["attempt_number"]
    .mean()
    .sort_values(ascending=False)
    .head(5)
)

st.table(weak_words)

st.subheader("Easiest Words (Lowest Attempts)")
easy_words = (
    df.groupby("word")["attempt_number"]
    .mean()
    .sort_values()
    .head(5)
)
st.table(easy_words)

st.divider()


# ==========================
# 📈 Learning Curve (Accuracy Over Time)
# ==========================

st.subheader("Learning Curve: Accuracy Over Time")

df['timestamp'] = pd.to_datetime(df['created_at'], errors='coerce')

acc_over_time = (
    df.sort_values("timestamp")
      .groupby(df['timestamp'].dt.date)["correct"]
      .mean() * 100
)

if len(acc_over_time) > 1:
    line = alt.Chart(acc_over_time.reset_index()).mark_line(point=True).encode(
        x="timestamp:T",
        y="correct:Q",
        tooltip=["timestamp:T", "correct:Q"]
    )
    st.altair_chart(line, use_container_width=True)
else:
    st.info("Not enough data for learning curve yet.")

st.divider()


# ==========================
# ⏱ Response Time Distribution
# ==========================
st.subheader("Response Time Distribution")

hist = alt.Chart(df).mark_bar().encode(
    x=alt.X("response_time:Q", bin=True),
    y='count()'
)

st.altair_chart(hist, use_container_width=True)

st.divider()


# ==========================
# 🧩 Category Performance Heatmap
# ==========================

st.subheader("Category Performance Heatmap")

heat_df = (
    df.groupby("category")[["correct", "attempt_number", "response_time"]]
    .mean()
    .rename(columns={
        "correct": "accuracy",
        "attempt_number": "avg_attempts",
        "response_time": "avg_time"
    })
)
heat_df["accuracy"] *= 100

st.dataframe(heat_df.style.background_gradient(cmap="Blues"))

st.divider()
# Navigation back to practice
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("← Back to Practice", use_container_width=True):
        st.switch_page("pages/1_Practice.py")

# Logout button
if st.button("Log Out", use_container_width=True):
    logout_button()       

#Html to force black text on tables:
st.markdown("""
<style>
    /* Force all text in the dashboard to be dark */
    .stApp, .stApp * {
        color: #2f2f2f !important;
    }
    
    /* But keep the navbar title color */
    .nav-title, .nav-title * {
        color: #c85f4a !important;
    }
    
    /* Keep streak values colored */
    .streak-value, .streak-value * {
        color: #c85f4a !important;
    }
    
    /* Keep metric values colored */
    [data-testid="stMetricValue"] {
        color: #db6e58 !important;
    }
    
    /* Style the bar charts - change text color */
    .stBarChart svg text {
        fill: #2f2f2f !important;
    }
    
    /* Style Altair charts */
    .vega-embed svg text {
        fill: #2f2f2f !important;
    }
    
    /* Style table text */
    .stTable table, .stTable td, .stTable th {
        color: #2f2f2f !important;
    }
    
    .stTable td {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Style dataframe */
    .stDataFrame, .stDataFrame * {
        color: #2f2f2f !important;
    }
    
    /* Style the insights text */
    .stMarkdown p {
        color: #2f2f2f !important;
    }
    
    /* Style subheaders */
    h1, h2, h3, h4, h5, h6 {
        color: #5a355a !important;
    }
    
    /* Override any white text */
    div:not(.nav-title):not(.streak-value) {
        color: #2f2f2f !important;
    }
</style>
""", unsafe_allow_html=True)