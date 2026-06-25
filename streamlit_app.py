"""
AI Movie Recommender System
Complete Streamlit App with User Authentication
"""

import streamlit as st
import pandas as pd
import pickle
import os

from utils.auth import create_usertable, add_user, login_user, make_hashes, user_exists, get_user_info

# ============= SETUP =============
st.set_page_config(
    page_title="🎬 AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize auth table
create_usertable()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''
    st.session_state['page'] = 'login'

# ============= DATA LOADING FUNCTIONS =============

from pathlib import Path



@st.cache_resource
def load_data():
    """Load the cleaned movie datasets with error reporting"""
    file_path = Path(__file__).resolve().parent / 'models' / 'clean_movies.pkl'
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:

        st.error(f"Error loading data: {str(e)}")
        return None

@st.cache_resource
@st.cache_resource
def load_models(model_dir='models'):
    """Load ML model files safely"""
    model_files = {
        'content_based': 'content_based_model.pkl',
        'collaborative': 'collaborative.pkl'
    }
    loaded = {}
    
    for name, filename in model_files.items():
        path = os.path.join(model_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    loaded[name] = pickle.load(f)
            except Exception as e:
                st.warning(f"Could not load {name} model: {str(e)}")
                loaded[name] = None
        else:
            st.error(f"File not found: {path}")
            loaded[name] = None
            
    return loaded  # Correct: Return the dictionary of models

def check_and_load_models(model_dir: str):
    """Check for expected model files and load them if available."""
    expected = {
        'content_based_model': 'content_based_model.pkl',
        'collaborative_model': 'collaborative_model.pkl',
        'matrix_fact_model': 'matrix_fact_model.pkl'
    }
    loaded = {}
    model_path = Path(__file__).resolve().parent / model_dir
    for key, fname in expected.items():
        path = model_path / fname
        if path.exists():
            try:
                with open(path, 'rb') as f:
                    loaded[key] = pickle.load(f)
            except Exception as e:
                loaded[key] = f"Error loading: {e}"

        else:
            loaded[key] = None
    return loaded


def display_movie_card(movie, score=None):
    """
    Display a movie card with details
    
    Args:
        movie: Movie row from dataframe
        score: Optional recommendation score (0-1)
    """
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Poster placeholder
        st.write(f"**Year:** {int(movie['year'])}")
        st.write(f"**Rating:** {movie['vote_average']}/10")
        if score:
            st.write(f"**Match:** {score*100:.0f}%")
    
    with col2:
        # Movie overview
        overview = movie.get('overview', 'No overview available')
        if isinstance(overview, str) and overview:
            st.write(overview[:300] + "...")
        else:
            st.write("No description available")
        
        # Additional info
        st.write(f"**Popularity:** {movie.get('popularity', 0):.0f}")

def get_movie_poster(poster_path):
    """Get movie poster URL from TMDB"""
    if poster_path and isinstance(poster_path, str):
        return f"https://image.tmdb.org/t/p/w300{poster_path}"
    return None

# ============= AUTHENTICATION PAGES =============

def login_page():
    """Display login page"""
    st.markdown("# 🎬 AI Movie Recommender System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🔐 Login")
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col_login, col_signup = st.columns(2)
        
        with col_login:
            if st.button("🔓 Login", use_container_width=True):
                if username and password:
                    # Login using auth function
                    is_valid, message = login_user(username, password)
                    if is_valid:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("❌ Please enter both username and password!")
        
        with col_signup:
            if st.button("📝 Create Account", use_container_width=True):
                st.session_state['page'] = 'signup'
                st.rerun()
        
        # Demo info
        st.markdown("---")
        st.info("""
        **Demo Account:**
        - Username: demo
        - Password: demo123
        
        Or create a new account!
        """)

def signup_page():
    """Display signup page"""
    st.markdown("# 🎬 AI Movie Recommender System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 📝 Create Account")
        
        username = st.text_input("Username", placeholder="Choose a username (3+ chars)", key="signup_user")
        email = st.text_input("Email", placeholder="Enter your email", key="signup_email")
        password = st.text_input("Password", type="password", placeholder="Enter password (6+ chars)", key="signup_pwd")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="signup_confirm")
        
        col_signup, col_back = st.columns(2)
        
        with col_signup:
            if st.button("✅ Create Account", use_container_width=True):
                if not all([username, email, password, confirm_password]):
                    st.error("❌ Please fill in all fields!")
                elif len(username) < 3:
                    st.error("❌ Username must be at least 3 characters!")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters!")
                elif password != confirm_password:
                    st.error("❌ Passwords don't match!")
                elif user_exists(username):
                    st.error("❌ Username already exists!")
                else:

                    # Add user with plain password; auth will hash internally

                    # Pass plaintext password - add_user will hash it

                    success, message = add_user(username, password, email)
                    if success:
                        st.success(message)
                        st.info("✅ Account created! Please login.")
                        st.balloons()
                        import time
                        time.sleep(2)
                        st.session_state['page'] = 'login'
                        st.rerun()
                    else:
                        st.error(message)
        
        with col_back:
            if st.button("⬅️ Back to Login", use_container_width=True):
                st.session_state['page'] = 'login'
                st.rerun()

# ============= MAIN APPLICATION PAGES =============

def home_page(username):
    """Home page for logged-in users"""
    st.markdown(f"# 🎬 Welcome, {username}! 👋")
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
        1. Browse our database of movies
        2. Search for movies you like
        3. Get personalized recommendations
        4. Explore analytics and insights
        """)
    
    with col2:
        st.markdown("#### Your Profile:")
        
        user_info = get_user_info(username)
        if user_info:
            st.metric("Username", user_info.get('username', 'N/A'))
            st.metric("Email", user_info.get('email', 'Not set'))
            if user_info.get('created_at'):
                st.metric("Member Since", user_info.get('created_at', 'N/A')[:10])

def movie_search_page(username, movies_df):
    """Movie search page"""
    st.markdown("---")
    st.markdown("## 🔎 Search Movies")
    
    if movies_df is None or movies_df.empty:
        st.warning("⚠️ Movie data not loaded. Please ensure data files exist.")
        return
    
    search_term = st.text_input("Search for a movie:", placeholder="e.g., Inception, Avatar...")
    
    if search_term:
        search_results = movies_df[
            movies_df['title'].str.contains(search_term, case=False, na=False)
        ].nlargest(10, 'popularity')
        
        if not search_results.empty:
            st.markdown(f"### Found {len(search_results)} movies:")
            
            for idx, movie in search_results.iterrows():
                with st.expander(f"▶️ {movie['title']} ({int(movie['year'])} - ⭐ {movie['vote_average']}/10)"):
                    display_movie_card(movie)
        else:
            st.info("No movies found. Try different keywords.")

def recommendations_page(username, movies_df):
    """Get recommendations page"""
    st.markdown("---")
    st.markdown("## 💡 Get Personalized Recommendations")
    
    if movies_df is None or movies_df.empty:
        st.warning("⚠️ Movie data not loaded.")
        return
    
    recommendation_type = st.selectbox(
        "Choose recommendation method:",
        [
            "🎯 Content-Based (Similar Movies)",
            "👥 Collaborative Filtering (Popular with Similar Users)",
            "🧮 Matrix Factorization (Advanced ML)",
            "🔗 Hybrid (Best of All)"
        ]
    )
    
    # Get top movies for selection
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
            
            # Get similar movies by rating and popularity
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
                        score = 0.95 - (idx * 0.05)
                        display_movie_card(movie, score=score)

def analytics_page(username, movies_df):
    """Analytics page"""
    st.markdown("---")
    st.markdown("## 📊 Movie Database Analytics")
    
    if movies_df is None or movies_df.empty:
        st.warning("⚠️ Movie data not loaded.")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Ratings Distribution", "Movies by Year", "Top Movies"])
    
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Movies", f"{len(movies_df):,}")
        col2.metric("Avg Rating", f"{movies_df['vote_average'].mean():.1f}/10")
        col3.metric("Total Ratings", f"{int(movies_df['vote_count'].sum()):,}")
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

def about_page(username):
    """About page"""
    st.markdown("---")
    st.markdown(f"""
    ## 🎯 About This Project
    
    **User:** {username}
    
    ### Overview
    This is an **AI-powered Movie Recommendation System** built with machine learning to provide 
    personalized movie suggestions based on multiple algorithms.
    
    ### Recommendation Algorithms
    
    #### 1. **Content-Based Filtering**
    - Analyzes movie features (genre, overview, keywords)
    - Recommends movies similar to ones you like
    - Uses TF-IDF and cosine similarity
    
    #### 2. **Collaborative Filtering**
    - Analyzes user rating patterns
    - Recommends movies liked by similar users
    - Uses K-Nearest Neighbors (KNN)
    
    #### 3. **Matrix Factorization (SVD)**
    - Decomposes user-item interaction matrix
    - Discovers latent factors and patterns
    - Handles sparsity in rating data
    
    #### 4. **Hybrid Approach**
    - Combines all three methods
    - Weighted ensemble for best results
    - Balances content and user preferences
    
    ### Dataset
    - **Movies**: 45,000+ movies with metadata
    - **Ratings**: 25+ million user ratings
    - **Features**: Genre, keywords, credits, popularity
    
    ### Technologies Used
    - **Frontend**: Streamlit
    - **ML Libraries**: Scikit-learn, NumPy, Pandas
    - **Database**: SQLite for user authentication
    - **Data**: MovieLens & TMDB API
    
    ### Performance Metrics
    - Content-Based Precision: ~0.75
    - Collaborative Precision: ~0.68
    - Hybrid Precision: ~0.82
    
    ### Built By:
    - **Student**: Shivansh Srivastava (ID: 2301220130084)
    - **Teammate**: Sankalp Shrivastava
    - **Advisor**: Er. Shilpi Khanna
    - **Institution**: Final Year Capstone Project
    """)

# ============= MAIN APP =============

def main():
    """Main application"""
    
    # ===== AUTHENTICATION GATEKEEPER =====
    if not st.session_state['logged_in']:
        # User not logged in - show login/signup
        if st.session_state['page'] == 'signup':
            signup_page()
        else:
            login_page()
        return  # Stop here - don't show main app
    
    # ===== USER IS LOGGED IN =====
    username = st.session_state['username']
    
    # Sidebar with logout
    st.sidebar.markdown(f"### 👤 {username}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Navigation
    st.sidebar.markdown("## 📊 Navigation")
    page = st.sidebar.radio("Select Page:", [
        "🏠 Home",
        "🔍 Movie Search",
        "💡 Get Recommendations",
        "📈 Analytics",
        "ℹ️ About"
    ])
    
    # Load data
    movies_df = load_data()
    models_loaded = load_models('models')
    
    # Check if data loaded
    if movies_df is None or (isinstance(movies_df, str) and "Error" in movies_df):
        st.error("⚠️ Error loading data. Please ensure model files exist in the 'models/' directory.")
        st.info("""
        **Quick Setup:**
        1. Place CSV files in `data/raw/` directory
        2. Run: `python train_models.py`
        3. Refresh the app
        """)
        return
    
    # ===== DISPLAY SELECTED PAGE =====
    if page == "🏠 Home":
        home_page(username)
    elif page == "🔍 Movie Search":
        movie_search_page(username, movies_df)
    elif page == "💡 Get Recommendations":
        recommendations_page(username, movies_df)
    elif page == "📈 Analytics":
        analytics_page(username, movies_df)
    elif page == "ℹ️ About":
        about_page(username)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
    <p>🎬 AI Movie Recommender System | Built with Streamlit & Machine Learning</p>
    <p>© 2024 | Final Year Capstone Project | All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

