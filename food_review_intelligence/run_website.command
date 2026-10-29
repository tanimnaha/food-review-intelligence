#!/bin/zsh
set -e
cd "$(dirname "$0")"
PYTHON="./.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  echo "Could not find the project's .venv Python at .venv/bin/python."
  echo "Open this launcher from your existing Sentiment_Analysis_Minor_Project folder."
  read -k 1 "?Press any key to close..."
  exit 1
fi
"$PYTHON" -m pip install -r streamlit_app/requirements_app.txt
exec "$PYTHON" -m streamlit run streamlit_app/app.py
