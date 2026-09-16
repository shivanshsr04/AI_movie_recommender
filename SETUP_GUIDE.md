# Setup and migration

## Environment

Use Python 3.12 with an isolated virtual environment. `requirements-lock.txt` pins the resolved application dependencies tested on Linux. `requirements.txt` lists direct dependencies. Do not combine these with an existing project's environment.

macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m streamlit run streamlit_app.py
```

Alternatively, `PYTHON_BIN=python3.12 bash setup.sh` creates the environment and launches the demo. It does not require unrelated CSV files.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-lock.txt
python -m streamlit run streamlit_app.py
```

macOS and Windows have not been verified in the implementation environment.

## Real data

1. Download the [GroupLens MovieLens latest-small archive](https://files.grouplens.org/datasets/movielens/ml-latest-small.zip).
2. Read its `README.txt` usage terms and extract it under `data/raw/`.
3. Verify `data/raw/ml-latest-small/movies.csv` and `ratings.csv` exist.
4. Run:

```bash
python train_models.py --data-dir data/raw/ml-latest-small
python evaluate.py --data-dir data/raw/ml-latest-small
python -m streamlit run streamlit_app.py
```

The app's catalog is built from all supplied ratings for demonstration. `evaluate.py` starts from the raw CSVs and independently trains models on the temporal training partition. It never uses full-data application artifacts to calculate held-out metrics.

MovieLens `movieId` is the canonical identifier throughout. Do not substitute TMDB metadata IDs or unrelated `movies_metadata.csv` files.

## Artifact contract

The default directory is `models/`, relative to the project code. It contains `catalog.json`, `content_features.npz`, and `metadata.json`. JSON contains movie IDs in sorted order and NPZ rows use that same order. Metadata stores their SHA-256 checksums and dimensions.

To select another location:

```bash
python train_models.py --data-dir data/raw/ml-latest-small --output-dir /absolute/path/to/models
MOVIE_MODEL_DIR=/absolute/path/to/models python -m streamlit run streamlit_app.py
```

In PowerShell set `$env:MOVIE_MODEL_DIR = 'C:\absolute\path\to\models'` before launching.

To create reproducible demo artifacts, run `python train_models.py --demo --output-dir models-demo`, then point `MOVIE_MODEL_DIR` there. The untouched repository defaults to demo data when all three standard artifacts are absent. A partial or corrupted artifact set produces an error rather than a silent fallback. Rebuild with the training command.

## Upgrading from the previous version

- Existing pickle files are no longer read. Regenerate with the new training command; old pickles can be archived outside the repository.
- The duplicate trainer, data-shrinking scripts and password-debugging scripts were removed. They are preserved in Git history.
- Guest access replaces the app's login gate. Existing `users.db` files are not deleted or uploaded. Optional account helpers remain available and upgrade legacy password hashes at login.
- The old root `config.toml` was replaced by a valid `.streamlit/config.toml`.
- The app intentionally offers only content recommendations and the real-data popularity baseline. Other methods run through `evaluate.py` until a genuine user-profile workflow is implemented.

## Troubleshooting

| Symptom | Action |
|---|---|
| Missing module | Activate `.venv`; run `python -m pip install -r requirements-lock.txt` |
| Unsupported Python/dependency build failure | Use Python 3.12 in a fresh environment |
| Demo banner appears | Build real artifacts or check `MOVIE_MODEL_DIR` |
| Incomplete/checksum-mismatched artifacts | Re-run the trainer for the chosen directory |
| Missing CSV/column/unknown movie IDs | Use the matching `movies.csv` and `ratings.csv` from the same MovieLens archive |
| Port 8501 occupied | Add `--server.port 8502` to the Streamlit command |

## Tests and deployment

Run `python -m pip install -r requirements-dev.txt` and `python -m pytest -q`. No personal database is touched by the tests.

This change does not publish a website. A deployment needs the same Python/dependency environment, the Streamlit entry point and an explicit decision to use the fictional demo or real-data artifacts. Review MovieLens redistribution and commercial-use terms before publishing transformed data. Never commit local accounts or secrets.
