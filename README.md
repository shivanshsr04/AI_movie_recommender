# Movie Discovery App

A Streamlit movie-discovery application being rebuilt into a reproducible recommendation system.

## Current status

Phase 2 is complete on the rebuild branch. The repository now includes a
validated preparation pipeline for TMDB metadata and MovieLens ratings. The
Streamlit interface remains a demonstration release until Phase 3 builds and
wires a real content-based recommender.

The app currently provides:

- Local account creation and login using SQLite
- Search across the bundled 100-movie demonstration dataset
- Popular, well-rated movie suggestions
- Basic dataset analytics

## Prepare real data

Place the required CSV files in data/raw. See
[data/raw/README.md](data/raw/README.md) for exact filenames and required
columns.

Then run:

    python prepare_data.py

The command validates the input schema, normalizes TMDB movie IDs, maps
MovieLens ratings through links_small.csv, filters invalid rows, and writes
ignored outputs to data/processed.

It produces:

- movies.csv — cleaned TMDB metadata, including optional credits and keywords
- ratings.csv — ratings mapped to TMDB movie_id values
- manifest.json — row counts and output schema

train_models.py intentionally does not train models in this phase. It prevents
the old synthetic artifacts from being regenerated.

## Rebuild roadmap

1. Stabilize repository structure and documentation — complete
2. Create a reliable movie and ratings data pipeline — complete
3. Deliver a real content-based recommender
4. Connect that recommender to the Streamlit app
5. Add collaborative filtering, SVD, and hybrid ranking
6. Add evaluation, tests, security hardening, and deployment documentation

## Run the current demo

    git clone https://github.com/shivanshsr04/AI_movie_recommender.git
    cd AI_movie_recommender
    python3 -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    streamlit run streamlit_app.py

The current demonstration UI requires the bundled legacy artifacts in models.

## Project structure

    .streamlit/config.toml     Streamlit configuration
    data/raw/                  Local source datasets and requirements
    data/processed/            Generated normalized outputs
    data_loader.py             Validated TMDB–MovieLens preparation pipeline
    prepare_data.py            Data-preparation command
    train_models.py            Guard until real model training is implemented
    recommender_models.py      Model classes to be corrected in later phases
    streamlit_app.py           Demonstration web application
    requirements.txt           Python dependencies

## License

Released under the [MIT License](LICENSE).
