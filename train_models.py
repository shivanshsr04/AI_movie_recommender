"""
Model Training Script
Trains all recommendation models and saves them for production use
"""

import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path
from typing import Tuple
import warnings
warnings.filterwarnings('ignore')

# Import custom modules (would be in src/ in actual project)
# from src.data_loader import DataLoader, load_and_preprocess_data
# from src.recommender_models import (
#     FeatureEngineer, ContentBasedRecommender, 
#     CollaborativeFilteringRecommender, MatrixFactorizationRecommender,
#     HybridRecommender, save_models
# )

class ModelTrainer:
    """Train all recommendation models"""
    
    def __init__(self, data_path: str, model_output_path: str = 'models'):
        self.data_path = Path(data_path)
        self.model_path = Path(model_output_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        self.movies = None
        self.ratings = None
        self.content_model = None
        self.collab_model = None
        self.matrix_model = None
        self.hybrid_model = None
    
    def load_data(self) -> bool:
        """Load movie and rating data"""
        try:
            print("Loading data...")
            
            # Load movies
            self.movies = pd.read_csv(self.data_path / 'movies_metadata.csv', low_memory=False)
            print(f"✓ Movies loaded: {len(self.movies)} records")
            
            # Load ratings
            self.ratings = pd.read_csv(self.data_path / 'ratings_small.csv')
            print(f"✓ Ratings loaded: {len(self.ratings)} records")
            
            return True
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return False
    
    def preprocess_data(self) -> bool:
        """Preprocess movies and ratings data"""
        try:
            print("\nPreprocessing data...")
            
            # 1. FIX CORRUPTED ROWS: Force 'id' to be numeric, turning text into NaN, then drop the NaNs
            self.movies['id'] = pd.to_numeric(self.movies['id'], errors='coerce')
            self.movies = self.movies.dropna(subset=['id'])
            
            # Convert release_date to datetime
            self.movies['release_date'] = pd.to_datetime(self.movies['release_date'], errors='coerce')
            self.movies['year'] = self.movies['release_date'].dt.year
            
            # Handle missing values
            self.movies['genres'] = self.movies['genres'].fillna('[]')
            self.movies['overview'] = self.movies['overview'].fillna('')
            self.movies['title'] = self.movies['title'].fillna('Unknown')
            
            # 2. SAFELY CONVERT NUMBERS: Use pd.to_numeric instead of direct .astype()
            self.movies['vote_average'] = pd.to_numeric(self.movies['vote_average'], errors='coerce').fillna(0).astype(float)
            self.movies['vote_count'] = pd.to_numeric(self.movies['vote_count'], errors='coerce').fillna(0).astype(int)
            self.movies['popularity'] = pd.to_numeric(self.movies['popularity'], errors='coerce').fillna(0).astype(float)
            
            # Remove duplicates
            self.movies = self.movies.drop_duplicates(subset=['id'], keep='first')
            self.movies = self.movies.reset_index(drop=True)
            
            print(f"✓ Data preprocessed: {len(self.movies)} valid movies")
            return True
        except Exception as e:
            print(f"✗ Error preprocessing data: {e}")
            return False
        
    def train_content_based(self) -> bool:
        """Train content-based recommendation model"""
        try:
            print("\nTraining Content-Based Model...")
            
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import linear_kernel
            
            # The Fix: Only use the top 10,000 popular movies to prevent crashing
            print("Grabbing the top 10,000 movies...")
            content_movies = self.movies.sort_values('popularity', ascending=False).head(10000).reset_index(drop=True)
            
            # Create TF-IDF features from overviews
            tfidf = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8
            )
            
            print("Building TF-IDF matrix...")
            tfidf_matrix = tfidf.fit_transform(content_movies['overview'].fillna(''))
            
            # Calculate similarity matrix safely
            print("Calculating similarity matrix...")
            similarity_matrix = linear_kernel(tfidf_matrix, tfidf_matrix)
            
            # Save model components
            model_data = {
                'similarity_matrix': similarity_matrix,
                'movies_df': content_movies,
                'tfidf_vectorizer': tfidf
            }
            
            with open(self.model_path / 'content_based.pkl', 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"✓ Content-based model trained (matrix shape: {similarity_matrix.shape})")
            return True
        except Exception as e:
            print(f"✗ Error training content-based model: {e}")
            return False
    
    def train_collaborative(self) -> bool:
        """Train collaborative filtering model"""
        try:
            print("\nTraining Collaborative Filtering Model...")
            
            from sklearn.neighbors import NearestNeighbors
            
            # Create user-item matrix
            user_item_matrix = self.ratings.pivot_table(
                index='userId',
                columns='movieId',
                values='rating'
            )
            
            user_item_matrix = user_item_matrix.fillna(0)
            
            # Train KNN model
            model = NearestNeighbors(n_neighbors=20, metric='cosine', n_jobs=-1)
            model.fit(user_item_matrix)
            
            # Save model
            model_data = {
                'model': model,
                'user_item_matrix': user_item_matrix,
                'movies_df': self.movies
            }
            
            with open(self.model_path / 'collaborative.pkl', 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"✓ Collaborative model trained (matrix shape: {user_item_matrix.shape})")
            return True
        except Exception as e:
            print(f"✗ Error training collaborative model: {e}")
            return False
    
    def train_matrix_factorization(self) -> bool:
        """Train matrix factorization model using SVD"""
        try:
            print("\nTraining Matrix Factorization Model...")
            
            from sklearn.decomposition import TruncatedSVD
            
            # Create user-item matrix
            user_item_matrix = self.ratings.pivot_table(
                index='userId',
                columns='movieId',
                values='rating'
            )
            
            user_item_matrix = user_item_matrix.fillna(0)
            
            # Apply SVD
            svd = TruncatedSVD(n_components=50, random_state=42)
            user_factors = svd.fit_transform(user_item_matrix)
            item_factors = svd.components_.T
            
            # Save model
            model_data = {
                'user_factors': user_factors,
                'item_factors': item_factors,
                'user_item_matrix': user_item_matrix,
                'movies_df': self.movies,
                'explained_variance': svd.explained_variance_ratio_.sum()
            }
            
            with open(self.model_path / 'matrix_factorization.pkl', 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"✓ Matrix factorization trained (variance explained: {svd.explained_variance_ratio_.sum():.2%})")
            return True
        except Exception as e:
            print(f"✗ Error training matrix factorization: {e}")
            return False
    
    def train_all_models(self) -> bool:
        """Train all models in sequence"""
        print("=" * 60)
        print("🎬 MOVIE RECOMMENDER SYSTEM - MODEL TRAINING")
        print("=" * 60)
        
        # Load and preprocess
        if not self.load_data():
            return False
        
        if not self.preprocess_data():
            return False
        
        # Train models
        success = True
        success &= self.train_content_based()
        success &= self.train_collaborative()
        success &= self.train_matrix_factorization()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ ALL MODELS TRAINED SUCCESSFULLY!")
            print("=" * 60)
            self.save_metadata()
            return True
        else:
            print("\n" + "=" * 60)
            print("❌ SOME MODELS FAILED TO TRAIN")
            print("=" * 60)
            return False
    
    def save_metadata(self):
        """Save metadata about the models"""
        metadata = {
            'num_movies': len(self.movies),
            'num_ratings': len(self.ratings),
            'models_trained': ['content_based', 'collaborative', 'matrix_factorization'],
            'model_path': str(self.model_path)
        }
        
        with open(self.model_path / 'metadata.pkl', 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"\n📊 Metadata saved:")
        print(f"   - Total movies: {metadata['num_movies']}")
        print(f"   - Total ratings: {metadata['num_ratings']}")
        print(f"   - Models saved in: {metadata['model_path']}")


def main():
    """Main training function"""
    # Set paths
    DATA_PATH = 'data/raw'  # Update with your data path
    MODEL_OUTPUT_PATH = 'models'
    
    # Create trainer
    trainer = ModelTrainer(DATA_PATH, MODEL_OUTPUT_PATH)
    
    # Train models
    success = trainer.train_all_models()
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)