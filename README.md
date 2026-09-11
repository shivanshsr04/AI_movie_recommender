# Movie Discovery App

A Streamlit movie-discovery application currently being rebuilt into a reproducible recommendation system.

## Current status

This branch is the stabilization phase of that rebuild. The application currently provides:

- Local account creation and login using SQLite
- Search across the bundled 100-movie demonstration dataset
- Popular, well-rated movie suggestions
- Basic dataset analytics

The committed model artifacts are legacy demonstration files. The current interface does **not** yet use content-based, collaborative, SVD, or hybrid recommendation models. Those capabilities will be added incrementally after the data pipeline is corrected and tested.

## Rebuild roadmap

1. Stabilize repository structure and documentation
2. Create a reliable movie and ratings data pipeline
3. Deliver a real content-based recommender
4. Connect that recommender to the Streamlit app
5. Add collaborative filtering, SVD, and hybrid ranking
6. Add evaluation, tests, security hardening, and deployment documentation

## Run the current demo

```bash
git clone https://github.com/shivanshsr04/AI_movie_recommender.git
cd AI_movie_recommender
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The application requires the bundled files in `models/` for this demonstration release.

## Data and model status

Raw datasets are intentionally not included in this repository. The next phase will document supported data sources and add validation for all required files.

Do not use the current demonstration artifacts to report recommendation-model accuracy. There is no implemented evaluation pipeline or measured model metrics yet.

## Project structure

```text
.streamlit/config.toml     Streamlit configuration
models/                    Legacy demonstration artifacts
utils/auth.py              Local account helpers
data_loader.py             Data-pipeline module to be rebuilt
recommender_models.py      Model classes to be corrected in later phases
streamlit_app.py           Web application
train_models.py            Single training entry point (to be rebuilt)
requirements.txt           Python dependencies
```

## License

Released under the [MIT License](LICENSE).
