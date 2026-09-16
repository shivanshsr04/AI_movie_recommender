# Recruiter-facing summary

Built a Python/Streamlit movie-discovery application with sparse TF-IDF and genre-based recommendations, search and analytics. Implemented and compared popularity, collaborative filtering, SVD and hybrid ranking on 100,836 MovieLens ratings using a reproducible global temporal split, documenting baseline performance and cold-start limitations. Added artifact validation, automated regression tests and CI.

## Resume bullets

- Built a guest-accessible movie explorer with content similarity and a popularity baseline, supporting a 9,742-movie MovieLens catalog through validated JSON/NPZ artifacts.
- Evaluated five ranking approaches with Precision@10, Recall@10, NDCG@10 and catalog coverage; reported temporal-split and small-cohort limitations rather than unsupported accuracy claims.
- Added tests for recommendation correctness, identifier mapping, artifact integrity and Streamlit interactions, with a pinned Python 3.12 setup and GitHub Actions workflow.

Do not claim improved recommendation accuracy over popularity, a deployed production service, real-time user personalization or measured business impact from this version.
