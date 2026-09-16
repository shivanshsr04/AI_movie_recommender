"""Sparse recommendation models with explicit item IDs and deterministic ranks."""
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer, normalize
from sklearn.decomposition import TruncatedSVD


def rank_scores(scores, exclude=(), k=10):
    """Stable top K; never confuse item positions with external movie IDs."""
    excluded = set(exclude)
    candidates = [(int(mid), float(score)) for mid, score in scores.items()
                  if mid not in excluded and np.isfinite(score)]
    return sorted(candidates, key=lambda pair: (-pair[1], pair[0]))[:max(0, k)]


class ContentBasedRecommender:
    def fit(self, movies):
        self.movies = movies.reset_index(drop=True).copy()
        self.movie_ids = self.movies.movieId.to_numpy()
        self.positions = {int(mid): i for i, mid in enumerate(self.movie_ids)}
        # MovieLens contains titles and genres, not plot summaries.
        titles = self.movies.title.str.replace(r'\(\d{4}\)', '', regex=True)
        texts = titles + ' ' + self.movies.overview.fillna('')
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2),
                                         max_features=20000, min_df=1)
        try:
            text_features = self.vectorizer.fit_transform(texts)
        except ValueError as exc:
            if 'empty vocabulary' not in str(exc):
                raise
            text_features = sparse.csr_matrix((len(movies), 1))
        self.genre_encoder = MultiLabelBinarizer(sparse_output=True)
        genre_features = self.genre_encoder.fit_transform(
            self.movies.genres.fillna('').map(lambda value: [g for g in value.split('|') if g]))
        # Concatenate different feature spaces instead of adding unequal widths.
        blocks = [0.6 * normalize(text_features)]
        if genre_features.shape[1]:
            blocks.append(0.4 * normalize(genre_features))
        self.features = normalize(sparse.hstack(blocks, format='csr'))
        return self

    def score(self, seed_ids):
        positions = [self.positions[mid] for mid in dict.fromkeys(seed_ids)
                     if mid in self.positions]
        if not positions:
            return {}
        profile = normalize(sparse.csr_matrix(self.features[positions].mean(axis=0)))
        scores = (self.features @ profile.T).toarray().ravel()
        return dict(zip(self.movie_ids, np.clip(scores, 0.0, 1.0)))

    def recommend(self, movie_id, k=10):
        return rank_scores(self.score([movie_id]), exclude=[movie_id], k=k)


class PopularityRecommender:
    def fit(self, movies, ratings):
        # Only the interactions passed here contribute to popularity.
        self.scores = ratings.groupby('movieId').size().reindex(movies.movieId, fill_value=0).to_dict()
        return self

    def score(self):
        return self.scores.copy()


def interaction_matrix(movies, ratings):
    movie_ids = movies.movieId.to_numpy()
    user_ids = np.sort(ratings.userId.unique())
    user_pos = {int(uid): i for i, uid in enumerate(user_ids)}
    movie_pos = {int(mid): i for i, mid in enumerate(movie_ids)}
    if not set(ratings.movieId).issubset(movie_pos):
        raise ValueError('Ratings contain unknown movie IDs')
    matrix = sparse.csr_matrix((ratings.rating.to_numpy(),
                               (ratings.userId.map(user_pos), ratings.movieId.map(movie_pos))),
                              shape=(len(user_ids), len(movie_ids)))
    return matrix, user_pos, movie_ids


class CollaborativeFilteringRecommender:
    def fit(self, movies, ratings, n_neighbors=20):
        self.matrix, self.user_pos, self.movie_ids = interaction_matrix(movies, ratings)
        self.normalized = normalize(self.matrix)
        self.n_neighbors = n_neighbors
        return self

    def score(self, user_id):
        if user_id not in self.user_pos:
            return {}
        pos = self.user_pos[user_id]
        similarities = (self.normalized @ self.normalized[pos].T).toarray().ravel()
        similarities[pos] = 0.0
        neighbors = np.argsort(-similarities, kind='stable')[:max(0, self.n_neighbors)]
        neighbors = neighbors[similarities[neighbors] > 0]
        if not len(neighbors):
            return {}
        weights = similarities[neighbors]
        values = self.matrix[neighbors]
        numerator = np.asarray(values.T @ weights).ravel()
        denominator = np.asarray(values.astype(bool).T @ weights).ravel()
        scores = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator > 0)
        return {int(mid): float(score) for mid, score, count in zip(self.movie_ids, scores, denominator)
                if count > 0}


class MatrixFactorizationRecommender:
    """TruncatedSVD on zero-filled ratings: a baseline, not a masked-loss model."""
    def fit(self, movies, ratings, n_factors=32, random_state=42):
        matrix, self.user_pos, self.movie_ids = interaction_matrix(movies, ratings)
        if min(matrix.shape) < 2:
            raise ValueError('SVD requires at least two users and two movies')
        factors = min(n_factors, min(matrix.shape) - 1)
        self.svd = TruncatedSVD(n_components=factors, random_state=random_state)
        self.user_factors = self.svd.fit_transform(matrix)
        self.item_factors = self.svd.components_.T
        return self

    def score(self, user_id):
        if user_id not in self.user_pos:
            return {}
        scores = self.user_factors[self.user_pos[user_id]] @ self.item_factors.T
        return dict(zip(self.movie_ids, scores))


class HybridRecommender:
    """Reciprocal-rank fusion avoids mixing incompatible raw score scales."""
    @staticmethod
    def score(score_maps, weights=None, exclude=()):
        weights = weights if weights is not None else [1.0] * len(score_maps)
        if len(weights) != len(score_maps) or any(w < 0 for w in weights):
            raise ValueError('Provide one nonnegative weight per model')
        fused = {}
        for scores, weight in zip(score_maps, weights):
            for rank, (mid, _) in enumerate(rank_scores(scores, exclude, len(scores)), 1):
                fused[mid] = fused.get(mid, 0.0) + weight / (60 + rank)
        return fused
