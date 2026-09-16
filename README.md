# Movie Recommendation Explorer

A Python and Streamlit movie-discovery project with **working TF-IDF + genre recommendations**, a popularity baseline, and reproducible offline experiments with collaborative filtering, SVD and hybrid ranking.

The application supports guest access. A small fictional catalog runs without downloads; a separate MovieLens workflow builds a real catalog of 9,742 movies. Similarity scores are computed from features, not assigned by rank.

## What works

| Capability | Status |
|---|---|
| Movie search, content recommendations and genre analytics | Available in the app |
| Rating-count popularity baseline and real-data analytics | Available after MovieLens training |
| User-based collaborative filtering, TruncatedSVD, hybrid rank fusion | Implemented and evaluated offline; not offered as guest personalization |
| Precision@10, Recall@10, NDCG@10 and catalog coverage | Reproducible evaluation with committed results |
| User preference collection / production accounts | Not part of the guest app |
| Hosted demo | Not deployed by this change; run locally below |

## Quick start

Use **Python 3.12**. The resolved dependency set was tested on Linux; macOS and Windows commands are provided but those platforms have not been tested here.

```bash
git clone https://github.com/shivanshsr04/AI_movie_recommender.git
cd AI_movie_recommender
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m streamlit run streamlit_app.py
```

On Windows, create the environment with `py -3.12 -m venv .venv` and activate it with `.venv\Scripts\Activate.ps1` in PowerShell.

Open `http://localhost:8501`. No account, API key or training step is needed for the **12-film fictional demo**. Select *Orbit Rescue* and click **Find movies**; the related space-adventure *The Last Starship* should appear first. The banner clearly distinguishes authored demo examples from real movie data.

## Use real MovieLens data

Download [MovieLens latest-small from GroupLens](https://grouplens.org/datasets/movielens/latest/) and extract it into `data/raw/ml-latest-small/`. Review the dataset's included usage terms. The raw data and generated artifacts are intentionally not committed.

```bash
python train_models.py --data-dir data/raw/ml-latest-small
python -m streamlit run streamlit_app.py
```

Training validates IDs and columns, builds a sparse content matrix and writes three artifacts to `models/`: `catalog.json`, `content_features.npz` and `metadata.json`. Metadata records source checksums, feature settings and package versions. The app verifies artifact checksums before loading. No pickle deserialization is used.

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for troubleshooting, custom artifact paths and upgrading from the previous repository version.

## How recommendations work

- **Content:** TF-IDF of titles and optional descriptions, with unigram/bigram features. Separately normalized genre indicators and text features are weighted 0.4 and 0.6, concatenated, then normalized. Cosine similarity ranks candidates. MovieLens small includes titles and genres, **not plot summaries**.
- **Popularity:** number of ratings per movie. The app uses the loaded catalog; offline evaluation counts only training interactions.
- **Collaborative:** cosine similarity between user-rating vectors; neighbor ratings are aggregated with similarity weights.
- **SVD:** deterministic TruncatedSVD of the zero-filled user–item matrix. This is a simple baseline, not an explicit-feedback model optimizing only observed ratings.
- **Hybrid:** equal-weight reciprocal-rank fusion of content, collaborative and SVD rankings. Rank fusion avoids adding incompatible raw score scales.

All recommendation paths preserve external movie IDs. The app excludes the selected film; evaluation excludes every movie rated in the user's training history. The content model uses sparse features and does not allocate an all-pairs movie similarity matrix.

**A similarity score is not a confidence percentage or a prediction of whether you will like a film.**

## Measured results

[Full reproducible results](reports/movielens-evaluation.json) · [Evaluation protocol and limitations](docs/EVALUATION.md)

```bash
python evaluate.py --data-dir data/raw/ml-latest-small
```

The evaluated snapshot contains **100,836 ratings, 610 users and 9,742 movies**. A global timestamp split produces 80,669 training, 10,083 validation and 10,084 test interactions. Test metrics below are macro averages over **18 eligible warm users**; 54 test users lack training history and two have no relevant held-out item. This small cohort limits generalization.

| Method | Precision@10 | Recall@10 | NDCG@10 | Catalog coverage |
|---|---:|---:|---:|---:|
| Popularity | 0.0889 | 0.0433 | **0.1042** | 0.62% |
| Content | 0.0000 | 0.0000 | 0.0000 | 0.50% |
| Collaborative KNN | 0.0056 | 0.0008 | 0.0061 | 1.20% |
| SVD | 0.0722 | **0.0451** | 0.0817 | **1.37%** |
| Hybrid | 0.0833 | 0.0436 | 0.0754 | **1.37%** |

**The learned methods did not outperform popularity on test NDCG@10.** Content similarity provides an item-exploration feature but these results do not establish strong personalized ranking. The offline content experiment averages a user's positively rated training items; that task differs from selecting one seed in the UI. No “accuracy improvement” or production-readiness claim is made.

Parameters were fixed before evaluating these partitions; no test-based tuning was performed. The complete catalog's metadata is assumed known. Movie release availability is not reconstructed at each historical time. These are portfolio experiments, not publication-grade benchmark claims.

## Repository map

| Path | Purpose |
|---|---|
| `streamlit_app.py` | Guest UI, search and analytics |
| `app_service.py` | Validated artifact loading and UI inference |
| `data_loader.py` | MovieLens validation and demo loading |
| `recommender_models.py` | Content, popularity, collaborative, SVD and hybrid models |
| `train_models.py` | Single artifact-building entry point |
| `evaluate.py` | Temporal split, ranking metrics and experiment report |
| `data/demo/movies.csv` | Authored fictional examples |
| `tests/` | Model, pipeline, auth and Streamlit regression tests |
| `reports/` | Generated real-data evaluation results |
| `utils/auth.py` | Optional local account helpers, unused by guest app |

## Development

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

GitHub Actions runs the tests and demo training on Python 3.12. Tests check seed-sensitive recommendations, self-exclusion, noncontiguous IDs, small user neighborhoods, artifact corruption, temporal split boundaries, known metric values and Streamlit interactions. Authentication helpers use salted PBKDF2 and upgrade old SHA-256 hashes on successful login; they are not a production authentication service.

## Next milestones

1. Improve content features with properly licensed plot metadata and evaluate improvements on validation data.
2. Address cold users and evaluate over a larger, well-defined cohort before making broad quality claims.
3. Add user feedback and deploy a reviewed demo with an explicit data/license policy.

## Author and attribution

**Shivansh Srivastava** · B.Tech Information Technology · [GitHub](https://github.com/shivanshsr04)

MovieLens is provided by GroupLens, University of Minnesota. Cite: F. Maxwell Harper and Joseph A. Konstan (2015), *The MovieLens Datasets: History and Context*, [DOI: 10.1145/2827872](https://doi.org/10.1145/2827872). Its usage terms are separate from this project's code and include restrictions on commercial use. See the README included with the downloaded dataset. GroupLens does not endorse this project.

No code license has been selected yet. Dataset access does not grant rights to use the project code under an open-source license.
