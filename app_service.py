"""Artifact validation and recommendation logic independent of Streamlit."""
import hashlib
import json
from io import StringIO
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import sparse
from data_loader import load_demo, validate_movies
from recommender_models import ContentBasedRecommender, rank_scores


def artifact_signature(model_dir):
    paths = [Path(model_dir) / name for name in ['metadata.json', 'catalog.json', 'content_features.npz']]
    return tuple((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in paths if p.exists())


def load_catalog(model_dir):
    model_dir = Path(model_dir)
    paths = [model_dir / name for name in ['metadata.json', 'catalog.json', 'content_features.npz']]
    if not any(path.exists() for path in paths):
        movies = load_demo()
        movies['rating_count'] = 0
        movies['mean_rating'] = None
        return movies, ContentBasedRecommender().fit(movies), {'demo': True, 'source': 'Fictional demo'}
    if not all(path.exists() for path in paths):
        raise ValueError('Incomplete artifacts. Re-run train_models.py to rebuild all three files.')
    metadata = json.loads(paths[0].read_text(encoding='utf-8'))
    if metadata.get('schema_version') != 1:
        raise ValueError('Unsupported artifact schema. Rebuild with train_models.py.')
    for path, key in [(paths[1], 'catalog_sha256'), (paths[2], 'features_sha256')]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != metadata[key]:
            raise ValueError(f'Artifact checksum mismatch: {path.name}. Rebuild the artifacts.')
    movies = validate_movies(pd.read_json(StringIO(paths[1].read_text(encoding='utf-8'))))
    features = sparse.load_npz(paths[2]).tocsr()
    if len(movies) != metadata['movie_count'] or features.shape != (len(movies), metadata['content']['feature_count']):
        raise ValueError('Catalog and feature matrix dimensions do not match')
    if not np.isfinite(features.data).all():
        raise ValueError('Content features contain non-finite values')
    model = ContentBasedRecommender()
    model.movie_ids = movies.movieId.to_numpy()
    model.positions = {int(mid): i for i, mid in enumerate(model.movie_ids)}
    model.features = features
    return movies, model, metadata


def recommend(movies, model, movie_id, method, k):
    if method == 'Content similarity':
        return model.recommend(movie_id, k)
    if method == 'Popularity baseline':
        return rank_scores(movies.set_index('movieId').rating_count.to_dict(), [movie_id], k)
    raise ValueError(f'Unknown recommendation method: {method}')
