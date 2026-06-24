"""
Feature Engineering and Recommendation Models
Implements: Content-Based, Collaborative Filtering, Matrix Factorization, Hybrid
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors
import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class FeatureEngineer:
    """Create features for content-based and collaborative filtering"""
    
    def __init__(self):
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.movie_features = None
        
    def create_tfidf_features(self, movies_df: pd.DataFrame, 
                             text_column: str = 'overview', 
                             max_features: int = 5000) -> np.ndarray:
        """
        Create TF-IDF vectors from movie overviews
        
        Args:
            movies_df: DataFrame containing movie data
            text_column: Column name to vectorize
            max_features: Maximum number of TF-IDF features
            
        Returns:
            TF-IDF sparse matrix
        """
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(
            movies_df[text_column].fillna('')
        )
        
        print(f"✓ TF-IDF features created: {self.tfidf_matrix.shape}")
        return self.tfidf_matrix
    
    def create_genre_features(self, movies_df: pd.DataFrame) -> np.ndarray:
        """
        Create one-hot encoded genre features
        """
        genre_columns = [col for col in movies_df.columns if col.startswith('genre_')]
        genre_matrix = movies_df[genre_columns].values
        
        print(f"✓ Genre features created: {genre_matrix.shape}")
        return genre_matrix
    
    def create_combined_features(self, tfidf_matrix: np.ndarray, 
                                genre_matrix: np.ndarray, 
                                tfidf_weight: float = 0.8) -> np.ndarray:
        """
        Combine TF-IDF and genre features
        """
        # Convert sparse TF-IDF to dense
        tfidf_dense = tfidf_matrix.toarray()
        
        # Normalize both matrices
        tfidf_normalized = tfidf_dense / (np.linalg.norm(tfidf_dense, axis=1, keepdims=True) + 1e-10)
        genre_normalized = genre_matrix / (np.linalg.norm(genre_matrix, axis=1, keepdims=True) + 1e-10)
        
        # Combine with weights
        combined = (tfidf_weight * tfidf_normalized + 
                   (1 - tfidf_weight) * genre_normalized)
        
        print(f"✓ Combined features created: {combined.shape}")
        return combined


class ContentBasedRecommender:
    """Content-based recommendation using TF-IDF and cosine similarity"""
    
    def __init__(self, movies_df: pd.DataFrame):
        self.movies_df = movies_df.reset_index(drop=True)
        self.similarity_matrix = None
        self.feature_matrix = None
        
    def fit(self, feature_matrix: np.ndarray):
        """
        Fit the content-based recommender
        
        Args:
            feature_matrix: Feature matrix (movies × features)
        """
        self.feature_matrix = feature_matrix
        
        # Calculate cosine similarity
        self.similarity_matrix = cosine_similarity(feature_matrix)
        
        print(f"✓ Content-based model fitted")
    
    def recommend(self, movie_id: int, n_recommendations: int = 10) -> List[Dict]:
        """
        Get content-based recommendations for a movie
        
        Args:
            movie_id: ID of the query movie
            n_recommendations: Number of recommendations
            
        Returns:
            List of recommended movies with scores
        """
        # Find movie index
        movie_indices = self.movies_df[self.movies_df['id'] == movie_id].index
        
        if len(movie_indices) == 0:
            return []
        
        movie_idx = movie_indices[0]
        
        # Get similarity scores
        similarity_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        
        # Sort by similarity (excluding the movie itself)
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:n_recommendations+1]
        
        # Get movie indices and scores
        indices = [i[0] for i in similarity_scores]
        scores = [i[1] for i in similarity_scores]
        
        # Create result list
        results = []
        for idx, score in zip(indices, scores):
            results.append({
                'id': self.movies_df.loc[idx, 'id'],
                'title': self.movies_df.loc[idx, 'title'],
                'score': float(score),
                'poster_path': self.movies_df.loc[idx, 'poster_path']
            })
        
        return results


class CollaborativeFilteringRecommender:
    """Collaborative filtering using user-item interactions"""
    
    def __init__(self, user_item_matrix: pd.DataFrame, movies_df: pd.DataFrame):
        self.user_item_matrix = user_item_matrix.fillna(0)
        self.movies_df = movies_df
        self.model = None
        
    def fit(self, n_neighbors: int = 20):
        """
        Fit KNN-based collaborative filtering model
        
        Args:
            n_neighbors: Number of neighbors to consider
        """
        self.model = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric='cosine',
            n_jobs=-1
        )
        self.model.fit(self.user_item_matrix)
        
        print(f"✓ Collaborative filtering model fitted")
    
    def recommend(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """
        Get collaborative filtering recommendations for a user
        
        Args:
            user_id: ID of the user
            n_recommendations: Number of recommendations
            
        Returns:
            List of recommended movies
        """
        if user_id not in self.user_item_matrix.index:
            return []
        
        user_idx = list(self.user_item_matrix.index).index(user_id)
        
        # Find similar users
        distances, indices = self.model.kneighbors(
            self.user_item_matrix.iloc[user_idx:user_idx+1],
            n_neighbors=20
        )
        
        # Get movies rated by similar users
        similar_user_indices = indices[0][1:]  # Exclude the user itself
        
        # Aggregate ratings from similar users
        recommended_movies = {}
        user_rated_movies = set(self.user_item_matrix.columns[
            self.user_item_matrix.iloc[user_idx] > 0
        ])
        
        for sim_user_idx in similar_user_indices:
            sim_user_id = self.user_item_matrix.index[sim_user_idx]
            sim_user_ratings = self.user_item_matrix.loc[sim_user_id]
            
            for movie_id, rating in sim_user_ratings[sim_user_ratings > 0].items():
                if movie_id not in user_rated_movies:
                    recommended_movies[movie_id] = recommended_movies.get(movie_id, 0) + rating
        
        # Sort and get top recommendations
        top_movies = sorted(recommended_movies.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        
        results = []
        for movie_id, score in top_movies:
            movie_data = self.movies_df[self.movies_df['id'] == int(movie_id)]
            if len(movie_data) > 0:
                results.append({
                    'id': movie_id,
                    'title': movie_data.iloc[0]['title'],
                    'score': float(score),
                    'poster_path': movie_data.iloc[0].get('poster_path', '')
                })
        
        return results


class MatrixFactorizationRecommender:
    """Matrix factorization using SVD"""
    
    def __init__(self, user_item_matrix: pd.DataFrame, movies_df: pd.DataFrame):
        self.user_item_matrix = user_item_matrix.fillna(0)
        self.movies_df = movies_df
        self.svd = None
        self.user_factors = None
        self.item_factors = None
        
    def fit(self, n_factors: int = 50):
        """
        Fit SVD-based matrix factorization
        
        Args:
            n_factors: Number of latent factors
        """
        self.svd = TruncatedSVD(n_components=min(n_factors, min(self.user_item_matrix.shape)-1))
        
        # Fit on transposed matrix to get item factors
        self.item_factors = self.svd.fit_transform(self.user_item_matrix.T)
        
        # Get user factors
        self.user_factors = self.user_item_matrix @ self.svd.components_.T
        
        print(f"✓ Matrix factorization model fitted (variance explained: {self.svd.explained_variance_ratio_.sum():.2%})")
    
    def recommend(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """
        Get recommendations using matrix factorization
        """
        if user_id not in self.user_item_matrix.index:
            return []
        
        user_idx = list(self.user_item_matrix.index).index(user_id)
        user_factor = self.user_factors[user_idx]
        
        # Predict ratings
        predicted_ratings = user_factor @ self.item_factors.T
        
        # Get movies the user hasn't rated
        user_rated_movies = set(self.user_item_matrix.columns[
            self.user_item_matrix.iloc[user_idx] > 0
        ])
        
        # Get top recommendations
        recommendations = []
        for movie_id, rating in enumerate(predicted_ratings):
            if movie_id not in user_rated_movies:
                recommendations.append((movie_id, rating))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for movie_idx, score in recommendations[:n_recommendations]:
            if movie_idx < len(self.movies_df):
                movie = self.movies_df.iloc[movie_idx]
                results.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'score': float(score),
                    'poster_path': movie.get('poster_path', '')
                })
        
        return results


class HybridRecommender:
    """Hybrid recommender combining multiple approaches"""
    
    def __init__(self, content_based: ContentBasedRecommender, 
                 collaborative: CollaborativeFilteringRecommender,
                 matrix_fact: MatrixFactorizationRecommender):
        self.content_based = content_based
        self.collaborative = collaborative
        self.matrix_fact = matrix_fact
        
    def recommend(self, movie_id: Optional[int] = None, user_id: Optional[int] = None,
                 n_recommendations: int = 10,
                 weights: Tuple[float, float, float] = (0.4, 0.3, 0.3)) -> List[Dict]:
        """
        Get hybrid recommendations
        
        Args:
            movie_id: Movie ID for content-based recommendations
            user_id: User ID for collaborative filtering
            n_recommendations: Number of recommendations
            weights: Weights for (content-based, collaborative, matrix_fact)
            
        Returns:
            List of recommended movies
        """
        recommendations = {}
        
        # Content-based recommendations
        if movie_id is not None:
            content_recs = self.content_based.recommend(movie_id, n_recommendations * 2)
            for rec in content_recs:
                movie_id_val = rec['id']
                if movie_id_val not in recommendations:
                    recommendations[movie_id_val] = {'title': rec['title'], 
                                                     'poster_path': rec['poster_path'],
                                                     'score': 0}
                recommendations[movie_id_val]['score'] += rec['score'] * weights[0]
        
        # Collaborative filtering recommendations
        if user_id is not None:
            collab_recs = self.collaborative.recommend(user_id, n_recommendations * 2)
            for rec in collab_recs:
                movie_id_val = rec['id']
                if movie_id_val not in recommendations:
                    recommendations[movie_id_val] = {'title': rec['title'],
                                                     'poster_path': rec['poster_path'],
                                                     'score': 0}
                recommendations[movie_id_val]['score'] += rec['score'] * weights[1]
            
            # Matrix factorization recommendations
            mf_recs = self.matrix_fact.recommend(user_id, n_recommendations * 2)
            for rec in mf_recs:
                movie_id_val = rec['id']
                if movie_id_val not in recommendations:
                    recommendations[movie_id_val] = {'title': rec['title'],
                                                     'poster_path': rec['poster_path'],
                                                     'score': 0}
                recommendations[movie_id_val]['score'] += rec['score'] * weights[2]
        
        # Sort and return top recommendations
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1]['score'], reverse=True)
        
        results = []
        for movie_id_val, data in sorted_recs[:n_recommendations]:
            results.append({
                'id': movie_id_val,
                'title': data['title'],
                'score': data['score'],
                'poster_path': data['poster_path']
            })
        
        return results


def save_models(content_model: ContentBasedRecommender,
               collab_model: CollaborativeFilteringRecommender,
               matrix_model: MatrixFactorizationRecommender,
               output_path: str):
    """Save trained models to disk"""
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'content_based_model.pkl', 'wb') as f:
        pickle.dump(content_model, f)
    
    with open(output_dir / 'collaborative_model.pkl', 'wb') as f:
        pickle.dump(collab_model, f)
    
    with open(output_dir / 'matrix_fact_model.pkl', 'wb') as f:
        pickle.dump(matrix_model, f)
    
    print(f"✓ Models saved to {output_dir}")


def load_models(model_path: str) -> Tuple[ContentBasedRecommender, 
                                          CollaborativeFilteringRecommender,
                                          MatrixFactorizationRecommender]:
    """Load trained models from disk"""
    model_dir = Path(model_path)
    
    with open(model_dir / 'content_based_model.pkl', 'rb') as f:
        content_model = pickle.load(f)
    
    with open(model_dir / 'collaborative_model.pkl', 'rb') as f:
        collab_model = pickle.load(f)
    
    with open(model_dir / 'matrix_fact_model.pkl', 'rb') as f:
        matrix_model = pickle.load(f)
    
    return content_model, collab_model, matrix_model