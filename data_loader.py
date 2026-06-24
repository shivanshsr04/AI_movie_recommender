"""
Data Loader Module - Load and preprocess movie recommendation data
"""
import pandas as pd
import numpy as np
import json
import pickle
from pathlib import Path
from typing import Tuple, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class DataLoader:
    """Load and preprocess movie data for recommendation systems"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.movies = None
        self.ratings = None
        self.credits = None
        self.keywords = None
        self.links = None
        
    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load all necessary data files
        
        Returns:
            Tuple of (movies, ratings, credits, keywords) DataFrames
        """
        try:
            # Load movies metadata
            self.movies = pd.read_csv(self.data_path / 'movies_metadata.csv', low_memory=False)
            print(f"✓ Movies loaded: {len(self.movies)} records")
            
            # Load ratings (use small version for faster processing)
            self.ratings = pd.read_csv(self.data_path / 'ratings_small.csv')
            print(f"✓ Ratings loaded: {len(self.ratings)} records")
            
            # Load credits
            self.credits = pd.read_csv(self.data_path / 'credits.csv')
            print(f"✓ Credits loaded: {len(self.credits)} records")
            
            # Load keywords
            self.keywords = pd.read_csv(self.data_path / 'keywords.csv')
            print(f"✓ Keywords loaded: {len(self.keywords)} records")
            
            return self.movies, self.ratings, self.credits, self.keywords
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Data file not found: {e}")
    
    def preprocess_movies(self) -> pd.DataFrame:
        """
        Preprocess movies data
        - Handle missing values
        - Extract relevant features
        - Clean data types
        """
        df = self.movies.copy()
        
        # Convert release_date to datetime
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        
        # Extract year
        df['year'] = df['release_date'].dt.year
        
        # Handle missing values
        df['genres'] = df['genres'].fillna('[]')
        df['overview'] = df['overview'].fillna('')
        df['title'] = df['title'].fillna('Unknown')
        df['vote_average'] = df['vote_average'].fillna(0)
        df['vote_count'] = df['vote_count'].fillna(0)
        df['popularity'] = df['popularity'].fillna(0)
        
        # Remove rows with missing movie ID or release year
        df = df.dropna(subset=['id'])
        df = df[df['id'].notna()]
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['id'], keep='first')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        print(f"✓ Movies preprocessed: {len(df)} valid records")
        return df
    
    def extract_genres(self) -> pd.DataFrame:
        """
        Extract genre information from JSON-like string format
        """
        def safe_literal_eval(x):
            try:
                if isinstance(x, str):
                    import ast
                    return ast.literal_eval(x)
                return x if isinstance(x, list) else []
            except:
                return []
        
        self.movies['genres_list'] = self.movies['genres'].apply(
            lambda x: [genre['name'] for genre in safe_literal_eval(x)]
        )
        
        # Create genre columns
        all_genres = []
        for genres in self.movies['genres_list']:
            all_genres.extend(genres)
        
        unique_genres = list(set(all_genres))
        
        for genre in unique_genres:
            self.movies[f'genre_{genre.lower().replace(" ", "_")}'] = \
                self.movies['genres_list'].apply(lambda x: 1 if genre in x else 0)
        
        print(f"✓ {len(unique_genres)} genres extracted")
        return self.movies
    
    def merge_data(self) -> pd.DataFrame:
        """
        Merge movies with credits and keywords
        """
        # Merge with credits
        df = self.movies.merge(self.credits, left_on='id', right_on='id', how='left')
        
        # Merge with keywords
        df = df.merge(self.keywords, left_on='id', right_on='id', how='left')
        
        # Fill NaN values
        df['cast'] = df['cast'].fillna('[]')
        df['crew'] = df['crew'].fillna('[]')
        df['keywords'] = df['keywords'].fillna('[]')
        
        print(f"✓ Data merged successfully")
        return df
    
    def get_user_movie_matrix(self, min_ratings: int = 5) -> Tuple[pd.DataFrame, Dict[int, int]]:
        """
        Create user-item interaction matrix for collaborative filtering
        
        Args:
            min_ratings: Minimum number of ratings for a user to be included
            
        Returns:
            Tuple of (user_movie_matrix, movie_id_mapping)
        """
        # Filter users with minimum ratings
        user_counts = self.ratings['userId'].value_counts()
        valid_users = user_counts[user_counts >= min_ratings].index
        ratings_filtered = self.ratings[self.ratings['userId'].isin(valid_users)]
        
        # Create pivot table
        user_movie_matrix = ratings_filtered.pivot_table(
            index='userId',
            columns='movieId',
            values='rating'
        )
        
        # Create movie ID mapping
        movie_id_mapping = {mid: i for i, mid in enumerate(self.movies['id'].values)}
        
        print(f"✓ User-item matrix created: {user_movie_matrix.shape}")
        return user_movie_matrix, movie_id_mapping
    
    def get_movie_features(self) -> pd.DataFrame:
        """
        Get clean movie features for recommendation
        """
        features = self.movies[['id', 'title', 'overview', 'genres_list', 'vote_average', 
                                 'vote_count', 'popularity', 'poster_path', 'year']].copy()
        
        # Remove rows with no overview or title
        features = features[(features['overview'] != '') & (features['title'] != 'Unknown')]
        features = features.reset_index(drop=True)
        
        print(f"✓ Movie features extracted: {len(features)} records")
        return features
    
    def save_processed_data(self, output_path: str):
        """Save preprocessed data for later use"""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save movies
        self.movies.to_csv(output_dir / 'movies_processed.csv', index=False)
        
        # Save ratings
        self.ratings.to_csv(output_dir / 'ratings_processed.csv', index=False)
        
        print(f"✓ Processed data saved to {output_dir}")


# Utility function for quick data loading
def load_and_preprocess_data(data_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Quick function to load and preprocess all data
    
    Args:
        data_path: Path to data directory
        
    Returns:
        Tuple of (movies_df, ratings_df)
    """
    loader = DataLoader(data_path)
    loader.load_all_data()
    movies = loader.preprocess_movies()
    loader.extract_genres()
    loader.merge_data()
    ratings = loader.ratings
    
    return movies, ratings