# Setup Guide

## Demonstration release

The Streamlit UI is still a demonstration release. It supports local accounts,
movie search, popular-title discovery, and analytics. It does not yet use a
machine-learning recommender.

### 1. Clone and install

    git clone https://github.com/shivanshsr04/AI_movie_recommender.git
    cd AI_movie_recommender
    python3 -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt

### 2. Run the current UI

    streamlit run streamlit_app.py

## Prepare source data for the next model phase

Place these required files in data/raw:

- movies_metadata.csv
- ratings_small.csv
- links_small.csv

Optional files are credits.csv and keywords.csv. Their expected schema is
documented in [data/raw/README.md](data/raw/README.md).

Run:

    python prepare_data.py

The command validates files and columns, maps MovieLens ratings to TMDB IDs,
and writes movies.csv, ratings.csv, and manifest.json to data/processed.

If validation fails, correct the reported source file or column problem before
continuing. Raw and processed datasets are ignored by Git.

## Training status

Do not run train_models.py yet. It is a safety guard while the synthetic
training path is retired. Phase 3 will add actual content-based model training.
