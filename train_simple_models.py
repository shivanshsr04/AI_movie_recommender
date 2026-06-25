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
    
    # Sample movies data
    movies_data = {
        'id': list(range(1, 101)),
        'title': [
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
        ],
        'overview': [
            'A skilled thief who steals corporate secrets through dream-sharing technology.',
            'A computer hacker learns about the true nature of reality.',
            'A team of astronauts travel through a wormhole to find a new habitable planet.',
            'Batman fights to save Gotham City from the Joker.',
            'The lives of several mobsters intertwine in four tales of violence.',
            'A man with a low IQ has big dreams and achieves them.',
            'A banker wrongly imprisoned forms an unlikely friendship.',
            'An insomniac office worker and a soap maker form an underground fighting club.',
            'The aging patriarch of an organized crime dynasty.',
            'A marine on an alien world helps fight an invading corporation.',
            'A love story unfolds aboard the ill-fated RMS Titanic.',
            'Dinosaurs are brought back to life on a remote island.',
            'Superheroes unite to fight an alien invasion.',
            'A billionaire playboy creates a powered suit of armor.',
            'A soldier is brought back to life to fight a terrorist organization.',
            'The God of Thunder seeks to stop an alien invasion.',
            'A king fights to save his nation from invaders.',
            'A teenager bitten by a radioactive spider becomes a superhero.',
            'A neurosurgeon discovers mystical arts.',
            'A group of misfits comes together to save the galaxy.',
            'A mercenary with no sense of pain becomes a hero.',
            'An aging mutant must protect a young mutant.',
            'A team of mutants fight against discrimination.',
            'Superheroes must save the world from evil.',
            'A thief is recruited to help stop a threat.',
            'A lion prince flees his kingdom to find his place.',
            'Two sisters with magical powers must save their kingdom.',
            'A spirited princess sets out on a daring ocean voyage.',
            'A skeleton must save Christmas.',
            'A cowboy must deal with competition from a new space ranger.',
            'A clownfish searches for his lost son.',
            'A girl experiences emotions and memories.',
            'A robot must save the world.',
            'A robot must preserve the last plant on Earth.',
            'Monsters scare children to harvest their screams.',
            'A superhero family must save the world.',
            'A rat dreams of becoming a chef.',
            'A car must find his place in the world.',
            'An ant dreams of becoming a warrior.',
            'A princess must be brave.',
            'A young wizard attends a magical school.',
            'A teenager must survive deadly games.',
            'A human falls in love with a vampire.',
            'A teenager discovers his godly heritage.',
            'A girl must survive in a dystopian world.',
            'A teen must escape a faction-based society.',
            'A teen must escape a deadly maze.',
            'A soldier fights a powerful entity.',
            'A cop must find a killer in a cyberpunk world.',
            'A cyborg is sent back in time.',
            'A cop fights futuristic criminals.',
            'An operative is recruited for a special mission.',
            'A looper must kill his future self.',
            'A soldier must relive the same day to defeat an alien invasion.',
            'A warrior seeks revenge in a post-apocalyptic world.',
            'An assassin seeks vengeance.',
            'A spy must stop an enemy agent.',
            'An agent is sent on covert operations.',
            'An assassin must find his identity.',
            'A spy must complete dangerous missions.',
            'A con artist must pull off a heist.',
            'Thieves must plan a casino heist.',
            'A detective must solve mysterious cases.',
            'A lady must stop robbers.',
            'An archaeologist seeks treasure and adventure.',
            'A mummy is unleashed and must be stopped.',
            'An adventurer seeks mystical artifacts.',
            'A treasure hunter seeks fortune.',
            'An explorer seeks a legendary city.',
            'A diver must survive dangerous waters.',
            'A criminal must survive a deadly island.',
            'A couple falls in love during a war.',
            'Two lovers are separated by circumstance.',
            'A teenage girl discovers her sexuality.',
            'Two boys explore their feelings.',
            'Two men form an unexpected bond.',
            'A woman falls in love with another woman.',
            'A young man discovers his sexuality.',
            'A boy searches for love and acceptance.',
            'A young man searches for identity and love.',
            'A young man discovers the world around him.',
            'A musician and dancer fall in love.',
            'A woman is taken to a magical world.',
            'A woman discovers her unique powers.',
            'A woman redefines her life and love.'
        ] + ['A compelling story'] * 17,
        'genres': ['Action'] * 25 + ['Animation'] * 20 + ['Adventure'] * 20 + ['Romance'] * 15 + ['Drama'] * 20,
        'release_date': pd.date_range(start='1999-01-01', periods=100, freq='90D'),
        'vote_average': np.random.uniform(5, 10, 100),
        'vote_count': np.random.randint(100, 10000, 100),
        'popularity': np.random.uniform(10, 500, 100)
    }
    
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
