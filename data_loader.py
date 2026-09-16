"""Validated MovieLens loading with one canonical movie ID namespace."""
from pathlib import Path
import hashlib
import pandas as pd

ROOT = Path(__file__).resolve().parent


def require_columns(frame, columns, label):
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f"{label} is missing columns: {', '.join(sorted(missing))}")


def integer_column(values, name):
    numeric = pd.to_numeric(values, errors="raise")
    if numeric.isna().any() or (numeric % 1 != 0).any():
        raise ValueError(f"{name} must contain non-null integers")
    return numeric.astype('int64')


def validate_movies(movies):
    require_columns(movies, ['movieId', 'title', 'genres'], 'movies')
    movies = movies.copy()
    movies['movieId'] = integer_column(movies['movieId'], 'movieId')
    if movies.empty or movies.movieId.duplicated().any():
        raise ValueError('Movies must be nonempty with unique movieId values')
    movies['title'] = movies.title.fillna('').astype(str).str.strip()
    if movies.title.eq('').any():
        raise ValueError('Every movie needs a title')
    movies['genres'] = movies.genres.fillna('').replace('(no genres listed)', '')
    if 'overview' not in movies:
        movies['overview'] = ''
    movies['overview'] = movies.overview.fillna('').astype(str)
    return movies.sort_values('movieId').reset_index(drop=True)


def load_movielens(data_dir):
    """Read GroupLens movies.csv and ratings.csv; no TMDB ID join is needed."""
    data_dir = Path(data_dir)
    movies = validate_movies(pd.read_csv(data_dir / 'movies.csv'))
    ratings = pd.read_csv(data_dir / 'ratings.csv')
    require_columns(ratings, ['userId', 'movieId', 'rating', 'timestamp'], 'ratings')
    ratings = ratings[['userId', 'movieId', 'rating', 'timestamp']].copy()
    for column in ['userId', 'movieId', 'timestamp']:
        ratings[column] = integer_column(ratings[column], column)
    ratings['rating'] = pd.to_numeric(ratings.rating, errors='raise')
    if ratings.empty or not ratings.rating.between(0.5, 5.0).all():
        raise ValueError('Ratings must be nonempty and between 0.5 and 5.0')
    unknown = set(ratings.movieId) - set(movies.movieId)
    if unknown:
        raise ValueError(f'Ratings reference {len(unknown)} unknown movie IDs')
    ratings = ratings.sort_values(['timestamp', 'userId', 'movieId'])
    ratings = ratings.drop_duplicates(['userId', 'movieId'], keep='last')
    return movies, ratings.reset_index(drop=True)


def load_demo():
    """Fictional, authored examples; these are not a real-world benchmark."""
    return validate_movies(pd.read_csv(ROOT / 'data/demo/movies.csv'))


def source_checksums(data_dir):
    return {name: hashlib.sha256((Path(data_dir) / name).read_bytes()).hexdigest()
            for name in ['movies.csv', 'ratings.csv']}
