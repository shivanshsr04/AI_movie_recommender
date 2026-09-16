#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" -c 'import sys; assert sys.version_info[:2] == (3, 12), "Use Python 3.12 for the tested environment"'
"$PYTHON_BIN" -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
exec .venv/bin/python -m streamlit run streamlit_app.py
