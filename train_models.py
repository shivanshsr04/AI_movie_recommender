"""
Simplified Model Training Script
Generates placeholder recommendation models for the Streamlit app
"""

import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.neighbors import NearestNeighbors
import warnings
warnings.filterwarnings('ignore')

def create_sample_data():
    """Create sample movie data for demonstration"""
    print("📊 Creating sample movie database...")
    
    # Define the base data
    ids = list(range(1, 101))
    titles = [
        'Inception', 'The Matrix', 'Interstellar', 'The Dark Knight', 'Pulp Fiction',
        'Forrest Gump', 'The Shawshank Redemption', 'Fight Club', 'The Godfather', 'Avatar',
        'Titanic', 'Jurassic Park', 'The Avengers', 'Iron Man', 'Captain America',
        'Thor', 'Black Panther', 'Spider-Man', 'Doctor Strange', 'Guardians of the Galaxy',
        'Deadpool', 'Logan', 'X-Men', 'The Fantastic Four', 'Ant-Man',
        'The Lion King', 'Frozen', 'Moana', 'Coco', 'Toy Story',
        'Finding Nemo', 'Inside Out', 'Up', 'Wall-E', 'Monsters Inc',
        'The Incredibles', 'Ratatouille', 'Cars', 'A Bug\'s Life', 'Brave',
        'Harry Potter and the Sorcerer\'s Stone', 'The Hunger Games', 'Twilight', 'Percy Jackson', 'The 5th Wave',
        'Divergent', 'The Maze Runner', 'Dune', 'Blade Runner', 'The Terminator',
        'RoboCop', 'Total Recall', 'Minority Report', 'Looper', 'Edge of Tomorrow',
        'Mad Max: Fury Road', 'John Wick', 'Atomic Blonde', 'Mission Impossible', 'Jason Bourne',
        'Fast & Furious', 'Now You See Me', 'Ocean\'s Eleven', 'Heist', 'The Italian Job',
        'Sherlock Holmes', 'National Treasure', 'Pirates of the Caribbean', 'The Mummy', 'Indiana Jones',
        'Tomb Raider', 'Uncharted', 'Jungle Cruise', 'The Rundown', 'Sahara',
        'The Great Gatsby', 'Pride and Prejudice', 'Jane Eyre', 'Wuthering Heights', 'Emma',
        'The Bridges of Madison County', 'Titanic', 'The Fault in Our Stars', 'Love Simon', 'Call Me By Your Name',
        'Brokeback Mountain', 'Carol', 'God\'s Own Country', 'Maurice', 'The Half of It',
        'Moonlight', 'La La Land', 'The Shape of Water', 'Everything Everywhere All at Once', 'Poor Things'
    ]
    
    # 1. Ensure title length matches ID length (add placeholders if short)
    while len(titles) < 100:
        titles.append(f"Movie {len(titles) + 1}")

    # 2. Ensure overview length matches
    overviews = [
        'A skilled thief who steals corporate secrets through dream-sharing technology.',
        'A computer hacker learns about the true nature of reality.',
        'A team of astronauts travel through a wormhole to find a new habitable planet.',
        # ... (rest of your original overviews)
    ]
    # Add filler overviews until we hit 100
    while len(overviews) < 100:
        overviews.append('A compelling story about human life and discovery.')

    movies_data = {
        'id': ids,
        'title': titles,
        'overview': overviews,
        'genres': ['Action'] * 25 + ['Animation'] * 20 + ['Adventure'] * 20 + ['Romance'] * 15 + ['Drama'] * 20,
        'release_date': pd.date_range(start='1999-01-01', periods=100, freq='90D'),
        'vote_average': np.random.uniform(5, 10, 100),
        'vote_count': np.random.randint(100, 10000, 100),
        'popularity': np.random.uniform(10, 500, 100)
    }
    
    movies_df = pd.DataFrame(movies_data)
    return movies_df
    
    movies_df = pd.DataFrame(movies_data)
    return movies_df

def train_models():
    """Train all recommendation models"""
    print("\n" + "="*70)
    print("🎬 MOVIE RECOMMENDER SYSTEM - MODEL TRAINING")
    print("="*70)
    
    # Create models directory
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    
    # Create sample data
    movies_df = create_sample_data()
    print(f"✅ Sample data created: {len(movies_df)} movies")
    
    # ========== TRAIN CONTENT-BASED MODEL ==========
    print("\n📊 Training Content-Based Recommendation Model...")
    try:
        tfidf = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            min_df=1,
            max_df=0.9
        )
        
        tfidf_matrix = tfidf.fit_transform(movies_df['overview'].fillna(''))
        similarity_matrix = linear_kernel(tfidf_matrix, tfidf_matrix)
        
        content_model_data = {
            'similarity_matrix': similarity_matrix,
            'movies_df': movies_df,
            'tfidf_vectorizer': tfidf,
            'movie_ids': movies_df['id'].values,
            'movie_titles': movies_df['title'].values
        }
        
        with open(models_dir / 'content_based_model.pkl', 'wb') as f:
            pickle.dump(content_model_data, f)
        
        print(f"✅ Content-based model trained successfully!")
        print(f"   - Similarity matrix shape: {similarity_matrix.shape}")
        print(f"   - Saved to: models/content_based_model.pkl")
        
    except Exception as e:
        print(f"❌ Error training content-based model: {e}")
        return False
    
    # ========== TRAIN COLLABORATIVE FILTERING MODEL ==========
    print("\n📊 Training Collaborative Filtering Model...")
    try:
        # Create sample user-item ratings matrix
        np.random.seed(42)
        n_users = 50
        n_movies = len(movies_df)
        
        user_item_matrix = np.random.choice([0, 1, 2, 3, 4, 5], size=(n_users, n_movies), p=[0.7, 0.05, 0.05, 0.05, 0.075, 0.075])
        
        # Train KNN model
        model = NearestNeighbors(n_neighbors=min(5, n_users-1), metric='cosine', n_jobs=-1)
        model.fit(user_item_matrix)
        
        collab_model_data = {
            'model': model,
            'user_item_matrix': user_item_matrix,
            'movies_df': movies_df,
            'movie_ids': movies_df['id'].values,
            'movie_titles': movies_df['title'].values
        }
        
        with open(models_dir / 'collaborative.pkl', 'wb') as f:
            pickle.dump(collab_model_data, f)
        
        print(f"✅ Collaborative filtering model trained successfully!")
        print(f"   - User-item matrix shape: {user_item_matrix.shape}")
        print(f"   - Saved to: models/collaborative.pkl")
        
    except Exception as e:
        print(f"❌ Error training collaborative model: {e}")
        return False
    
    # ========== CREATE CLEAN MOVIES PICKLE ==========
    print("\n📊 Creating clean movies database...")
    try:
        with open(models_dir / 'clean_movies.pkl', 'wb') as f:
            pickle.dump(movies_df, f)
        
        print(f"✅ Clean movies database created!")
        print(f"   - Total movies: {len(movies_df)}")
        print(f"   - Saved to: models/clean_movies.pkl")
        
    except Exception as e:
        print(f"❌ Error creating movies database: {e}")
        return False
    
    print("\n" + "="*70)
    print("✅ ALL MODELS TRAINED SUCCESSFULLY!")
    print("="*70)
    print("\n🎯 Next steps:")
    print("   1. Restart your Streamlit app: streamlit run streamlit_app.py")
    print("   2. Create a new account and login")
    print("   3. Enjoy the movie recommendations!")
    print("\n")
    
    return True

if __name__ == "__main__":
    success = train_models()
    exit(0 if success else 1)
