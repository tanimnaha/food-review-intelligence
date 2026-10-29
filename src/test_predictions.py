
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "results" / "best_model.joblib"
OUTPUT_PATH = ROOT / "results" / "sample_predictions.csv"

reviews = [
    "The food was delicious and the service was excellent.",
    "The food was cold and the delivery was extremely late.",
    "The food was average and nothing was particularly special.",
]

def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    model = joblib.load(MODEL_PATH)
    predictions = model.predict(reviews)

    results = pd.DataFrame({
        "Review": reviews,
        "Predicted Sentiment": predictions,
    })

    print("\nSENTIMENT ANALYSIS DEMONSTRATION")
    print("=" * 55)

    for _, row in results.iterrows():
        print(f"\nReview: {row['Review']}")
        print(f"Prediction: {row['Predicted Sentiment']}")

    results.to_csv(OUTPUT_PATH, index=False)
    print(f"\nPredictions saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
