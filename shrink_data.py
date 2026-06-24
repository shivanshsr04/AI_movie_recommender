import pandas as pd
import pickle

print("Loading raw data...")
movies = pd.read_csv('data/raw/movies_metadata.csv', low_memory=False)

print("Cleaning data...")
movies['id'] = pd.to_numeric(movies['id'], errors='coerce')
movies = movies.dropna(subset=['id'])
movies['release_date'] = pd.to_datetime(movies['release_date'], errors='coerce')
movies['year'] = movies['release_date'].dt.year
movies['vote_average'] = pd.to_numeric(movies['vote_average'], errors='coerce').fillna(0).astype(float)

# Grab the top 10k movies (This shrinks it to ~5MB)
clean_movies = movies.sort_values('popularity', ascending=False).head(10000).reset_index(drop=True)

print("Saving lightweight file...")
with open('models/clean_movies.pkl', 'wb') as f:
    pickle.dump(clean_movies, f)

print("✅ Success! Your data is now tiny and ready for GitHub.")