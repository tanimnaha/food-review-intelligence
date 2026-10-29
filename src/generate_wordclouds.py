
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# Project paths
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "yelp_sentiment_master_dataset.csv"
OUTPUT_DIR = ROOT / "results" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LABELS = {
    "Positive": "Greens",
    "Negative": "Reds",
    "Neutral": "viridis",
}

def main():
    print("Loading review dataset...")

    df = pd.read_csv(DATA_PATH)

    # Clean the text and sentiment labels.
    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df["rating_review"] = (
        df["rating_review"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.title()
    )

    df = df[
        df["text"].ne("")
        & df["rating_review"].isin(LABELS)
    ].copy()

    # Remove repeated review texts, matching the training workflow.
    df = df.drop_duplicates(subset=["text"])

    stopwords = set(ENGLISH_STOP_WORDS)

    for sentiment, colormap in LABELS.items():
        reviews = df.loc[
            df["rating_review"] == sentiment, "text"
        ]

        if reviews.empty:
            print(f"No reviews found for {sentiment}. Skipping.")
            continue

        combined_text = " ".join(reviews.tolist())

        cloud = WordCloud(
            width=1600,
            height=1000,
            background_color="white",
            colormap=colormap,
            stopwords=stopwords,
            max_words=120,
            collocations=False,
            min_font_size=8,
            random_state=42,
        ).generate(combined_text)

        fig, ax = plt.subplots(figsize=(12, 7))
        ax.imshow(cloud, interpolation="bilinear")
        ax.axis("off")

        ax.set_title(
            f"Word Cloud of {sentiment} Food Reviews\n"
            f"{len(reviews):,} reviews",
            fontsize=17,
            fontweight="bold",
            pad=16,
        )

        filename = f"wordcloud_{sentiment.lower()}.png"
        output_path = OUTPUT_DIR / filename

        plt.tight_layout()
        plt.savefig(
            output_path,
            dpi=220,
            bbox_inches="tight",
            facecolor="white",
        )
        plt.close(fig)

        print(f"Saved: {output_path}")

    print("\nAll available word clouds have been generated.")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
