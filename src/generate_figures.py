
from pathlib import Path
import textwrap
import shutil

import joblib
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from sklearn.model_selection import train_test_split


# ============================================================
# PROJECT PATHS AND SETTINGS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "yelp_sentiment_master_dataset.csv"
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"

FIGURES.mkdir(parents=True, exist_ok=True)

LABELS = ["Negative", "Neutral", "Positive"]

MODEL_NAMES = {
    "MultinomialNB": "Multinomial Naive Bayes",
    "LogisticRegression": "Logistic Regression",
    "LinearSVM": "Linear SVM",
}

COLORS = {
    "Negative": "#D9534F",
    "Neutral": "#D9A441",
    "Positive": "#299764",
}


def save_figure(filename):
    """Save the current plot as a high-resolution PNG."""
    path = FIGURES / filename
    plt.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Saved: {path.relative_to(ROOT)}")


def load_clean_data():
    """Load data with the same essential filtering as model training."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required = {"text", "rating_review", "stars_review"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Dataset is missing columns: {missing}")

    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df["rating_review"] = (
        df["rating_review"].fillna("").astype(str).str.strip().str.title()
    )

    df = df[
        df["text"].ne("") & df["rating_review"].isin(LABELS)
    ].copy()

    # Match the training script's duplicate-text handling.
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)
    return df


# ============================================================
# FIGURE 1: PROJECT METHODOLOGY WORKFLOW
# ============================================================

def make_workflow():
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5, 0.92,
        "Sentiment Analysis: Project Methodology",
        ha="center", va="center",
        fontsize=21, fontweight="bold"
    )

    steps = [
        ("1. Dataset", "Online food reviews\nand sentiment labels"),
        ("2. Preprocessing", "Clean text, remove\ninvalid rows and duplicates"),
        ("3. Data split", "80% training\n20% testing; stratified"),
        ("4. Feature extraction", "TF-IDF representation\nunigrams and bigrams"),
        ("5. Model training", "Naive Bayes, Logistic\nRegression and Linear SVM"),
        ("6. Evaluation", "Accuracy, precision, recall\nand F1-scores"),
    ]

    x_positions = [0.018, 0.183, 0.348, 0.513, 0.678, 0.843]
    box_width = 0.139
    box_height = 0.38
    y = 0.39

    for i, (heading, description) in enumerate(steps):
        box = FancyBboxPatch(
            (x_positions[i], y),
            box_width, box_height,
            boxstyle="round,pad=0.009,rounding_size=0.015",
            linewidth=1.6,
            edgecolor="#426A8C",
            facecolor="#EFF5FA",
        )
        ax.add_patch(box)

        ax.text(
            x_positions[i] + box_width / 2,
            y + box_height * 0.68,
            heading,
            ha="center", va="center",
            fontsize=10.5, fontweight="bold",
            wrap=True,
        )

        ax.text(
            x_positions[i] + box_width / 2,
            y + box_height * 0.37,
            description,
            ha="center", va="center",
            fontsize=9,
            linespacing=1.5,
            wrap=True,
        )

        if i < len(steps) - 1:
            start = (x_positions[i] + box_width + 0.002, y + box_height / 2)
            end = (x_positions[i + 1] - 0.004, y + box_height / 2)

            ax.add_patch(
                FancyArrowPatch(
                    start, end,
                    arrowstyle="-|>",
                    mutation_scale=13,
                    color="#426A8C",
                    linewidth=1.4,
                )
            )

    ax.text(
        0.5, 0.20,
        "The best-performing model is selected using macro F1-score.",
        ha="center", va="center", fontsize=12
    )

    plt.tight_layout()
    save_figure("fig01_methodology_workflow.png")


# ============================================================
# FIGURE 2: SENTIMENT DISTRIBUTION
# ============================================================

def make_sentiment_distribution(df):
    counts = df["rating_review"].value_counts().reindex(
        ["Positive", "Negative", "Neutral"], fill_value=0
    )

    fig, ax = plt.subplots(figsize=(9, 5.5))

    bars = ax.bar(
        counts.index,
        counts.values,
        color=[COLORS[label] for label in counts.index],
        width=0.62,
    )

    ax.set_title("Distribution of Food Review Sentiments",
                 fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Sentiment category")
    ax.set_ylabel("Number of reviews")
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.set_axisbelow(True)

    for bar, count in zip(bars, counts.values):
        percentage = count / counts.sum() * 100
        ax.annotate(
            f"{count:,}\n({percentage:.1f}%)",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center", va="bottom", fontsize=10,
            xytext=(0, 4), textcoords="offset points",
        )

    plt.tight_layout()
    save_figure("fig02_sentiment_distribution.png")


# ============================================================
# FIGURE 3: STAR-RATING DISTRIBUTION
# ============================================================

def make_rating_distribution(df):
    ratings = pd.to_numeric(df["stars_review"], errors="coerce").dropna()
    counts = ratings.value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(9, 5.5))

    bars = ax.bar(
        counts.index.astype(str),
        counts.values,
        color="#4477AA",
        width=0.65,
    )

    ax.set_title("Distribution of Customer Star Ratings",
                 fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Star rating")
    ax.set_ylabel("Number of reviews")
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.set_axisbelow(True)

    for bar, count in zip(bars, counts.values):
        ax.annotate(
            f"{count:,}",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center", va="bottom", fontsize=9,
            xytext=(0, 3), textcoords="offset points",
        )

    plt.tight_layout()
    save_figure("fig03_star_rating_distribution.png")


# ============================================================
# FIGURE 4: TRAINING AND TESTING SENTIMENT DISTRIBUTION
# ============================================================

def make_split_distribution(df):
    _, _, y_train, y_test = train_test_split(
        df["text"],
        df["rating_review"],
        test_size=0.20,
        random_state=42,
        stratify=df["rating_review"],
    )

    split_percentages = pd.DataFrame({
        "All reviews": (
            df["rating_review"].value_counts(normalize=True)
        ),
        "Training set": y_train.value_counts(normalize=True),
        "Test set": y_test.value_counts(normalize=True),
    }).reindex(LABELS).fillna(0) * 100

    ax = split_percentages.plot(
        kind="bar",
        figsize=(10, 5.8),
        color=["#4477AA", "#66A182", "#D9A441"],
        width=0.78,
    )

    ax.set_title("Sentiment Proportions Across Data Splits",
                 fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Sentiment category")
    ax.set_ylabel("Percentage of reviews")
    ax.set_xticklabels(LABELS, rotation=0)
    ax.legend(title="Dataset portion")
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.set_axisbelow(True)

    plt.tight_layout()
    save_figure("fig04_train_test_distribution.png")


# ============================================================
# FIGURE 5: OVERALL MODEL PERFORMANCE COMPARISON
# ============================================================

def make_model_comparison():
    path = RESULTS / "model_comparison.csv"

    if not path.exists():
        print("Skipping model comparison: model_comparison.csv not found.")
        return

    scores = pd.read_csv(path)

    metrics = [
        "accuracy",
        "macro_precision",
        "macro_recall",
        "macro_f1",
        "weighted_f1",
    ]

    missing = set(metrics + ["model"]) - set(scores.columns)
    if missing:
        raise ValueError(f"Missing comparison columns: {missing}")

    labels = [
        MODEL_NAMES.get(name, name) for name in scores["model"]
    ]

    ax = scores.set_index("model")[metrics].plot(
        kind="bar",
        figsize=(12, 6.5),
        width=0.78,
        color=["#4477AA", "#66A182", "#D9A441", "#C76D4D", "#8172B2"],
    )

    ax.set_title("Comparative Performance of Machine Learning Models",
                 fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Classification algorithm")
    ax.set_ylabel("Score (%)")
    ax.set_xticklabels(labels, rotation=12, ha="right")
    ax.set_ylim(0, 1.08)
    ax.set_yticks([i / 10 for i in range(11)])
    ax.set_yticklabels([f"{i * 10}%" for i in range(11)])
    ax.legend(
        ["Accuracy", "Macro Precision", "Macro Recall",
         "Macro F1-score", "Weighted F1-score"],
        loc="lower right",
        fontsize=9,
    )
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.set_axisbelow(True)

    # Metrics in the CSV are fractions from 0 to 1.
    # The displayed axis is converted to percentages.
    plt.tight_layout()
    save_figure("fig05_model_performance_comparison.png")


# ============================================================
# FIGURE 6: CLASS-WISE F1-SCORE COMPARISON
# ============================================================

def make_classwise_f1():
    report_paths = {
        key: RESULTS / f"report_{key}.csv"
        for key in MODEL_NAMES
    }

    available = {key: path for key, path in report_paths.items()
                 if path.exists()}

    if not available:
        print("Skipping class-wise F1: classification reports not found.")
        return

    values = {}

    for model_key, path in available.items():
        report = pd.read_csv(path, index_col=0)
        class_scores = {}

        for label in LABELS:
            if label in report.index and "f1-score" in report.columns:
                class_scores[label] = float(
                    report.loc[label, "f1-score"]
                )

        values[MODEL_NAMES[model_key]] = class_scores

    comparison = pd.DataFrame(values).reindex(LABELS) * 100

    ax = comparison.plot(
        kind="bar",
        figsize=(10, 6),
        width=0.78,
        color=["#4477AA", "#66A182", "#C76D4D"],
    )

    ax.set_title("Class-wise F1-score by Model",
                 fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Actual sentiment category")
    ax.set_ylabel("F1-score (%)")
    ax.set_xticklabels(LABELS, rotation=0)
    ax.set_ylim(0, 105)
    ax.legend(title="Algorithm")
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.set_axisbelow(True)

    plt.tight_layout()
    save_figure("fig06_classwise_f1_comparison.png")


# ============================================================
# FIGURE 7: SAMPLE PREDICTIONS FROM THE SAVED BEST MODEL
# ============================================================

def make_prediction_examples():
    model_path = RESULTS / "best_model.joblib"
    name_path = RESULTS / "best_model_name.txt"

    if not model_path.exists():
        print("Skipping prediction examples: saved best model not found.")
        return

    model = joblib.load(model_path)

    if name_path.exists():
        best_name = name_path.read_text(encoding="utf-8").strip()
    else:
        best_name = "Saved best model"

    examples = [
        "The food was delicious and the service was excellent.",
        "The food was cold and the delivery was extremely late.",
        "The food was average and nothing was particularly special.",
    ]

    predictions = model.predict(examples)

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5, 0.94,
        "Sample Predictions from the Trained Model",
        ha="center", va="center",
        fontsize=18, fontweight="bold",
    )

    ax.text(
        0.5, 0.885,
        f"Model: {MODEL_NAMES.get(best_name, best_name)}",
        ha="center", va="center", fontsize=11,
    )

    y_positions = [0.68, 0.44, 0.20]

    for review, prediction, y in zip(examples, predictions, y_positions):
        card = FancyBboxPatch(
            (0.045, y - 0.075),
            0.91, 0.17,
            boxstyle="round,pad=0.01,rounding_size=0.015",
            facecolor="#F4F6F8",
            edgecolor="#C5CDD5",
            linewidth=1.2,
        )
        ax.add_patch(card)

        wrapped_review = textwrap.fill(review, width=100)

        ax.text(
            0.07, y + 0.025,
            "Review: " + wrapped_review,
            ha="left", va="center", fontsize=10.5,
        )

        ax.text(
            0.07, y - 0.035,
            f"Predicted sentiment: {prediction}",
            ha="left", va="center",
            fontsize=11, fontweight="bold",
            color=COLORS.get(str(prediction), "#333333"),
        )

    ax.text(
        0.5, 0.035,
        "Predictions are model outputs and may not always match human judgement.",
        ha="center", va="center", fontsize=9, color="#555555",
    )

    plt.tight_layout()
    save_figure("fig07_sample_predictions.png")


# ============================================================
# COPY THE THREE EXISTING CONFUSION MATRICES
# ============================================================

def collect_confusion_matrices():
    model_keys = ["MultinomialNB", "LogisticRegression", "LinearSVM"]

    for key in model_keys:
        filename = f"confusion_matrix_{key}.png"
        source = RESULTS / filename

        if source.exists():
            destination = FIGURES / filename
            shutil.copy2(source, destination)
            print(f"Collected: {destination.relative_to(ROOT)}")
        else:
            print(f"Not found yet: {source.relative_to(ROOT)}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("GENERATING PROJECT FIGURES")
    print("=" * 60)

    df = load_clean_data()

    print(f"Clean dataset rows: {len(df):,}")
    print(f"Unique review texts: {df['text'].nunique():,}")

    make_workflow()
    make_sentiment_distribution(df)
    make_rating_distribution(df)
    make_split_distribution(df)
    make_model_comparison()
    make_classwise_f1()
    make_prediction_examples()
    collect_confusion_matrices()

    print("\n" + "=" * 60)
    print("FIGURE GENERATION FINISHED")
    print(f"Open this folder: {FIGURES}")
    print("=" * 60)


if __name__ == "__main__":
    main()
