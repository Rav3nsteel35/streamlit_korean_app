from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
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
from utils import load_css, get_base64_image
from sklearn.cluster import KMeans
import numpy as np

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

@st.cache_data
def load_words():
    with open("korean_words.json", "r", encoding="utf-8") as f:
        return json.load(f)

words = load_words()

embeddings = {}
for word in words:
    embeddings[word["korean"]] = model.encode(word["korean"]).tolist()

# with open('word_embeddings.json', 'w', encoding='utf-8') as f:
#     # Convert numpy arrays to lists for JSON (already lists from the loop)
#     json.dump(embeddings, f, ensure_ascii=False, indent=4)

# Load embeddings
word_list = list(embeddings.keys())
embedding_matrix = np.array(list(embeddings.values()))

# Find optimal clusters (try 5-10)
kmeans = KMeans(n_clusters=8, random_state=42)
clusters = kmeans.fit_predict(embedding_matrix)

# Create mapping
word_to_cluster = {word: int(cluster) for word, cluster in zip(word_list, clusters)}


with open("word_cluster_mapping.json", "w", encoding="utf-8") as f:
    json.dump(word_to_cluster, f, ensure_ascii=False, indent=4)

# Also save cluster statistics (optional, for debugging)
cluster_summary = {}
for word, cluster in word_to_cluster.items():
    if cluster not in cluster_summary:
        cluster_summary[cluster] = []
    cluster_summary[cluster].append(word)

print("\n=== CLUSTER SUMMARY ===")
for cluster_id, words_in_cluster in cluster_summary.items():
    print(f"\nCluster {cluster_id}: {len(words_in_cluster)} words")
    print(f"Sample words: {', '.join(words_in_cluster[:5])}")

school = model.encode("학교", convert_to_tensor=True)
student = model.encode("학생", convert_to_tensor=True)
happy = model.encode("행복", convert_to_tensor=True)

print("학교 vs 학생:")
print(cos_sim(school, student))

print()

print("학교 vs 행복:")
print(cos_sim(school, happy))