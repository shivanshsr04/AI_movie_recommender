import json
import pandas as pd
import pytest
from app_service import load_catalog, recommend
from data_loader import load_demo, load_movielens
from train_models import train
from evaluate import ranking_metrics, temporal_split


def test_artifact_round_trip_and_tamper_detection(tmp_path):
    metadata = train(demo=True, output_dir=tmp_path)
    movies, model, loaded = load_catalog(tmp_path)
    assert metadata == loaded
    assert recommend(movies, model, 101, 'Content similarity', 1)[0][0] == 205
    with (tmp_path / 'catalog.json').open('a') as handle:
        handle.write(' ')
    with pytest.raises(ValueError, match='checksum'):
        load_catalog(tmp_path)


def test_missing_artifacts_use_explicit_demo_but_partial_files_fail(tmp_path):
    assert load_catalog(tmp_path)[2]['demo']
    (tmp_path / 'catalog.json').write_text('[]')
    with pytest.raises(ValueError, match='Incomplete'):
        load_catalog(tmp_path)


def test_real_data_training_and_schema_validation(tmp_path):
    load_demo().to_csv(tmp_path / 'movies.csv', index=False)
    ratings = pd.DataFrame({'userId': [1, 2], 'movieId': [101, 101],
                            'rating': [4, 5], 'timestamp': [10, 20]})
    ratings.to_csv(tmp_path / 'ratings.csv', index=False)
    train(data_dir=tmp_path, output_dir=tmp_path / 'models')
    movies, model, metadata = load_catalog(tmp_path / 'models')
    assert not metadata['demo']
    assert movies.set_index('movieId').loc[101, 'rating_count'] == 2
    assert recommend(movies, model, 205, 'Popularity baseline', 1)[0] == (101, 2.0)
    ratings.loc[0, 'movieId'] = 999999
    ratings.to_csv(tmp_path / 'ratings.csv', index=False)
    with pytest.raises(ValueError, match='unknown movie IDs'):
        load_movielens(tmp_path)


def test_temporal_split_does_not_leak_or_split_ties():
    ratings = pd.DataFrame({'timestamp': list(range(100)) + [80, 90]})
    train_df, validation, test = temporal_split(ratings)
    assert train_df.timestamp.max() < validation.timestamp.min()
    assert validation.timestamp.max() < test.timestamp.min()
    assert len(train_df) + len(validation) + len(test) == len(ratings)


def test_known_metrics_and_short_lists():
    values = ranking_metrics([10, 20, 30], {10, 30}, 3)
    assert values['precision'] == pytest.approx(2 / 3)
    assert values['recall'] == 1
    assert values['ndcg'] == pytest.approx(1.5 / (1 + 1 / 1.584962500721156))
    assert ranking_metrics([10], {10}, 10)['precision'] == 0.1
