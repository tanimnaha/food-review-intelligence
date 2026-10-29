
from pathlib import Path

import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    ConfusionMatrixDisplay,
)

# Project paths
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/raw/yelp_sentiment_master_dataset.csv"
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

LABELS = ["Negative", "Neutral", "Positive"]


def main():
    print("Loading food-review dataset...")

    df = pd.read_csv(DATA_PATH)

    # Validate the required columns.
    required = {"text", "rating_review"}
    if not required.issubset(df.columns):
        raise ValueError(f"Required columns are missing: {required - set(df.columns)}")

    # Basic cleaning.
    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df["rating_review"] = (
        df["rating_review"].fillna("").astype(str).str.strip().str.title()
    )

    df = df[
        df["text"].ne("") & df["rating_review"].isin(LABELS)
    ].copy()

    original_rows = len(df)
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)

    print(f"Usable reviews: {len(df)}")
    print(f"Duplicate reviews removed: {original_rows - len(df)}")
    print("\nSentiment distribution:")
    print(df["rating_review"].value_counts().reindex(LABELS, fill_value=0))

    # Split into training data (80%) and testing data (20%).
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["rating_review"],
        test_size=0.20,
        random_state=42,
        stratify=df["rating_review"],
    )

    print(f"\nTraining reviews: {len(X_train)}")
    print(f"Testing reviews: {len(X_test)}")

    # Compare three machine learning algorithms.
    models = {
        "MultinomialNB": MultinomialNB(),
        "LogisticRegression": LogisticRegression(
            max_iter=1000, class_weight="balanced"
        ),
        "LinearSVM": LinearSVC(class_weight="balanced"),
    }

    all_results = []

    for name, classifier in models.items():
        print(f"\n{'=' * 50}")
        print(f"Training {name}...")

        pipeline = Pipeline([
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=30000,
                    sublinear_tf=True,
                ),
            ),
            ("classifier", classifier),
        ])

        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)

        scores = {
            "model": name,
            "accuracy": accuracy_score(y_test, predictions),
            "macro_precision": precision_score(
                y_test, predictions, average="macro", zero_division=0
            ),
            "macro_recall": recall_score(
                y_test, predictions, average="macro", zero_division=0
            ),
            "macro_f1": f1_score(
                y_test, predictions, average="macro", zero_division=0
            ),
            "weighted_f1": f1_score(
                y_test, predictions, average="weighted", zero_division=0
            ),
        }
        all_results.append(scores)

        print(f"Accuracy: {scores['accuracy']:.4f}")
        print(f"Macro F1-score: {scores['macro_f1']:.4f}")
        print("\nDetailed classification report:")
        print(classification_report(
            y_test, predictions, labels=LABELS, zero_division=0
        ))

        report = classification_report(
            y_test,
            predictions,
            labels=LABELS,
            output_dict=True,
            zero_division=0,
        )
        pd.DataFrame(report).transpose().to_csv(
            RESULTS / f"report_{name}.csv"
        )

        ConfusionMatrixDisplay.from_predictions(
            y_test,
            predictions,
            labels=LABELS,
            display_labels=LABELS,
            xticks_rotation="vertical",
        )
        plt.title(f"Confusion Matrix - {name}")
        plt.tight_layout()
        plt.savefig(RESULTS / f"confusion_matrix_{name}.png", dpi=150)
        plt.close()

        joblib.dump(pipeline, RESULTS / f"{name}.joblib")
        print(f"{name} evaluation completed.")

    # Save the comparison table and select the highest macro F1.
    comparison = pd.DataFrame(all_results).sort_values(
        "macro_f1", ascending=False
    )
    comparison.to_csv(RESULTS / "model_comparison.csv", index=False)

    best_name = comparison.iloc[0]["model"]
    best_model = joblib.load(RESULTS / f"{best_name}.joblib")

    joblib.dump(best_model, RESULTS / "best_model.joblib")
    (RESULTS / "best_model_name.txt").write_text(
        best_name, encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("FINAL MODEL COMPARISON")
    print(comparison.to_string(
        index=False, float_format=lambda value: f"{value:.4f}"
    ))
    print(f"\nBest model by macro F1-score: {best_name}")
    print(f"Results saved in: {RESULTS}")


if __name__ == "__main__":
    main()
