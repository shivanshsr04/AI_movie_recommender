import streamlit as st
import pandas as pd
import pickle
import os
from utils.auth import create_usertable, add_user, login_user, make_hashes

# 1. DATA LOADING FUNCTIONS
@st.cache_resource
def load_data():
    """Load the cleaned movie dataset"""
    file_path = 'models/clean_movies.pkl'
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return pd.DataFrame()

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
    create_usertable()
    # ... (Keep your Auth Logic) ...
    
    # Authenticated section
    movies_df = load_data()
    models = load_models('models') # Pass the directory here
    
    if movies_df.empty:
        st.warning("⚠️ Data not loaded.")
        return
    
    # ... (Rest of your UI code) ...