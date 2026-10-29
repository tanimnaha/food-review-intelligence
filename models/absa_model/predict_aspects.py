"""Aspect-Based Sentiment Analysis (ABSA) Inference Engine.

Exposes: predict_aspects(text) -> {food, service, hygiene, ambience, price}
Combines clause-level aspect segmentation with trained ML classifiers.
"""

from __future__ import annotations
import re
from pathlib import Path
from typing import Dict
import joblib

ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = ROOT / "models" / "absa_model"

_vectorizer = None
_classifiers = None

ASPECT_KEYWORDS = {
    "food": [
        "food", "biryani", "taste", "tasty", "flavor", "flavour", "dish", "dishes", "meal", "menu",
        "chicken", "mutton", "kebab", "kebabs", "roll", "rolls", "fish", "prawn", "dessert", "desserts",
        "sweet", "sweets", "curry", "noodles", "pizza", "burger", "rice", "dal", "paneer", "soup",
        "starter", "portion", "cook", "cooked", "spicy", "delicious", "yummy"
    ],
    "service": [
        "service", "waiter", "waiters", "waitress", "staff", "server", "servers", "manager",
        "hospitality", "attentive", "delivery", "rider", "wait", "waiting", "order", "ordered",
        "bill", "billing", "prompt", "quick", "delayed", "slow", "courteous", "polite", "rude"
    ],
    "hygiene": [
        "clean", "cleanliness", "dirty", "hygiene", "sanitized", "sanitary", "table", "tables",
        "washroom", "toilet", "toilets", "restroom", "hair", "cockroach", "roach", "pest", "rat",
        "utensil", "utensils", "cutlery", "glass", "glasses", "plate", "plates", "filthy", "stale",
        "unhygienic", "gloves", "bare hands", "mold", "smell", "rotten", "spoiled", "poisoning"
    ],
    "ambience": [
        "ambience", "ambiance", "atmosphere", "decor", "music", "seating", "lighting", "interior",
        "interiors", "vibe", "vibes", "view", "cramped", "noisy", "loud", "quiet", "cozy",
        "aesthetic", "environment", "setting"
    ],
    "price": [
        "price", "prices", "pricing", "expensive", "cheap", "cost", "costly", "bill", "value",
        "pocket", "worth", "budget", "overpriced", "affordable", "reasonable", "money"
    ]
}

POLARITY_LEXICON = {
    "positive": {
        "excellent", "delicious", "great", "good", "superb", "amazing", "tasty", "fresh", "best",
        "polite", "friendly", "clean", "spotless", "courteous", "wonderful", "fast", "quick",
        "affordable", "reasonable", "loved", "perfect", "generous", "heavenly", "piping", "tender",
        "juicy", "cozy", "chic", "helpful", "delightful", "impressed", "flavourful", "flavorful"
    },
    "negative": {
        "terrible", "horrible", "bad", "dirty", "filthy", "slow", "cold", "stale", "awful",
        "rude", "disgusting", "worst", "expensive", "overpriced", "poor", "unacceptable",
        "soggy", "tasteless", "bland", "unhygienic", "sick", "poisoning", "undercooked", "raw",
        "cramped", "noisy", "greasy", "spoiled", "rotten", "smelly", "waste", "stinky", "rancid"
    }
}

def _load_artifacts():
    global _vectorizer, _classifiers
    if _vectorizer is None:
        _vectorizer = joblib.load(MODELS_DIR / "absa_vectorizer.joblib")
    if _classifiers is None:
        _classifiers = joblib.load(MODELS_DIR / "absa_classifiers.joblib")

def predict_aspects(text: str) -> Dict[str, str]:
    """Predict aspect-level sentiments for food, service, hygiene, ambience, price.

    Args:
        text: Raw review text string.

    Returns:
        Dictionary mapping each aspect to 'positive', 'neutral', or 'negative'.
    """
    _load_artifacts()
    lowered = text.lower()

    # Split into clauses based on discourse markers and punctuation
    raw_clauses = re.split(r"[,;.]|\bbut\b|\bhowever\b|\balthough\b|\bwhile\b|\band\b", lowered)
    clauses = [c.strip() for c in raw_clauses if len(c.strip()) > 3]

    results = {}
    vec_full = _vectorizer.transform([lowered])

    for aspect in ["food", "service", "hygiene", "ambience", "price"]:
        keywords = ASPECT_KEYWORDS[aspect]

        # Find clauses specifically mentioning this aspect
        matching_clauses = [c for c in clauses if any(re.search(r"\b" + re.escape(w) + r"\b", c) for w in keywords)]

        if matching_clauses:
            clause_text = " ".join(matching_clauses)
            tokens = set(re.findall(r"\b\w+\b", clause_text))

            pos_hits = len(tokens.intersection(POLARITY_LEXICON["positive"]))
            neg_hits = len(tokens.intersection(POLARITY_LEXICON["negative"]))

            if pos_hits > neg_hits:
                results[aspect] = "positive"
            elif neg_hits > pos_hits:
                results[aspect] = "negative"
            else:
                # Use model probability on the clause or full text
                clf = _classifiers[aspect]
                pred = clf.predict(_vectorizer.transform([clause_text]))[0]
                results[aspect] = pred.lower()
        else:
            # If aspect is not explicitly isolated, use global classifier fallback
            # but default to neutral if no aspect keywords appear in entire text
            has_any_kw = any(re.search(r"\b" + re.escape(w) + r"\b", lowered) for w in keywords)
            if has_any_kw:
                pred = _classifiers[aspect].predict(vec_full)[0]
                results[aspect] = pred.lower()
            else:
                results[aspect] = "neutral"

    return results

if __name__ == "__main__":
    example = "The biryani was excellent, but the tables were dirty and the service was terrible"
    print(f"Review: \"{example}\"")
    print("Aspect Output:", predict_aspects(example))
