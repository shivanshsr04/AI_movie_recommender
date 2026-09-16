"""Build a versioned content artifact from MovieLens or explicit demo data."""
import argparse
import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path
from scipy import sparse
from data_loader import ROOT, load_demo, load_movielens, source_checksums
from recommender_models import ContentBasedRecommender


def train(data_dir=None, demo=False, output_dir=None):
    if demo == (data_dir is not None):
        raise ValueError('Choose exactly one of demo=True or data_dir')
    output_dir = Path(output_dir or ROOT / 'models')
    output_dir.mkdir(parents=True, exist_ok=True)
    if demo:
        movies = load_demo()
        source = 'Authored fictional demo (12 movies); not a benchmark'
        hashes = {'movies.csv': hashlib.sha256((ROOT / 'data/demo/movies.csv').read_bytes()).hexdigest()}
        rating_count = 0
        movies['rating_count'] = 0
        movies['mean_rating'] = None
    else:
        movies, ratings = load_movielens(data_dir)
        source = 'GroupLens MovieLens latest-small'
        hashes = source_checksums(data_dir)
        rating_count = len(ratings)
        summary = ratings.groupby('movieId').rating.agg(rating_count='size', mean_rating='mean')
        movies = movies.join(summary, on='movieId')
        movies['rating_count'] = movies.rating_count.fillna(0).astype(int)
    model = ContentBasedRecommender().fit(movies)
    # JSON + sparse NPZ avoid loading executable pickle artifacts.
    catalog = movies.to_json(orient='records', force_ascii=False, indent=2)
    (output_dir / 'catalog.json').write_text(catalog, encoding='utf-8')
    sparse.save_npz(output_dir / 'content_features.npz', model.features)
    metadata = {
        'schema_version': 1, 'source': source, 'demo': demo,
        'movie_count': len(movies), 'rating_count': rating_count,
        'source_sha256': hashes,
        'catalog_sha256': hashlib.sha256(catalog.encode('utf-8')).hexdigest(),
        'features_sha256': hashlib.sha256((output_dir / 'content_features.npz').read_bytes()).hexdigest(),
        'content': {'text_weight': 0.6, 'genre_weight': 0.4, 'ngram_range': [1, 2],
                    'max_features': 20000, 'feature_count': model.features.shape[1]},
        'python': platform.python_version(),
        'packages': {name: version(name) for name in ['numpy', 'pandas', 'scipy', 'scikit-learn']},
    }
    (output_dir / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--data-dir', type=Path, help='Folder containing movies.csv and ratings.csv')
    source.add_argument('--demo', action='store_true', help='Use fictional examples only')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'models')
    args = parser.parse_args()
    print(json.dumps(train(args.data_dir, args.demo, args.output_dir), indent=2))
