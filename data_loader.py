"""Validated preparation of TMDB metadata and MovieLens ratings.

movie_id is a TMDB movie identifier. movielens_id is used only while applying
links_small.csv.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


class DataValidationError(ValueError):
    """Raised when a required source file or column is missing or invalid."""


@dataclass(frozen=True)
class PreparedDatasets:
    """The normalized datasets produced by the preparation pipeline."""

    movies: pd.DataFrame
    ratings: pd.DataFrame
    stats: dict[str, int]


class DataLoader:
    """Load, validate, normalize, and map source movie datasets."""

    REQUIRED_FILES = (
        "movies_metadata.csv",
        "ratings_small.csv",
        "links_small.csv",
    )

    def __init__(self, data_path: str | Path):
        self.data_path = Path(data_path)

    def _path(self, filename: str) -> Path:
        return self.data_path / filename

    def _read_csv(self, filename: str, *, required: bool = True) -> pd.DataFrame | None:
        path = self._path(filename)
        if not path.exists():
            if required:
                raise DataValidationError(
                    f"Missing {filename}. Place it in {self.data_path.resolve()}."
                )
            return None

        try:
            return pd.read_csv(path, low_memory=False)
        except Exception as error:
            raise DataValidationError(f"Could not read {path}: {error}") from error

    @staticmethod
    def _require_columns(frame: pd.DataFrame, filename: str, columns: set[str]) -> None:
        missing = sorted(columns.difference(frame.columns))
        if missing:
            raise DataValidationError(
                f"{filename} is missing required column(s): {', '.join(missing)}."
            )

    @staticmethod
    def _text_column(frame: pd.DataFrame, column: str, default: str = "") -> pd.Series:
        if column not in frame.columns:
            return pd.Series(default, index=frame.index, dtype="string")
        return frame[column].fillna(default).astype("string").str.strip()

    @staticmethod
    def _numeric_column(
        frame: pd.DataFrame, column: str, default: float = 0.0
    ) -> pd.Series:
        if column not in frame.columns:
            return pd.Series(default, index=frame.index, dtype="float64")
        return pd.to_numeric(frame[column], errors="coerce").fillna(default)

    def load_movies(self) -> pd.DataFrame:
        """Load TMDB metadata using a normalized integer movie_id."""
        raw = self._read_csv("movies_metadata.csv")
        self._require_columns(raw, "movies_metadata.csv", {"id", "title"})

        release_dates = pd.to_datetime(
            raw.get("release_date", pd.Series(index=raw.index, dtype="string")),
            errors="coerce",
        )
        titles = self._text_column(raw, "title")
        if "original_title" in raw.columns:
            titles = titles.mask(titles.eq(""), self._text_column(raw, "original_title"))

        movies = pd.DataFrame(
            {
                "movie_id": pd.to_numeric(raw["id"], errors="coerce"),
                "title": titles,
                "overview": self._text_column(raw, "overview"),
                "genres": self._text_column(raw, "genres", "[]"),
                "release_date": release_dates.dt.strftime("%Y-%m-%d").fillna(""),
                "year": release_dates.dt.year.astype("Int64"),
                "vote_average": self._numeric_column(raw, "vote_average"),
                "vote_count": self._numeric_column(raw, "vote_count", 0).astype("int64"),
                "popularity": self._numeric_column(raw, "popularity"),
                "poster_path": self._text_column(raw, "poster_path"),
            }
        )

        movies = movies.dropna(subset=["movie_id"])
        movies = movies[movies["title"].ne("")]
        movies["movie_id"] = movies["movie_id"].astype("int64")
        movies = (
            movies.drop_duplicates(subset=["movie_id"], keep="first")
            .sort_values("movie_id")
            .reset_index(drop=True)
        )

        if movies.empty:
            raise DataValidationError("movies_metadata.csv contains no valid movies.")

        return self._merge_optional_metadata(movies, "credits.csv", ("cast", "crew"))

    def _merge_optional_metadata(
        self, movies: pd.DataFrame, filename: str, fields: tuple[str, ...]
    ) -> pd.DataFrame:
        """Merge optional TMDB metadata without changing the core schema."""
        raw = self._read_csv(filename, required=False)
        if raw is None:
            for field in fields:
                movies[field] = "[]"
            return movies

        self._require_columns(raw, filename, {"id"})
        metadata = pd.DataFrame({"movie_id": pd.to_numeric(raw["id"], errors="coerce")})
        metadata = metadata.dropna(subset=["movie_id"])
        metadata["movie_id"] = metadata["movie_id"].astype("int64")

        for field in fields:
            metadata[field] = self._text_column(raw.loc[metadata.index], field, "[]")

        metadata = metadata.drop_duplicates(subset=["movie_id"], keep="first")
        return movies.merge(metadata, on="movie_id", how="left", validate="one_to_one").fillna(
            {field: "[]" for field in fields}
        )

    def load_movie_metadata(self) -> pd.DataFrame:
        """Load movies plus optional credits and keywords metadata."""
        movies = self.load_movies()
        return self._merge_optional_metadata(movies, "keywords.csv", ("keywords",))

    def load_ratings(self) -> pd.DataFrame:
        """Load valid MovieLens ratings with normalized integer identifiers."""
        raw = self._read_csv("ratings_small.csv")
        self._require_columns(raw, "ratings_small.csv", {"userId", "movieId", "rating"})

        ratings = pd.DataFrame(
            {
                "user_id": pd.to_numeric(raw["userId"], errors="coerce"),
                "movielens_id": pd.to_numeric(raw["movieId"], errors="coerce"),
                "rating": pd.to_numeric(raw["rating"], errors="coerce"),
            }
        )
        if "timestamp" in raw.columns:
            ratings["timestamp"] = pd.to_numeric(raw["timestamp"], errors="coerce")

        ratings = ratings.dropna(subset=["user_id", "movielens_id", "rating"])
        ratings = ratings[ratings["rating"].between(0.5, 5.0)]
        ratings["user_id"] = ratings["user_id"].astype("int64")
        ratings["movielens_id"] = ratings["movielens_id"].astype("int64")
        ratings = ratings.drop_duplicates(
            subset=["user_id", "movielens_id"], keep="last"
        ).reset_index(drop=True)

        if ratings.empty:
            raise DataValidationError("ratings_small.csv contains no valid ratings.")

        return ratings

    def load_links(self) -> pd.DataFrame:
        """Load the MovieLens-to-TMDB mapping needed by collaborative models."""
        raw = self._read_csv("links_small.csv")
        self._require_columns(raw, "links_small.csv", {"movieId", "tmdbId"})

        links = pd.DataFrame(
            {
                "movielens_id": pd.to_numeric(raw["movieId"], errors="coerce"),
                "movie_id": pd.to_numeric(raw["tmdbId"], errors="coerce"),
            }
        ).dropna()

        links["movielens_id"] = links["movielens_id"].astype("int64")
        links["movie_id"] = links["movie_id"].astype("int64")
        links = links.drop_duplicates(subset=["movielens_id"], keep="first")

        if links.empty:
            raise DataValidationError("links_small.csv contains no valid TMDB mappings.")

        return links

    def prepare(
        self, min_user_ratings: int = 5, min_movie_ratings: int = 1
    ) -> PreparedDatasets:
        """Build clean movie metadata and TMDB-mapped ratings datasets."""
        if min_user_ratings < 1 or min_movie_ratings < 1:
            raise ValueError("Minimum rating thresholds must be positive integers.")

        movies = self.load_movie_metadata()
        source_ratings = self.load_ratings()
        links = self.load_links()

        mapped_ratings = source_ratings.merge(
            links, on="movielens_id", how="inner", validate="many_to_one"
        )
        mapped_ratings = mapped_ratings[
            mapped_ratings["movie_id"].isin(movies["movie_id"])
        ]
        mapped_ratings = mapped_ratings.drop(columns=["movielens_id"])
        mapped_ratings = mapped_ratings.drop_duplicates(
            subset=["user_id", "movie_id"], keep="last"
        )

        ratings = mapped_ratings
        movie_counts = ratings["movie_id"].value_counts()
        ratings = ratings[
            ratings["movie_id"].isin(
                movie_counts[movie_counts >= min_movie_ratings].index
            )
        ]

        user_counts = ratings["user_id"].value_counts()
        ratings = ratings[
            ratings["user_id"].isin(
                user_counts[user_counts >= min_user_ratings].index
            )
        ]
        ratings = ratings.sort_values(["user_id", "movie_id"]).reset_index(drop=True)

        if ratings.empty:
            raise DataValidationError(
                "No ratings remain after applying mappings and rating thresholds."
            )

        stats = {
            "movies": int(len(movies)),
            "source_ratings": int(len(source_ratings)),
            "mapped_ratings": int(len(mapped_ratings)),
            "ratings": int(len(ratings)),
            "users": int(ratings["user_id"].nunique()),
            "rated_movies": int(ratings["movie_id"].nunique()),
            "unmapped_ratings": int(len(source_ratings) - len(mapped_ratings)),
            "ratings_filtered_by_thresholds": int(
                len(mapped_ratings) - len(ratings)
            ),
        }
        return PreparedDatasets(movies=movies, ratings=ratings, stats=stats)

    @staticmethod
    def write_processed(
        prepared: PreparedDatasets, output_path: str | Path
    ) -> dict[str, Path]:
        """Write reproducible processed datasets and a small manifest."""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        movies_path = output_dir / "movies.csv"
        ratings_path = output_dir / "ratings.csv"
        manifest_path = output_dir / "manifest.json"

        prepared.movies.to_csv(movies_path, index=False)
        prepared.ratings.to_csv(ratings_path, index=False)
        manifest_path.write_text(
            json.dumps(
                {
                    "stats": prepared.stats,
                    "movie_columns": list(prepared.movies.columns),
                    "rating_columns": list(prepared.ratings.columns),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return {
            "movies": movies_path,
            "ratings": ratings_path,
            "manifest": manifest_path,
        }


def prepare_datasets(
    raw_data_path: str | Path = "data/raw",
    output_path: str | Path = "data/processed",
    min_user_ratings: int = 5,
    min_movie_ratings: int = 1,
) -> tuple[PreparedDatasets, dict[str, Path]]:
    """Prepare and persist datasets with the repository's default paths."""
    prepared = DataLoader(raw_data_path).prepare(
        min_user_ratings=min_user_ratings,
        min_movie_ratings=min_movie_ratings,
    )
    return prepared, DataLoader.write_processed(prepared, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and prepare TMDB metadata and MovieLens ratings."
    )
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--output-dir", default="data/processed")
    parser.add_argument("--min-user-ratings", type=int, default=5)
    parser.add_argument("--min-movie-ratings", type=int, default=1)
    args = parser.parse_args()

    try:
        prepared, paths = prepare_datasets(
            raw_data_path=args.raw_dir,
            output_path=args.output_dir,
            min_user_ratings=args.min_user_ratings,
            min_movie_ratings=args.min_movie_ratings,
        )
    except (DataValidationError, ValueError) as error:
        print(f"Data preparation failed: {error}")
        return 1

    print("Data preparation complete.")
    for name, value in prepared.stats.items():
        print(f"  {name.replace('_', ' ')}: {value:,}")
    for name, path in paths.items():
        print(f"  {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
