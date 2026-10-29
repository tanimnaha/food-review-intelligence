# Sentiment Lab — Food Review Intelligence

A Streamlit web app for the minor project **Sentiment Analysis of Online Food Reviews**. It provides single-review prediction, batch review analysis, evaluation metrics, dataset insights, and a methodology overview.

## Files required for real predictions

This app expects the trained model artifact at:

```text
results/best_model.joblib
```

It can load a complete scikit-learn pipeline that accepts raw review text. If your training code stores only a classifier, also place the fitted vectorizer at `results/tfidf_vectorizer.joblib` or `results/vectorizer.joblib`, and ensure it matches the saved classifier.

The repository intentionally does **not** include a model or the raw dataset. Copy the model artifact from your own project folder before running or deploying. The model and vectorizer must come from your real training run; this app does not fake predictions.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
python -m pip install -r requirements.txt
streamlit run app.py
```

If you put this file inside your current project's `streamlit_app/` folder, the app searches its parent folders for a `results/` folder. In that layout, launch it with:

```bash
streamlit run streamlit_app/app.py
```

## Deploy publicly

See `DEPLOY_TO_STREAMLIT_CLOUD.md`. For a public deployment, the GitHub repository must include `app.py`, `requirements.txt`, `.streamlit/config.toml`, and your trained artifact under `results/`.
