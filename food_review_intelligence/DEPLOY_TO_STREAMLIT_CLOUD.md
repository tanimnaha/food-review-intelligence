# Publish the website so other people can open it

The public web link is created by hosting/deploying the app. `localhost` only points to your own computer; a cloud deployment runs the app on a hosting service and gives it an online URL.

## A. Prepare the deployment folder

Use a small clean repository. It only needs these files:

```text
sentiment-review-app/
├── app.py
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml
└── results/
    ├── best_model.joblib
    ├── best_model_name.txt        (optional)
    ├── model_comparison.csv       (optional)
    └── tfidf_vectorizer.joblib    (only if training saved it separately)
```

Copy your **actual** `results/best_model.joblib` from the trained project into the deployment folder's `results/` folder. If the model file is only a classifier and training saved a separate fitted TF-IDF/vectorizer, include the matching vectorizer too. The raw dataset and `.venv` are not needed to serve predictions.

Before sharing a public repository, check that you are comfortable making its code and model downloadable. Do not upload passwords, API keys, private information, or the full raw dataset unnecessarily. GitHub blocks individual files larger than 100 MB; if the model file exceeds that size, do not try to upload it through the normal web interface.

## B. Test before publishing

In Terminal, navigate to the deployment folder and run:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Test positive, negative, and neutral examples. If the prediction fails locally, fix that before deployment. The hosted app must use the same fitted model/vectorizer and compatible scikit-learn version as the training environment.

## C. Put the app on GitHub

1. Sign in to GitHub and create a new repository, for example `sentiment-review-app`.
2. Choose **Public** if you want the source code and model to be openly viewable. Do not upload `.venv/`, the raw dataset, or private files.
3. Upload the contents of this deployment folder, including the model under `results/`.
4. Check that `app.py`, `requirements.txt`, `.streamlit/config.toml`, and `results/best_model.joblib` are visible in the repository.

## D. Deploy to Streamlit Community Cloud

1. Open https://share.streamlit.io/ and sign in with GitHub.
2. Click **Create app** and choose the repository you just created.
3. Set the branch to `main` and the app file path to `app.py`.
4. Click **Deploy** and watch the app logs for any errors.
5. Once it launches, Streamlit assigns a URL ending in `streamlit.app`. Open that link in a private/incognito window to confirm that people can access it without your laptop running.
6. Use the app's **Share** or **Settings** options to make sure viewer access is public if that is what you intend.

## E. Updating the public app

After changing code, push the updated files to the same GitHub repository; Community Cloud syncs the update from GitHub. The public app can become unavailable if the repository loses the model artifact or its dependencies fail to install, so test locally and review deployment logs after updates.

Official documentation:
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app
