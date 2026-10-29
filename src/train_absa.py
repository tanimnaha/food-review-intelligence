import sys
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from preprocessing import clean_text

DATA_DIR = ROOT / "data" / "kolkata_dataset"
MODELS_DIR = ROOT / "models" / "absa_model"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = ROOT / "reports"

# 1. Load Kolkata reviews (5,000 synthetic reviews with aspect labels)
df_kolkata = pd.read_csv(DATA_DIR / "reviews_kolkata.csv")
print(f"Loaded Kolkata reviews: {len(df_kolkata):,} rows")

df_kolkata["cleaned_text"] = df_kolkata["review_text"].apply(clean_text)

ASPECTS = ["food", "service", "hygiene", "ambience", "price"]
ASPECT_COL_MAP = {
    "food": "sentiment_food",
    "service": "sentiment_service",
    "hygiene": "sentiment_hygiene",
    "ambience": "sentiment_ambience",
    "price": "sentiment_price"
}

# 2. Fit shared TF-IDF representation
print("Fitting TF-IDF vectorizer across review corpus...")
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    min_df=2,
    max_features=25000,
    sublinear_tf=True
)
X_train_vec = vectorizer.fit_transform(df_kolkata["cleaned_text"])

# 3. Train specialized classifier for each of the 5 aspects
aspect_models = {}
for aspect in ASPECTS:
    col = ASPECT_COL_MAP[aspect]
    y_train = df_kolkata[col].str.lower()
    print(f"Training aspect model: {aspect.upper()} (Distribution: {y_train.value_counts().to_dict()})...")
    clf = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    clf.fit(X_train_vec, y_train)
    aspect_models[aspect] = clf

# Save models & vectorizer
joblib.dump(vectorizer, MODELS_DIR / "absa_vectorizer.joblib")
joblib.dump(aspect_models, MODELS_DIR / "absa_classifiers.joblib")
print(f"Saved ABSA models to {MODELS_DIR}")

# 4. Validate on aspect_based_sample_semeval.csv
print("\n" + "="*60)
print("VALIDATING ON REAL SEMEVAL RESTAURANT ASPECT DATA (86 samples)...")
semeval_df = pd.read_csv(DATA_DIR / "aspect_based_sample_semeval.csv")

# Parse SemEval samples
semeval_results = []
for idx, row in semeval_df.iterrows():
    text = clean_text(str(row["content"]))
    cats = [c.strip().lower() for c in str(row["category"]).split(",")]
    asps = [a.strip().lower() for a in str(row["aspect"]).split(",")]
    sents = [s.strip().lower() for s in str(row["sentiments"]).split(",")]

    item = {"text": text, "food": None, "service": None, "ambience": None, "price": None, "hygiene": None}
    for c, a, s in zip(cats, asps, sents):
        if "food" in c or "quality" in a:
            item["food"] = s
        if "service" in c:
            item["service"] = s
        if "ambience" in c or "atmosphere" in c or "decor" in c:
            item["ambience"] = s
        if "price" in c or "price" in a or "prices" in a:
            item["price"] = s
        if "clean" in c or "hygiene" in c or "sanit" in a:
            item["hygiene"] = s
    semeval_results.append(item)

eval_df = pd.DataFrame(semeval_results)

# Predict using trained aspect models
X_semeval = vectorizer.transform(eval_df["text"])
report_lines = []

for aspect in ["food", "service", "ambience", "price"]:
    sub = eval_df[eval_df[aspect].notna()].copy()
    if len(sub) > 0:
        true_labels = sub[aspect].tolist()
        pred_labels = aspect_models[aspect].predict(vectorizer.transform(sub["text"]))
        # normalize labels
        true_labels = [l if l in ["positive", "neutral", "negative"] else "neutral" for l in true_labels]
        macro_f1 = f1_score(true_labels, pred_labels, average="macro", zero_division=0)
        report_lines.append(f"{aspect.capitalize():12s} | Validated Samples: {len(sub):2d} | Macro F1: {macro_f1:.4f}")
        print(report_lines[-1])

# 5. Sanity Check Example
print("\n" + "="*60)
print("SANITY CHECK:")
test_example = "The biryani was excellent, but the tables were dirty and the service was terrible"
print(f"Input: \"{test_example}\"")
vec_test = vectorizer.transform([clean_text(test_example)])

preds = {aspect: aspect_models[aspect].predict(vec_test)[0] for aspect in ASPECTS}
print(f"Predicted Aspects: {preds}")
