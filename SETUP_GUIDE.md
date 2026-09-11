# Setup Guide

## Current demonstration release

This repository is in a staged rebuild. The current app uses bundled demonstration artifacts and supports movie search, popular-title discovery, and analytics. It does not yet run the multi-model recommender described in earlier project materials.

### 1. Clone the repository

```bash
git clone https://github.com/shivanshsr04/AI_movie_recommender.git
cd AI_movie_recommender
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run streamlit_app.py
```

Open the local address Streamlit displays, normally `http://localhost:8501`.

## Data and training

Do not run `train_models.py` as a way to claim a production recommender. The training and data pipeline are being replaced in later phases.

The next data phase will define required raw datasets, validate their schema, and produce a correctly mapped movie-and-ratings dataset before model training is re-enabled.
