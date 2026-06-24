import pandas as pd
import pickle
import os

print("--- STARTING RELIABLE SHRINK ---")
path = 'data/raw/movies_metadata.csv'

# Load data
df = pd.read_csv(path, low_memory=False)

# 1. Map columns correctly based on your actual CSV header
# We ensure 'title' exists by using 'original_title' if 'title' is empty
df['title'] = df['title'].fillna(df['original_title'])

# 2. Extract year safely
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df['year'] = df['release_date'].dt.year.fillna(0).astype(int)

# 3. Clean numeric columns
df['id'] = pd.to_numeric(df['id'], errors='coerce')
df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce').fillna(0)
df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce').fillna(0)

# 4. Filter only the columns we actually need
# Update the column list to include 'vote_count'
cols = ['id', 'title', 'year', 'vote_average', 'popularity', 'overview', 'poster_path', 'vote_count']

# Ensure we don't crash if vote_count is missing in the raw data
if 'vote_count' not in df.columns:
    df['vote_count'] = 0

clean_movies = df[cols].dropna(subset=['id']).sort_values('popularity', ascending=False).head(10000)
# 5. Save
with open('models/clean_movies.pkl', 'wb') as f:
    pickle.dump(clean_movies, f)

print(f"✅ SUCCESS! Saved {len(clean_movies)} movies.")