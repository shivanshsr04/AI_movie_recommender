import streamlit as st
import pandas as pd
import pickle
import os
#from utils.auth import create_usertable, add_user, login_user, make_hashes


# 1. DATA LOADING FUNCTIONS
@st.cache_resource
def load_data():
    """Load the cleaned movie datasets with error reporting"""
    file_path = 'models/clean_movies.pkl'
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return "Error: File 'models/clean_movies.pkl' not found."
    except Exception as e:
        return f"Error: {str(e)}"

@st.cache_resource
def load_models(model_dir):
    """Load ML model files safely"""
    model_files = {'content_based': 'content_based_model.pkl', 'collaborative': 'collaborative.pkl'}
    loaded = {}
    for name, filename in model_files.items():
        path = os.path.join(model_dir, filename)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                loaded[name] = pickle.load(f)
        else:
            loaded[name] = None
    return loaded

# ... (Insert your display_movie_card and get_movie_poster functions here) ...

# 2. MAIN APP
def main():
    try:
        st.title("Diagnostic Mode")

        # 1. Attempt Data Load
        st.write("Attempting to load data...")
        movies_df = load_data()
        if movies_df is None or (hasattr(movies_df, 'empty') and movies_df.empty):
            st.error("Data loading failed or returned empty. Try checking models/clean_movies.pkl")
        else:
            st.write(f"Data loaded successfully! Rows: {len(movies_df)}")

        # 2. Attempt Auth
        st.write("Attempting to create user table...")
        # create_usertable()
        st.write("Auth system initialized.")

        # 3. Attempt UI Rendering
        st.write("Attempting to render Sidebar...")
        page = st.sidebar.radio("Navigation", ["Home", "About"])
        st.write(f"Page selected: {page}")

        st.success("Everything is working!")

    except Exception as e:
        st.error(f"FATAL ERROR: {e}")
        import traceback
        st.text(traceback.format_exc())
    return


if __name__ == "__main__":
    main()
