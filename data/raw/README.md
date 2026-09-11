# Raw data

Place these local CSV files in this directory before running the preparation pipeline.

Required files:

- movies_metadata.csv — TMDB movie metadata; requires id and title.
- ratings_small.csv — MovieLens ratings; requires userId, movieId, and rating.
- links_small.csv — MovieLens-to-TMDB mapping; requires movieId and tmdbId.

Optional enrichment files:

- credits.csv — joined on TMDB id; cast and crew are included when present.
- keywords.csv — joined on TMDB id; keywords are included when present.

The CSV files are ignored by Git. Do not commit them unless you have explicit
permission to redistribute them.

Run the pipeline from the repository root:

    python prepare_data.py

It writes these ignored outputs to data/processed:

- movies.csv
- ratings.csv
- manifest.json
