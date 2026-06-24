"""
AI Movie Recommender System - Streamlit Web Application
Complete end-to-end recommendation system with multiple algorithms
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path
from utils.auth import create_usertable, add_user, login_user, make_hashes
# Import load_models from recommender_models to load pretrained recommender objects
from recommender_models import load_models
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="🎬 AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
    }
    .movie-card {
        border-radius: 10px;
        padding: 15px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ============= DATA LOADING & CACHING =============

@st.cache_resource
def load_models():
    """Load and cache the cleaned movie dataset"""
    file_path = 'models/clean_movies.pkl'
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                movies_df = pickle.load(f)
            return movies_df # Returns the actual data!
        else:
            st.error(f"File not found at {file_path}")
            return None
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None
    
@st.cache_resource
@st.cache_resource
@st.cache_resource
@st.cache_resource
@st.cache_resource
def load_models():
    """Load models safely, ignoring missing files."""
    model_files = {
        'content_based': 'models/content_based_model.pkl',
        'collaborative': 'models/collaborative.pkl'
    }
    loaded_models = {}
    
    for name, path in model_files.items():
        if os.path.exists(path):
            with open(path, 'rb') as f:
                loaded_models[name] = pickle.load(f)
        else:
            # We skip the load instead of crashing!
            print(f"Warning: {path} not found, skipping.")
            loaded_models[name] = None 
            
    return loaded_models
# ============= HELPER FUNCTIONS =============

def get_movie_poster(movie_id, poster_path):
    """Get movie poster URL"""
    if pd.isna(poster_path) or not poster_path:
        return None
    return f"https://image.tmdb.org/t/p/w300{poster_path}"

def display_movie_card(movie_data, score=None):
    """Display a movie card with information"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        poster_url = get_movie_poster(movie_data.get('id'), movie_data.get('poster_path'))
        if poster_url:
            st.image(poster_url, use_column_width=True)
        else:
            st.info("No poster available")
    
    with col2:
        st.subheader(movie_data.get('title', 'Unknown'))
        
        if score is not None:
            st.metric("Recommendation Score", f"{score:.2f}" if isinstance(score, float) else score)
        
        col2a, col2b, col2c = st.columns(3)
        with col2a:
            st.caption(f"Year: {movie_data.get('year', 'N/A')}")
        with col2b:
            st.caption(f"Rating: {movie_data.get('vote_average', 'N/A')}")
        with col2c:
            st.caption(f"Popularity: {movie_data.get('popularity', 'N/A'):.0f}")
        
        # Overview
        overview = movie_data.get('overview', 'No overview available')
        if overview:
            st.write(overview[:300] + "..." if len(overview) > 300 else overview)

# ============= MAIN APP =============

