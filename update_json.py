import json
import os

filepath = "korean_words.json"

with open(filepath, "r", encoding="utf-8") as f:
    words = json.load(f)

# Normalize existing words
for w in words:
    english = w.get("english", "")
    if w.get("word_type") == "adjective":
        if english.startswith("to be "):
            w["english"] = english[6:]
        elif english.startswith("to "):
            w["english"] = english[3:]
    elif w.get("word_type") == "verb":
        if not english.startswith("to "):
            w["english"] = "to " + english

new_words = [
    {"korean": "빵", "english": "bread", "difficulty": "beginner", "word_type": "noun", "category": "food", "frequency_rank": 350},
    {"korean": "우유", "english": "milk", "difficulty": "beginner", "word_type": "noun", "category": "food", "frequency_rank": 400},
    {"korean": "계란", "english": "egg", "difficulty": "beginner", "word_type": "noun", "category": "food", "frequency_rank": 450},
    {"korean": "커피", "english": "coffee", "difficulty": "beginner", "word_type": "noun", "category": "food", "frequency_rank": 200},
    {"korean": "차", "english": "tea", "difficulty": "beginner", "word_type": "noun", "category": "food", "frequency_rank": 500},
    {"korean": "개", "english": "dog", "difficulty": "beginner", "word_type": "noun", "category": "animals", "frequency_rank": 300},
    {"korean": "고양이", "english": "cat", "difficulty": "beginner", "word_type": "noun", "category": "animals", "frequency_rank": 320},
    {"korean": "새", "english": "bird", "difficulty": "beginner", "word_type": "noun", "category": "animals", "frequency_rank": 800},
    {"korean": "비", "english": "rain", "difficulty": "beginner", "word_type": "noun", "category": "weather", "frequency_rank": 600},
    {"korean": "눈", "english": "snow", "difficulty": "beginner", "word_type": "noun", "category": "weather", "frequency_rank": 650},
    {"korean": "바람", "english": "wind", "difficulty": "beginner", "word_type": "noun", "category": "weather", "frequency_rank": 700},
    {"korean": "자다", "english": "to sleep", "difficulty": "beginner", "word_type": "verb", "category": "verbs", "frequency_rank": 100},
    {"korean": "일하다", "english": "to work", "difficulty": "beginner", "word_type": "verb", "category": "verbs", "frequency_rank": 150},
    {"korean": "놀다", "english": "to play", "difficulty": "beginner", "word_type": "verb", "category": "verbs", "frequency_rank": 180},
    {"korean": "마시다", "english": "to drink", "difficulty": "beginner", "word_type": "verb", "category": "verbs", "frequency_rank": 120},
    {"korean": "사다", "english": "to buy", "difficulty": "beginner", "word_type": "verb", "category": "verbs", "frequency_rank": 140}
]

existing_korean_words = {w.get("korean") for w in words}
for nw in new_words:
    if nw["korean"] not in existing_korean_words:
        nw["word"] = nw.pop("korean") # wait, the format uses 'korean', 'english', 'difficulty', 'word_type', 'category', 'frequency_rank'
        # my dictionary has keys 'korean' in original json based on view_file output. Let's check view_file output.
        # yes, `{"korean": "학교", "english": "school", "difficulty": "beginner", "word_type": "noun", "category": "education", "frequency_rank": 400}`
        # Wait, the popping 'korean' was unnecessary.
        pass

# Fix new words dict keys
new_words_clean = [
    {"korean": "빵", "english": "bread", "difficulty": "beginner", "word_type": "noun", "category": "food", "frequency_rank": 350},
    {"korean": "우유", "english": "milk", "difficulty": "beginner", "word_type": "noun", "category": "food", "frequency_rank": 400},
    {"korean": "계란", "english": "egg", "difficulty": "beginner", "word_type": "noun", "category": "food", "frequency_rank": 450},
    {"korean": "커피", "english": "coffee", "difficulty": "beginner", "word_type": "noun", "category": "food", "frequency_rank": 200},
    {"korean": "차", "english": "tea", "difficulty": "beginner", "word_type": "noun", "category": "food", "frequency_rank": 500},
    {"korean": "개", "english": "dog", "difficulty": "beginner", "word_type": "noun", "category": "animals", "frequency_rank": 300},
    {"korean": "고양이", "english": "cat", "difficulty": "beginner", "word_type": "noun", "category": "animals", "frequency_rank": 320},
    {"korean": "새", "english": "bird", "difficulty": "beginner", "word_type": "noun", "category": "animals", "frequency_rank": 800},
    {"korean": "비", "english": "rain", "difficulty": "beginner", "word_type": "noun", "category": "weather", "frequency_rank": 600},
    {"korean": "눈", "english": "snow", "difficulty": "beginner", "word_type": "noun", "category": "weather", "frequency_rank": 650},
    {"korean": "바람", "english": "wind", "difficulty": "beginner", "word_type": "noun", "category": "weather", "frequency_rank": 700},
    {"korean": "자다", "english": "to sleep", "difficulty": "beginner", "word_type": "verb", "category": "verbs", "frequency_rank": 100},
    {"korean": "일하다", "english": "to work", "difficulty": "beginner", "word_type": "verb", "category": "verbs", "frequency_rank": 150},
    {"korean": "놀다", "english": "to play", "difficulty": "beginner", "word_type": "verb", "category": "verbs", "frequency_rank": 180},
    {"korean": "마시다", "english": "to drink", "difficulty": "beginner", "word_type": "verb", "category": "verbs", "frequency_rank": 120},
    {"korean": "사다", "english": "to buy", "difficulty": "beginner", "word_type": "verb", "category": "verbs", "frequency_rank": 140}
]

for nw in new_words_clean:
    if nw["korean"] not in existing_korean_words:
        words.append(nw)

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(words, f, indent=2, ensure_ascii=False)
print("Updated korean_words.json with normalized English translations and 16 new words.")
