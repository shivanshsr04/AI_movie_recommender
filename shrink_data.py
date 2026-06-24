import pandas as pd
import pickle
import os

os.makedirs('models', exist_ok=True)

# Use 'on_bad_lines="skip"' to ignore rows that are broken
print("Loading raw data with skip...")
try:
    movies = pd.read_csv('data/raw/movies_metadata.csv', low_memory=False, on_bad_lines='skip')
    print(f"Loaded {len(movies)} rows.")
except Exception as e:
    print(f"Error reading CSV: {e}")
    exit()

# Force numeric conversion for ID to ensure we have valid records
movies['id'] = pd.to_numeric(movies['id'], errors='coerce')
movies = movies.dropna(subset=['id'])

# Clean columns
movies['release_date'] = pd.to_datetime(movies['release_date'], errors='coerce')
movies['year'] = movies['release_date'].dt.year
movies['vote_average'] = pd.to_numeric(movies['vote_average'], errors='coerce').fillna(0)
movies['popularity'] = pd.to_numeric(movies['popularity'], errors='coerce').fillna(0)

# Shrink
clean_movies = movies.sort_values('popularity', ascending=False).head(10000).reset_index(drop=True)

if len(clean_movies) > 0:
    with open('models/clean_movies.pkl', 'wb') as f:
        pickle.dump(clean_movies, f)
    print(f"✅ Success! Created file with {len(clean_movies)} movies.")
else:
    print("❌ Error: Still produced an empty file. Check your CSV structure!")