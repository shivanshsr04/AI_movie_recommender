"""Leakage-aware global temporal evaluation against a popularity baseline."""
import argparse
import json
import platform
from importlib.metadata import version
from pathlib import Path
import numpy as np
from data_loader import load_movielens, source_checksums
from recommender_models import (ContentBasedRecommender, PopularityRecommender,
    CollaborativeFilteringRecommender, MatrixFactorizationRecommender,
    HybridRecommender, rank_scores)


def temporal_split(ratings):
    """Global 80/10/10 time boundaries; equal timestamps stay in one partition."""
    first = int(ratings.timestamp.quantile(0.8, interpolation='lower'))
    second = int(ratings.timestamp.quantile(0.9, interpolation='lower'))
    train = ratings[ratings.timestamp <= first].copy()
    validation = ratings[(ratings.timestamp > first) & (ratings.timestamp <= second)].copy()
    test = ratings[ratings.timestamp > second].copy()
    if any(part.empty for part in [train, validation, test]):
        raise ValueError('Need distinct timestamps for nonempty train/validation/test partitions')
    return train, validation, test


def ranking_metrics(predictions, relevant, k):
    hits = np.array([mid in relevant for mid in predictions[:k]], dtype=float)
    dcg = float((hits / np.log2(np.arange(len(hits)) + 2)).sum())
    ideal = float((1 / np.log2(np.arange(min(k, len(relevant))) + 2)).sum())
    return {'precision': float(hits.sum() / k),
            'recall': float(hits.sum() / len(relevant)) if relevant else 0.0,
            'ndcg': dcg / ideal if ideal else 0.0}


def evaluate(data_dir, k=10):
    if k < 1:
        raise ValueError('k must be positive')
    movies, ratings = load_movielens(data_dir)
    train, validation, test = temporal_split(ratings)
    content = ContentBasedRecommender().fit(movies)
    popularity = PopularityRecommender().fit(movies, train)
    collab = CollaborativeFilteringRecommender().fit(movies, train)
    svd = MatrixFactorizationRecommender().fit(movies, train, random_state=42)
    histories = {int(uid): group for uid, group in train.groupby('userId')}
    report = {
        'dataset': 'GroupLens MovieLens latest-small', 'source_sha256': source_checksums(data_dir),
        'python': platform.python_version(),
        'packages': {name: version(name) for name in ['numpy', 'pandas', 'scipy', 'scikit-learn']},
        'protocol': {'split': 'global timestamp 80/10/10; ties stay together', 'k': k,
                     'positive_rating': 4.0, 'seed': 42, 'minimum_train_ratings': 5,
                     'content_seed': 'all training movies rated >= 4.0',
                     'candidates': 'full known catalog minus all training-rated items',
                     'cold_users': 'excluded; counts reported',
                     'tuning': 'none; fixed parameters; both partitions use the same training fit',
                     'content_weights': [0.6, 0.4], 'knn_neighbors': 20, 'svd_factors': 32,
                     'hybrid': 'equal-weight reciprocal-rank fusion, constant 60'},
        'data': {'movies': len(movies), 'users': int(ratings.userId.nunique()), 'ratings': len(ratings),
                 'sparsity': 1 - len(ratings) / (ratings.userId.nunique() * len(movies)),
                 'train_rows': len(train), 'validation_rows': len(validation), 'test_rows': len(test),
                 'train_end_timestamp': int(train.timestamp.max()),
                 'validation_end_timestamp': int(validation.timestamp.max()),
                 'movies_without_training_ratings': len(set(movies.movieId) - set(train.movieId))},
        'partitions': {},
    }
    for partition_name, heldout in [('validation', validation), ('test', test)]:
        per_model = {name: [] for name in ['popularity', 'content', 'knn', 'svd', 'hybrid']}
        coverage = {name: set() for name in per_model}
        cohorts = {'no_training_history': 0, 'insufficient_training_history': 0,
                   'no_positive_seed': 0, 'no_relevant_heldout_item': 0}
        for uid, group in heldout.groupby('userId'):
            history = histories.get(int(uid))
            if history is None:
                cohorts['no_training_history'] += 1
                continue
            if len(history) < 5:
                cohorts['insufficient_training_history'] += 1
                continue
            seed_ids = history.loc[history.rating >= 4, 'movieId'].tolist()
            if not seed_ids:
                cohorts['no_positive_seed'] += 1
                continue
            relevant = set(group.loc[group.rating >= 4, 'movieId'])
            if not relevant:
                cohorts['no_relevant_heldout_item'] += 1
                continue
            seen = set(history.movieId)
            scores = {'popularity': popularity.score(), 'content': content.score(seed_ids),
                      'knn': collab.score(int(uid)), 'svd': svd.score(int(uid))}
            # Explicit fallback only for unsupported users/neighborhoods.
            if not scores['knn']:
                scores['knn'] = scores['popularity']
            scores['hybrid'] = HybridRecommender.score(
                [scores['content'], scores['knn'], scores['svd']], exclude=seen)
            for name, values in scores.items():
                predicted = [mid for mid, _ in rank_scores(values, seen, k)]
                row = ranking_metrics(predicted, relevant, k)
                row['training_ratings'] = len(history)
                per_model[name].append(row)
                coverage[name].update(predicted)
        eligible = len(per_model['popularity'])
        if not eligible:
            raise ValueError(f'No eligible warm users in {partition_name}; cannot report a benchmark')
        metrics = {}
        for name, rows in per_model.items():
            metrics[name] = {metric + f'@{k}': float(np.mean([row[metric] for row in rows]))
                             for metric in ['precision', 'recall', 'ndcg']}
            metrics[name]['catalog_coverage'] = len(coverage[name]) / len(movies)
            metrics[name]['users_with_5_to_19_train_ratings'] = sum(row['training_ratings'] < 20 for row in rows)
        report['partitions'][partition_name] = {
            'heldout_users': int(heldout.userId.nunique()), 'evaluated_users': eligible,
            'excluded_users_by_reason': cohorts, 'metrics': metrics,
        }
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('reports/movielens-evaluation.json'))
    parser.add_argument('--k', type=int, default=10)
    args = parser.parse_args()
    result = evaluate(args.data_dir, args.k)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
