# Evaluation protocol and interpretation

## Reproduction

```bash
python -m pip install -r requirements-lock.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python evaluate.py --data-dir data/raw/ml-latest-small
```

Thread limits are optional and were used for the recorded run. The JSON report includes file hashes, library versions, split boundaries and fixed parameters. Raw data are not redistributed here. `ml-latest-small` is a development dataset, so hashes identify the exact snapshot; it should not be treated as a permanent publication benchmark.

## Protocol

- Split **globally by rating timestamp**, at the 80th and 90th percentiles. Equal timestamps are never split across boundaries.
- Fit interaction models and popularity counts only on the first partition. Validation and test use the same training fit; validation interactions do not enter test history.
- TF-IDF uses the full known catalog metadata (a transductive catalog assumption), without held-out ratings.
- Evaluate warm users with at least five training ratings, at least one training rating >= 4, and at least one positive held-out rating (>= 4).
- Candidate set: complete movie catalog, excluding all items already rated in training. There is no sampled-negative evaluation. Relevant items are the user's positive held-out items. Precision divides by K even if a model returns fewer than K.
- Content profiles average features of all positively rated training items. KNN uses up to 20 cosine-similar users with similarity-weighted rating averages; if no usable neighbors exist, it falls back to training popularity. SVD uses 32 factors (bounded by matrix size), seed 42 and zero-filled missing ratings.
- Hybrid uses equal reciprocal-rank weights with denominator `60 + rank`, excluding seen items before fusion.
- Report macro-averaged Precision@10, Recall@10 and NDCG@10 plus the fraction of the full catalog appearing in any top-10 list.
- All parameters are fixed, without tuning on validation or test. Validation is reported to support later development, not used to select this reported run's parameters.

## Findings and failure analysis

Popularity achieved test NDCG@10 of **0.1042**, compared with **0.0817** for SVD and **0.0754** for hybrid. Content reached zero hits in the 18-user test cohort. These results are retained rather than replaced by invented precision or “accuracy” claims.

The test window has 74 users but only 18 are evaluated: 54 have no training history, and two have no positive test item. The validation cohort has 21 eligible users out of 62. The evaluation describes established users, not the whole service population. Only one evaluated test user has 5–19 training ratings; there is insufficient evidence for a robust sparse-user subgroup conclusion.

The full matrix is approximately 98.3% unobserved. There are 1,875 catalog movies with no training ratings, so interaction models cannot learn their preferences. The content model can represent these items but title/genre features do not imply strong preference prediction. A single-seed UI demonstration is not the same task as aggregating historical preferences across time.

KNN can favor movies highly rated by very few neighbors. Zero-filled SVD models missing entries as zeros rather than optimizing an observed-rating loss. The hybrid ranking inherits weak component ranks. These are concrete improvement targets, not proven explanations of every error.

## Limits and next experiments

- The full catalog is treated as known; historical release/availability is not reconstructed. Avoid claims of a complete time-aware production simulation.
- No confidence intervals, repeated datasets or online A/B test are included. Small-cohort differences are descriptive, not statistically established wins.
- Compare shrinkage-weighted KNN, an observed-feedback factorization objective and richer licensed text features on validation before another test evaluation.
- Design and report cold-user performance separately. Do not quietly discard these users and claim population-wide quality.
- RMSE is not reported: these implementations are evaluated as rankers, not calibrated rating predictors.
