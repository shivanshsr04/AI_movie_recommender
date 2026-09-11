#!/usr/bin/env bash
# Run the current Streamlit demonstration release.
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 is required. Install it from https://www.python.org/downloads/."
  exit 1
fi

if [ ! -d "venv" ]; then
  "$PYTHON_BIN" -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [ ! -f "models/clean_movies.pkl" ]; then
  echo "Missing demonstration data at models/clean_movies.pkl."
  echo "Restore the tracked demonstration artifacts before running the app."
  exit 1
fi

echo "Starting the Movie Discovery App at http://localhost:8501"
streamlit run streamlit_app.py
