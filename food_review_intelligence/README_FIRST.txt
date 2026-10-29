PREMIUM FOOD REVIEW SENTIMENT WEBSITE

WHAT IS INCLUDED
- app.py: recommended entrypoint for cloud deployment from a clean GitHub repo
- streamlit_app/app.py: same app for your current student project layout
- requirements.txt and streamlit_app/requirements_app.txt
- .streamlit/config.toml: minimalist light theme
- run_website.command: one-command local launcher for your existing project layout
- DEPLOY_TO_STREAMLIT_CLOUD.md: how to get a public streamlit.app link

LOCAL INSTALL
1. Copy streamlit_app/app.py into your existing project folder's streamlit_app/app.py (replace the old app.py).
2. Copy streamlit_app/requirements_app.txt into your existing project's streamlit_app/requirements_app.txt.
3. Copy run_website.command into the top level of your existing project (beside .venv and results).
4. Optional: copy .streamlit/config.toml into the top level of your existing project under a .streamlit folder.
5. In the VS Code terminal at your project root, run: ./run_website.command

MODEL REQUIREMENT
This zip does not contain your model because it lives on your Mac. The app needs your actual trained results/best_model.joblib. It expects a saved fitted pipeline that accepts raw review text. If the classifier and text vectorizer were saved separately, include the matching vectorizer as results/tfidf_vectorizer.joblib or results/vectorizer.joblib.

PUBLIC DEPLOYMENT
For Streamlit Community Cloud, create a clean repository based on the root app.py, requirements.txt, .streamlit/config.toml, and results/best_model.joblib. Follow DEPLOY_TO_STREAMLIT_CLOUD.md. A public URL is only created after you upload the real model and complete deployment; this package itself is not a live hosted website.
