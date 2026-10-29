#!/bin/zsh
set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -x "$PROJECT_DIR/.venv/bin/python" ]; then
  echo "Creating the project's .venv environment..."
  python3 -m venv .venv
fi

echo "Installing the website dependencies into this project's .venv..."
"$PROJECT_DIR/.venv/bin/python" -m pip install --upgrade pip
"$PROJECT_DIR/.venv/bin/python" -m pip install -r "$PROJECT_DIR/streamlit_app/requirements_app.txt"

echo "Starting the Food Review Sentiment Analyzer..."
exec "$PROJECT_DIR/.venv/bin/python" -m streamlit run "$PROJECT_DIR/streamlit_app/app.py"
