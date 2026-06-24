import streamlit as st
import pandas as pd
import pickle
import os
from pathlib import Path


# 1. DATA LOADING FUNCTIONS
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
        return f"Error: {str(e)}"


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


# 2. MAIN APP

def main():
    st.title("Diagnostic Mode — AI Movie Recommender")

    # Data
    with st.spinner("Loading data..."):
        movies_df = load_data()

    if movies_df is None:
        st.error("Data file models/clean_movies.pkl not found. The app can still run, but there will be no movie content.")
    elif isinstance(movies_df, str) and movies_df.startswith("Error:"):
        st.error(movies_df)
    else:
        st.success(f"Data loaded: {len(movies_df)} rows")
        st.dataframe(movies_df.head(5))

    # Models
    st.write("\n---\n")
    st.write("Checking for trained model files in models/ ...")
    with st.spinner("Checking models..."):
        models = check_and_load_models('models')

    any_loaded = any(models[k] not in (None, f"Error loading: {k}") for k in models)

    for k, v in models.items():
        if v is None:
            st.warning(f"{k}: MISSING ({models[k]})")
        elif isinstance(v, str) and v.startswith('Error loading'):
            st.error(f"{k}: {v}")
        else:
            st.success(f"{k}: loaded ({type(v).__name__})")

    # Basic UI stubs
    st.write("\n---\n")
    st.header("Quick UI check")

    page = st.sidebar.radio("Navigation", ["Home", "About", "Diagnostics"])
    st.write(f"Page selected: {page}")

    if page == "Home":
        st.subheader("Home — Recommendations (stub)")
        if movies_df is None or isinstance(movies_df, str):
            st.info("No movie data available to show recommendations.")
        else:
            # Show first movie and sample recommendation if content model exists
            first = movies_df.iloc[0]
            st.write(f"Sample movie: {first.get('title', first.get('name', 'Unknown'))} (id={first.get('id')})")

            content_model = models.get('content_based_model')
            if content_model is not None and not isinstance(content_model, str):
                try:
                    # try to call recommend with first movie id
                    recs = None
                    if hasattr(content_model, 'recommend'):
                        recs = content_model.recommend(int(first.get('id', 0)), n_recommendations=5)
                    elif hasattr(content_model, 'similarity_matrix'):
                        st.info('Content model appears to be raw feature object; skipping recommend call.')
                    else:
                        st.info('Loaded content model has no recommend() method; cannot call it.')

                    if recs:
                        st.write("Recommendations (titles):")
                        for r in recs:
                            st.write(f"- {r.get('title')} (score={r.get('score')})")
                except Exception as e:
                    st.error(f"Error calling content model.recommend(): {e}")
            else:
                st.info('Content model not available — provide content_based_model.pkl in models/')

    elif page == "Diagnostics":
        st.subheader("Diagnostics")
        st.write("Models object summary:")
        for k, v in models.items():
            st.write(f"- {k}: {type(v).__name__ if v is not None else 'None'}")

    else:
        st.subheader("About")
        st.write("This diagnostic deployment helps validate that data and model files load correctly and that Streamlit renders the UI. Implement the real UI functions to show posters and cards.")

    st.write("\n---\n")
    st.caption("If you see missing files, copy your trained pickles into the models/ directory with these names: content_based_model.pkl, collaborative_model.pkl, matrix_fact_model.pkl")


if __name__ == '__main__':
    main()
