"""
AI Movie Recommender System - CUSTOMIZED FOR YOUR DATA
Works with your specific columns:
- id, title, overview, genres, release_date (datetime), vote_average, vote_count, popularity
"""

import streamlit as st
import pandas as pd
import pickle
import os
from utils.auth import create_usertable, add_user, login_user, user_exists, get_user_info

# ============= SETUP =============
st.set_page_config(
    page_title="🎬 AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize auth table
try:
    create_usertable()
except Exception as e:
    st.warning(f"⚠️ Auth issue: {str(e)}")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''
    st.session_state['page'] = 'login'

# ============= DATA LOADING FUNCTIONS =============

@st.cache_resource
def load_data():
    """Load the cleaned movie dataset"""
    file_path = 'models/clean_movies.pkl'
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def extract_year(date_val):
    """Extract year from datetime or string"""
    try:
        if pd.isna(date_val):
            return "N/A"
        if isinstance(date_val, str):
            return date_val[:4]
        # For datetime
        return str(pd.Timestamp(date_val).year)
    except:
        return "N/A"

def display_movie_card(movie, score=None):
    """Display a movie card with details"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        year = extract_year(movie['release_date'])
        st.write(f"**Year:** {year}")
        st.write(f"**Rating:** {movie['vote_average']:.1f}/10")
        if score:
            st.write(f"**Match:** {score*100:.0f}%")
    
    with col2:
        overview = movie.get('overview', 'No overview available')
        if isinstance(overview, str) and overview:
            st.write(overview[:300] + "..." if len(overview) > 300 else overview)
        else:
            st.write("No description available")
        
        st.write(f"**Popularity:** {movie['popularity']:.0f}")

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
        
        st.markdown("---")
        st.info("Create an account to explore the demonstration catalog.")

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
                    #hashed_pwd = make_hashes(password)
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

def home_page(username, movies_df):
    """Display the current demonstration release status."""
    st.markdown(f"# 🎬 Welcome, {username}! 👋")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Movie Discovery Demo

        This stabilized release lets you search the bundled catalog, browse
        popular titles, and explore basic dataset analytics.

        ### Rebuild status

        The project is being rebuilt into a tested recommendation system.
        Content-based, collaborative, SVD, and hybrid recommendations are not
        yet available in this release.
        """)

    with col2:
        st.markdown("#### Your Profile")
        try:
            user_info = get_user_info(username)
            if user_info:
                st.metric("Username", user_info.get("username", "N/A"))
                st.metric("Email", user_info.get("email", "Not set"))
        except Exception:
            st.info("User information is unavailable.")


def movie_search_page(username, movies_df):
    """Movie search page"""
    st.markdown("---")
    st.markdown("## 🔎 Search Movies")
    
    if movies_df is None or movies_df.empty:
        st.warning("⚠️ Movie data not loaded.")
        return
    
    search_term = st.text_input("Search for a movie:", placeholder="e.g., Inception, Avatar...")
    
    if search_term:
        try:
            search_results = movies_df[
                movies_df['title'].str.contains(search_term, case=False, na=False)
            ].nlargest(10, 'popularity')
            
            if not search_results.empty:
                st.markdown(f"### Found {len(search_results)} movies:")
                
                for idx, movie in search_results.iterrows():
                    year = extract_year(movie['release_date'])
                    rating = movie['vote_average']
                    title = movie['title']
                    
                    with st.expander(f"▶️ {title} ({year} - ⭐ {rating:.1f}/10)"):
                        display_movie_card(movie)
            else:
                st.info("No movies found. Try different keywords.")
        except Exception as e:
            st.error(f"Search error: {str(e)}")

