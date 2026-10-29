"""Inference module for Kolkata FoodLens Sentiment Model.

Exposes predict_sentiment(text) -> {label, confidence, probabilities}
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import joblib

ROOT = Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(ROOT / "src"))
from preprocessing import clean_text

MODEL_PATH = Path(__file__).resolve().parent / "best_sentiment_model.joblib"
_model = None

def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Trained model not found at: {MODEL_PATH}")
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_sentiment(text: str) -> Dict[str, Any]:
    """Predict overall sentiment with calibrated confidence score.

    Args:
        text: Raw user review text string.

    Returns:
        Dictionary containing predicted label, confidence (0.0 to 1.0),
        and full class probability distribution.
    """
    model = get_model()
    cleaned = clean_text(text)
    if not cleaned:
        return {
            "label": "neutral",
            "confidence": 0.3333,
            "probabilities": {"negative": 0.3333, "neutral": 0.3333, "positive": 0.3334}
        }

    probs = model.predict_proba([cleaned])[0]
    classes = [c.lower() for c in model.classes_]
    prob_dict = {cls: float(prob) for cls, prob in zip(classes, probs)}

    predicted_label = model.predict([cleaned])[0].lower()
    confidence = prob_dict.get(predicted_label, float(max(probs)))

    return {
        "label": predicted_label,
        "confidence": round(confidence, 4),
        "probabilities": {k: round(v, 4) for k, v in prob_dict.items()}
    }

if __name__ == "__main__":
    samples = [
        "The mutton biryani was fragrant, aromatic, and cooked to perfection!",
        "The food was average, nothing special to write home about.",
        "Got severe food poisoning from the stale fish and raw chicken!"
    ]
    for s in samples:
        print(f"\nReview: {s}")
        print("Output:", predict_sentiment(s))
