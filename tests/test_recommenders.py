import numpy as np
import pandas as pd
import pytest
from data_loader import load_demo
from recommender_models import (ContentBasedRecommender, CollaborativeFilteringRecommender,
    MatrixFactorizationRecommender, PopularityRecommender, HybridRecommender, rank_scores)


@pytest.fixture
def interactions():
    return pd.DataFrame([(7, 101, 5.0), (7, 205, 4.0), (22, 101, 5.0),
                         (22, 309, 4.0), (93, 412, 5.0), (93, 518, 4.0)],
                        columns=['userId', 'movieId', 'rating'])


def test_content_changes_with_seed_and_excludes_self():
    model = ContentBasedRecommender().fit(load_demo())
    space = model.recommend(101, 20)
    mystery = model.recommend(412, 20)
    assert space[0][0] == 205
    assert mystery[0][0] == 518
    assert all(mid != 101 and 0 <= score <= 1 for mid, score in space)
    assert len(space) == 11
    assert model.recommend(-1) == []


def test_identical_vectors_still_exclude_query():
    movies = load_demo().iloc[:2].copy()
    movies.loc[:, 'title'] = 'Same movie'
    movies.loc[:, 'genres'] = 'Drama'
    movies.loc[:, 'overview'] = 'Same description'
    model = ContentBasedRecommender().fit(movies)
    assert [mid for mid, _ in model.recommend(205)] == [101]


def test_models_preserve_noncontiguous_ids_and_small_neighborhood(interactions):
    movies = load_demo()
    knn = CollaborativeFilteringRecommender().fit(movies, interactions)
    assert rank_scores(knn.score(7), [101, 205], 1)[0][0] == 309
    assert knn.score(999) == {}
    svd = MatrixFactorizationRecommender().fit(movies, interactions)
    assert svd.user_factors.shape == (3, 2)
    assert svd.item_factors.shape == (12, 2)
    assert set(svd.score(7)) == set(movies.movieId)
    assert np.isfinite(list(svd.score(7).values())).all()
    assert svd.score(999) == {}


def test_popularity_only_counts_supplied_training_data(interactions):
    model = PopularityRecommender().fit(load_demo(), interactions.iloc[:2])
    assert model.score()[101] == 1
    assert model.score()[309] == 0


def test_rank_fusion_is_scale_invariant_and_excludes_seen():
    scores = [{101: 0.8, 205: 0.4}, {205: 4, 309: 3}]
    scaled = [{101: 80, 205: 40}, scores[1]]
    assert HybridRecommender.score(scores) == HybridRecommender.score(scaled)
    assert 101 not in HybridRecommender.score(scores, exclude=[101])