def recommendations_page(username, movies_df):
    """Display a clearly labelled popularity-based discovery list."""
    st.markdown("---")
    st.markdown("## 💡 Discover Popular Movies")
    st.info(
        "This demonstration release shows popular, well-rated titles. "
        "Model-based recommendations will be added after the data pipeline is rebuilt."
    )

    if movies_df is None or movies_df.empty:
        st.warning("⚠️ Movie data not loaded.")
        return

    try:
        top_movies = movies_df.nlargest(100, "popularity")
        movie_options = {}
        for _, movie in top_movies.iterrows():
            label = f"{movie['title']} ({extract_year(movie['release_date'])}) — {movie['id']}"
            movie_options[label] = movie["id"]

        selected_label = st.selectbox(
            "Choose a movie to exclude from the discovery list:",
            list(movie_options.keys())
        )
        num_recommendations = st.slider("Number of movies to show:", 5, 20, 10)

        if st.button("🚀 Show Popular Movies", key="rec_button"):
            with st.spinner("Loading popular movies..."):
                selected_movie_id = movie_options[selected_label]
                selected_movie = movies_df[movies_df["id"] == selected_movie_id].iloc[0]

                st.markdown(f"### Selected: **{selected_movie['title']}**")
                display_movie_card(selected_movie)
                st.markdown("---")
                st.markdown(f"### 🎬 {num_recommendations} Popular, Well-Rated Movies")

                suggestions = movies_df[
                    (movies_df["id"] != selected_movie_id) &
                    (movies_df["vote_average"] >= 6.0)
                ].nlargest(num_recommendations, "popularity")

                for idx, (_, movie) in enumerate(suggestions.iterrows(), 1):
                    with st.expander(f"#{idx} · {movie['title']} — ⭐ {movie['vote_average']:.1f}/10"):
                        display_movie_card(movie)
    except Exception as e:
        st.error(f"Unable to load the discovery list: {str(e)}")


def analytics_page(username, movies_df):
    """Analytics page"""
    st.markdown("---")
    st.markdown("## 📊 Movie Database Analytics")
    
    if movies_df is None or movies_df.empty:
        st.warning("⚠️ Movie data not loaded.")
        return
    
    try:
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Ratings", "Timeline", "Top Movies"])
        
        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Movies", f"{len(movies_df):,}")
            col2.metric("Avg Rating", f"{movies_df['vote_average'].mean():.1f}/10")
            col3.metric("Total Votes", f"{int(movies_df['vote_count'].sum()):,}")
            col4.metric("Status", "✅ Ready")
        
        with tab2:
            st.markdown("### Rating Distribution")
            rating_data = movies_df['vote_average'].value_counts().sort_index()
            st.bar_chart(rating_data)
        
        with tab3:
            st.markdown("### Movies Over Time")
            try:
                # Convert datetime to year
                movies_df['year'] = pd.to_datetime(movies_df['release_date']).dt.year
                year_data = movies_df['year'].value_counts().sort_index().tail(30)
                st.line_chart(year_data)
            except Exception as e:
                st.error(f"Timeline error: {str(e)}")
        
        with tab4:
            st.markdown("### Top 20 Most Popular Movies")
            try:
                top_20 = movies_df.nlargest(20, 'popularity')[['title', 'vote_average', 'popularity']]
                st.dataframe(top_20, use_container_width=True)
            except Exception as e:
                st.error(f"Top movies error: {str(e)}")
    except Exception as e:
        st.error(f"Analytics error: {str(e)}")

def about_page(username):
    """Explain the current project scope accurately."""
    st.markdown("---")
    st.markdown(f"""
    ## About This Project

    **User:** {username}

    ### Current release

    This is a Streamlit movie-discovery demonstration built around a bundled
    100-movie sample dataset. It supports account creation, movie search,
    popularity-based discovery, and basic analytics.

    ### Rebuild roadmap

    1. Stabilize the repository and documentation
    2. Build a validated movie and ratings data pipeline
    3. Add a real content-based recommender
    4. Add collaborative filtering, SVD, and hybrid ranking
    5. Evaluate models and document measured results

    ### Important limitation

    The current release does not present its popularity list as a personalized
    or machine-learning recommendation. Those features will be enabled only
    after they are implemented and tested.

    ### Built By

    Shivansh Srivastava
    """)


# ============= MAIN APP =============

def main():
    """Main application"""
    
    # Authentication gatekeeper
    if not st.session_state['logged_in']:
        if st.session_state['page'] == 'signup':
            signup_page()
        else:
            login_page()
        return
    
    # Load data
    movies_df = load_data()
    username = st.session_state['username']
    
    # Sidebar
    st.sidebar.markdown(f"### 👤 {username}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📊 Navigation")
    page = st.sidebar.radio("Select Page:", [
        "🏠 Home",
        "🔍 Movie Search",
        "💡 Get Recommendations",
        "📈 Analytics",
        "ℹ️ About"
    ])
    
    # Check if data loaded
    if movies_df is None:
        st.error("❌ Unable to load movie data. Make sure 'models/clean_movies.pkl' exists.")
        st.info("Run: `python train_models.py` to generate the model file.")
        return
    
    # Display pages
    if page == "🏠 Home":
        home_page(username, movies_df)
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
    <p>🎬 Movie Discovery App | Demonstration release</p>
    <p>© 2026 | Recommendation pipeline rebuild in progress</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()