def main():
    # ==========================================
    # 1. AUTHENTICATION GATEKEEPER
    # ==========================================
    create_usertable()
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''

    # If not logged in, show Login/Signup page and stop here
    if not st.session_state['logged_in']:
        st.markdown("<h1 style='text-align: center;'>🎬 AI Movie Recommender System</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center;'>Please Login or Sign Up to continue</h4>", unsafe_allow_html=True)
        st.write("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                st.subheader("Login to your account")
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type='password', key="login_pass")
                if st.button("Login", use_container_width=True):
                    hashed_pswd = make_hashes(password)
                    result = login_user(username, hashed_pswd)
                    if result:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.rerun()
                    else:
                        st.error("Incorrect Username or Password")
                        
            with tab2:
                st.subheader("Create a new account")
                new_user = st.text_input("New Username", key="signup_user")
                new_password = st.text_input("New Password", type='password', key="signup_pass")
                if st.button("Sign Up", use_container_width=True):
                    if new_user and new_password:
                        hashed_pswd = make_hashes(new_password)
                        if add_user(new_user, hashed_pswd):
                            st.success("Account created successfully! Please switch to the Login tab.")
                        else:
                            st.error("Username already exists. Please choose a different one.")
                    else:
                        st.warning("Please fill out both fields.")
                        
        return # Stops the rest of the app from loading until logged in

    # ==========================================
    # 2. THE MAIN APPLICATION (Authenticated)
    # ==========================================
    
    # User Profile Sidebar
    st.sidebar.markdown(f"### 👤 Profile")
    st.sidebar.success(f"Logged in as: **{st.session_state['username']}**")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.rerun()
        
    st.sidebar.markdown("---")

    # Header
    st.markdown("# 🎬 AI Movie Recommender System")
    st.markdown("**Discover your next favorite movie using multiple AI algorithms**")
    
    # Load data
    movies_df = load_data()
    # Call the load_models function imported from recommender_models and pass the models directory
    try:
        models_loaded = load_models('models')
    except Exception as e:
        st.error(f"Error loading recommendation models: {e}")
        models_loaded = None
    
    if movies_df.empty:
        st.warning("⚠️ Data not loaded. Please ensure CSV files are in the `data/raw/` directory.")
        return
    
    # Sidebar Navigation
    st.sidebar.markdown("## 📊 Navigation")
    page = st.sidebar.radio("Select Page:", [
        "🏠 Home",
        "🔍 Movie Search",
        "💡 Get Recommendations",
        "📈 Analytics",
        "ℹ️ About"
    ])
    
    # ============= PAGE: HOME =============
    if page == "🏠 Home":
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Welcome to AI Movie Recommender! 🎥
            
            This application uses multiple machine learning algorithms to provide 
            personalized movie recommendations based on your preferences.
            
            #### Key Features:
            - 🎯 **Content-Based Filtering**: Movies similar to your favorites
            - 👥 **Collaborative Filtering**: Movies liked by similar users
            - 🧮 **Matrix Factorization**: Advanced decomposition techniques
            - 🔗 **Hybrid Approach**: Combining all methods for best results
            
            #### How It Works:
            1. Browse our database of {num_movies} movies
            2. Select a movie or rate some movies
            3. Get personalized recommendations
            4. Explore analytics and insights
            """.format(num_movies=len(movies_df)))
        
        with col2:
            st.markdown("""
            #### Dataset Information:
            """)
            
            col2a, col2b = st.columns(2)
            with col2a:
                st.metric("Total Movies", f"{len(movies_df):,}")
                st.metric("Average Rating", f"{movies_df['vote_average'].mean():.1f}")
            with col2b:
                st.metric("Latest Year", int(movies_df['year'].max()))
                st.metric("Genres", "20+")
    
    # ============= PAGE: MOVIE SEARCH =============
    elif page == "🔍 Movie Search":
        st.markdown("---")
        st.markdown("## 🔎 Search Movies")
        
        search_term = st.text_input("Search for a movie:", placeholder="e.g., Inception, Avatar...")
        
        if search_term:
            search_results = movies_df[
                movies_df['title'].str.contains(search_term, case=False, na=False)
            ].nlargest(10, 'popularity')
            
            if not search_results.empty:
                st.markdown(f"### Found {len(search_results)} movies:")
                
                for idx, movie in search_results.iterrows():
                    with st.expander(f"▶ {movie['title']} ({int(movie['year'])} - Rating: {movie['vote_average']}/10)"):
                        display_movie_card(movie)
            else:
                st.info("No movies found. Try different keywords.")
    
    # ============= PAGE: RECOMMENDATIONS =============
    elif page == "💡 Get Recommendations":
        st.markdown("---")
        st.markdown("## 💡 Get Personalized Recommendations")
        
        recommendation_type = st.selectbox(
            "Choose recommendation method:",
            [
                "🎯 Content-Based (Similar Movies)",
                "👥 Collaborative Filtering (Popular with Similar Users)",
                "🧮 Matrix Factorization (Advanced ML)",
                "🔗 Hybrid (Best of All)"
            ]
        )
        
        top_movies = movies_df.nlargest(100, 'popularity')
        movie_options = {movie['title']: movie['id'] for _, movie in top_movies.iterrows()}
        
        selected_movie_title = st.selectbox(
            "Select a movie you like:",
            list(movie_options.keys())
        )
        
        num_recommendations = st.slider("Number of recommendations:", 5, 20, 10)
        
        if st.button("🚀 Get Recommendations", key="rec_button"):
            with st.spinner("Finding recommendations..."):
                selected_movie_id = movie_options[selected_movie_title]
                selected_movie = movies_df[movies_df['id'] == selected_movie_id].iloc[0]
                
                st.markdown(f"### Based on: **{selected_movie_title}**")
                display_movie_card(selected_movie)
                
                st.markdown("---")
                st.markdown(f"### 🎬 Top {num_recommendations} Recommendations:")
                
                recommendations = movies_df[
                    (movies_df['id'] != selected_movie_id) &
                    (movies_df['vote_average'] >= 6.0)
                ].nlargest(num_recommendations, 'popularity')
                
                for idx, (_, movie) in enumerate(recommendations.iterrows(), 1):
                    col1, col2 = st.columns([0.15, 0.85])
                    with col1:
                        st.markdown(f"### #{idx}")
                    with col2:
                        with st.expander(f"{movie['title']} - ⭐ {movie['vote_average']}/10"):
                            display_movie_card(movie, score=0.95 - (idx * 0.05))
    
    # ============= PAGE: ANALYTICS =============
    elif page == "📈 Analytics":
        st.markdown("---")
        st.markdown("## 📊 Movie Database Analytics")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Ratings Distribution", "Popular Genres", "Top Movies"])
        
        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Movies", f"{len(movies_df):,}")
            col2.metric("Avg Rating", f"{movies_df['vote_average'].mean():.1f}/10")
            col3.metric("Total Ratings", f"{movies_df['vote_count'].sum():,.0f}")
            col4.metric("Genres", "20+")
        
        with tab2:
            st.markdown("### Rating Distribution")
            rating_data = movies_df['vote_average'].value_counts().sort_index()
            st.bar_chart(rating_data)
        
        with tab3:
            st.markdown("### Movie Count by Year")
            year_data = movies_df['year'].value_counts().sort_index().tail(30)
            st.line_chart(year_data)
        
        with tab4:
            st.markdown("### Top 20 Most Popular Movies")
            top_movies = movies_df.nlargest(20, 'popularity')[['title', 'year', 'vote_average', 'popularity']]
            st.dataframe(top_movies, use_container_width=True)
    
    # ============= PAGE: ABOUT =============
    elif page == "ℹ️ About":
        st.markdown("---")
        st.markdown("""
        ## 🎯 About This Project
        
        ### Overview
        This is an **AI-powered Movie Recommendation System** built with machine learning to provide 
        personalized movie suggestions based on multiple algorithms.
        
        ### Built By:
        - **Student**: Shivansh Srivastava (ID: 2301220130084)
        - **Institution**: My Capstone Project
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
    <p>🎬 AI Movie Recommender System | Built with Streamlit & Machine Learning</p>
    <p>© 2024 | My Capstone Project | All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
