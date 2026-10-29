import sys
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import ComplementNB
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from preprocessing import clean_text

DATA_DIR = ROOT / "data" / "splits"
MODELS_DIR = ROOT / "models" / "sentiment_model"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR = REPORTS_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load stratified splits
train_df = pd.read_csv(DATA_DIR / "train.csv")
val_df = pd.read_csv(DATA_DIR / "val.csv")
test_df = pd.read_csv(DATA_DIR / "test.csv")

print(f"Loaded splits: Train={len(train_df):,}, Val={len(val_df):,}, Test={len(test_df):,}")

X_train, y_train = train_df["cleaned_text"].fillna(""), train_df["sentiment_label"]
X_val, y_val = val_df["cleaned_text"].fillna(""), val_df["sentiment_label"]
X_test, y_test = test_df["cleaned_text"].fillna(""), test_df["sentiment_label"]

LABELS = ["negative", "neutral", "positive"]

# 2. Define Candidate Models
# We use TF-IDF with unigrams + bigrams and sublinear term frequency
tfidf = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=2,
    max_features=25000,
    sublinear_tf=True
)

candidates = {
    "TF-IDF + LogisticRegression": Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=25000, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42))
    ]),
    "TF-IDF + LinearSVM": Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=25000, sublinear_tf=True)),
        ("clf", CalibratedClassifierCV(LinearSVC(class_weight="balanced", random_state=42)))
    ]),
    "TF-IDF + ComplementNB": Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=25000, sublinear_tf=True)),
        ("clf", ComplementNB())
    ]),
    "TF-IDF + MLP (Neural Net)": Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=15000, sublinear_tf=True)),
        ("clf", MLPClassifier(hidden_layer_sizes=(100,), max_iter=30, early_stopping=True, random_state=42))
    ])
}

results = []
trained_pipelines = {}

for name, pipe in candidates.items():
    print(f"\n{'='*55}\nTraining {name}...")
    pipe.fit(X_train, y_train)
    trained_pipelines[name] = pipe

    # Evaluate on held-out test set
    preds = pipe.predict(X_test)
    acc = accuracy_score(y_test, preds)
    macro_p = precision_score(y_test, preds, average="macro", zero_division=0)
    macro_r = recall_score(y_test, preds, average="macro", zero_division=0)
    macro_f1 = f1_score(y_test, preds, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_test, preds, average="weighted", zero_division=0)

    # Per-class F1
    rep = classification_report(y_test, preds, labels=LABELS, output_dict=True, zero_division=0)
    neg_f1 = rep["negative"]["f1-score"]
    neu_f1 = rep["neutral"]["f1-score"]
    pos_f1 = rep["positive"]["f1-score"]

    print(f"Accuracy: {acc:.4f} | Macro F1: {macro_f1:.4f} | Neg F1: {neg_f1:.4f} | Neu F1: {neu_f1:.4f} | Pos F1: {pos_f1:.4f}")

    results.append({
        "model": name,
        "accuracy": acc,
        "macro_precision": macro_p,
        "macro_recall": macro_r,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "negative_f1": neg_f1,
        "neutral_f1": neu_f1,
        "positive_f1": pos_f1
    })

    # Save confusion matrix plot
    cm = confusion_matrix(y_test, preds, labels=LABELS)
    fig, ax = plt.subplots(figsize=(6, 5))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=LABELS)
    disp.plot(ax=ax, cmap="Blues", values_format="d")
    ax.set_title(f"Confusion Matrix — {name}", fontsize=12, fontweight="bold")
    plt.tight_layout()
    safe_name = name.replace(" ", "_").replace("+", "plus").replace("(", "").replace(")", "").replace("-", "_")
    plt.savefig(FIG_DIR / f"cm_{safe_name}.png", dpi=180)
    plt.close()

# Comparison Table
comparison_df = pd.DataFrame(results).sort_values("macro_f1", ascending=False)
comparison_df.to_csv(REPORTS_DIR / "model_comparison.csv", index=False)
print("\n" + "="*60)
print("FINAL BENCHMARK COMPARISON (RANKED BY MACRO-F1):")
print(comparison_df[["model", "accuracy", "macro_f1", "negative_f1", "neutral_f1", "positive_f1"]].to_string(index=False, float_format="%.4f"))

# Select winner
winner_row = comparison_df.iloc[0]
winner_name = winner_row["model"]
winner_pipe = trained_pipelines[winner_name]
print(f"\nWINNER SELECTED: {winner_name} (Macro F1 = {winner_row['macro_f1']:.4f})")

# Save winning model artifact
joblib.dump(winner_pipe, MODELS_DIR / "best_sentiment_model.joblib")
(MODELS_DIR / "model_info.txt").write_text(f"Selected Model: {winner_name}\nMacro F1: {winner_row['macro_f1']:.4f}\nAccuracy: {winner_row['accuracy']:.4f}\n", encoding="utf-8")
print(f"Saved winning pipeline to {MODELS_DIR / 'best_sentiment_model.joblib'}")

# Comparison Bar Chart
fig, ax = plt.subplots(figsize=(10, 5.5))
metrics_to_plot = ["accuracy", "macro_f1", "negative_f1", "positive_f1"]
plot_df = comparison_df.set_index("model")[metrics_to_plot]
plot_df.columns = ["Accuracy", "Macro F1", "Negative F1", "Positive F1"]
plot_df.plot(kind="bar", ax=ax, colormap="viridis", edgecolor="black", linewidth=0.7)
ax.set_title("Model Comparison on Held-Out Test Set (1,315 Reviews)", fontsize=13, fontweight="bold", pad=12)
ax.set_ylabel("Score", fontsize=11)
ax.set_ylim(0, 1.05)
ax.set_xticklabels(ax.get_xticklabels(), rotation=15, ha="right")
ax.legend(loc="lower right", framealpha=0.9)
plt.tight_layout()
plt.savefig(FIG_DIR / "model_comparison_barchart.png", dpi=200)
plt.close()
print(f"Saved {FIG_DIR / 'model_comparison_barchart.png'}")
