import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from preprocessing import clean_text, split_data

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.sans-serif": "Arial", "font.family": "sans-serif"})

DATA_DIR = ROOT / "data" / "kolkata_dataset"
FIG_DIR = ROOT / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load data
restaurants = pd.read_csv(DATA_DIR / "restaurants.csv")
reviews_kolkata = pd.read_csv(DATA_DIR / "reviews_kolkata.csv")
reviews_train_real = pd.read_csv(DATA_DIR / "reviews_training_corpus_real.csv")
safety = pd.read_csv(DATA_DIR / "safety_records.csv")
suitability = pd.read_csv(DATA_DIR / "restaurant_suitability.csv")
aspect_semeval = pd.read_csv(DATA_DIR / "aspect_based_sample_semeval.csv")

print("All datasets loaded successfully.")

PALETTE = {"positive": "#2a9d8f", "neutral": "#e9c46a", "negative": "#e76f51"}

# Figure 1: Sentiment Class Imbalance Comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
train_dist = reviews_train_real["sentiment_label"].value_counts(normalize=True).reindex(["positive", "neutral", "negative"])
kolkata_dist = reviews_kolkata["sentiment_label"].value_counts(normalize=True).reindex(["positive", "neutral", "negative"])

train_counts = reviews_train_real["sentiment_label"].value_counts()
kolkata_counts = reviews_kolkata["sentiment_label"].value_counts()

axes[0].bar(train_dist.index, train_dist.values, color=[PALETTE[c] for c in train_dist.index], edgecolor="black", linewidth=0.8)
axes[0].set_title("Training Corpus Real (13,144 reviews)", fontsize=13, fontweight="bold")
axes[0].set_ylabel("Proportion", fontsize=11)
axes[0].set_ylim(0, 0.75)
for i, v in enumerate(train_dist.values):
    label = train_dist.index[i]
    cnt = train_counts[label]
    axes[0].text(i, v + 0.015, f"{v:.1%}\n({cnt:,})", ha="center", fontsize=10, fontweight="bold")

axes[1].bar(kolkata_dist.index, kolkata_dist.values, color=[PALETTE[c] for c in kolkata_dist.index], edgecolor="black", linewidth=0.8)
axes[1].set_title("Kolkata Reviews Synthetic (5,000 reviews)", fontsize=13, fontweight="bold")
axes[1].set_ylabel("Proportion", fontsize=11)
axes[1].set_ylim(0, 0.75)
for i, v in enumerate(kolkata_dist.values):
    label = kolkata_dist.index[i]
    cnt = kolkata_counts[label]
    axes[1].text(i, v + 0.015, f"{v:.1%}\n({cnt:,})", ha="center", fontsize=10, fontweight="bold")

plt.suptitle("Figure 1: Class Imbalance Across Datasets (Severe Negative Class Scarcity)", fontsize=15, fontweight="bold", y=1.03)
plt.tight_layout()
plt.savefig(FIG_DIR / "eda_fig1_sentiment_imbalance.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved eda_fig1_sentiment_imbalance.png")

# Figure 2: Rating Distributions
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.countplot(data=reviews_train_real, x="rating", ax=axes[0], palette="crest", edgecolor="black", linewidth=0.8)
axes[0].set_title("Training Corpus Real Ratings (1-5 stars)", fontsize=13, fontweight="bold")
axes[0].set_xlabel("Star Rating")
axes[0].set_ylabel("Count")

sns.countplot(data=reviews_kolkata, x="rating", ax=axes[1], palette="crest", edgecolor="black", linewidth=0.8)
axes[1].set_title("Kolkata Reviews Ratings (1-5 stars)", fontsize=13, fontweight="bold")
axes[1].set_xlabel("Star Rating")
axes[1].set_ylabel("Count")

plt.suptitle("Figure 2: Star Rating Distributions", fontsize=15, fontweight="bold", y=1.03)
plt.tight_layout()
plt.savefig(FIG_DIR / "eda_fig2_rating_distributions.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved eda_fig2_rating_distributions.png")

# Figure 3: Sentiment by Cuisine in Kolkata Reviews
merged_reviews = reviews_kolkata.merge(restaurants[["restaurant_id", "primary_cuisine", "neighbourhood"]], on="restaurant_id", how="left")
top_cuisines = merged_reviews["primary_cuisine"].value_counts().head(8).index
cuisine_df = merged_reviews[merged_reviews["primary_cuisine"].isin(top_cuisines)]

cuisine_sent = pd.crosstab(cuisine_df["primary_cuisine"], cuisine_df["sentiment_label"], normalize="index")[["positive", "neutral", "negative"]]

fig, ax = plt.subplots(figsize=(12, 6))
cuisine_sent.plot(kind="barh", stacked=True, color=[PALETTE["positive"], PALETTE["neutral"], PALETTE["negative"]], ax=ax, edgecolor="black", linewidth=0.7)
ax.set_title("Figure 3: Sentiment Breakdown Across Top Kolkata Cuisines", fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Proportion of Reviews", fontsize=11)
ax.set_ylabel("Primary Cuisine", fontsize=11)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
ax.legend(title="Sentiment", loc="lower right", framealpha=0.9)
plt.tight_layout()
plt.savefig(FIG_DIR / "eda_fig3_sentiment_by_cuisine.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved eda_fig3_sentiment_by_cuisine.png")

# Figure 4: Sentiment by Neighbourhood in Kolkata Reviews
top_neighbourhoods = merged_reviews["neighbourhood"].value_counts().head(8).index
neigh_df = merged_reviews[merged_reviews["neighbourhood"].isin(top_neighbourhoods)]
neigh_sent = pd.crosstab(neigh_df["neighbourhood"], neigh_df["sentiment_label"], normalize="index")[["positive", "neutral", "negative"]]

fig, ax = plt.subplots(figsize=(12, 6))
neigh_sent.plot(kind="barh", stacked=True, color=[PALETTE["positive"], PALETTE["neutral"], PALETTE["negative"]], ax=ax, edgecolor="black", linewidth=0.7)
ax.set_title("Figure 4: Sentiment Breakdown by Kolkata Neighbourhoods", fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Proportion of Reviews", fontsize=11)
ax.set_ylabel("Neighbourhood", fontsize=11)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
ax.legend(title="Sentiment", loc="lower right", framealpha=0.9)
plt.tight_layout()
plt.savefig(FIG_DIR / "eda_fig4_sentiment_by_neighbourhood.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved eda_fig4_sentiment_by_neighbourhood.png")

# Figure 5: Aspect-Based Sentiment Distributions (5 Aspects)
aspect_cols = ["sentiment_food", "sentiment_service", "sentiment_hygiene", "sentiment_ambience", "sentiment_price"]
aspect_labels = ["Food", "Service", "Hygiene", "Ambience", "Price"]
aspect_data = {}
for col, name in zip(aspect_cols, aspect_labels):
    aspect_data[name] = reviews_kolkata[col].value_counts(normalize=True).reindex(["positive", "neutral", "negative"]).values

aspect_df = pd.DataFrame(aspect_data, index=["positive", "neutral", "negative"]).T

fig, ax = plt.subplots(figsize=(11, 5.5))
aspect_df.plot(kind="bar", stacked=True, color=[PALETTE["positive"], PALETTE["neutral"], PALETTE["negative"]], ax=ax, edgecolor="black", linewidth=0.7)
ax.set_title("Figure 5: Aspect-Based Sentiment Distribution (Kolkata 5,000 Reviews)", fontsize=14, fontweight="bold", pad=15)
ax.set_ylabel("Proportion", fontsize=11)
ax.set_xlabel("Aspect Category", fontsize=11)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
ax.legend(title="Aspect Sentiment", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(FIG_DIR / "eda_fig5_aspect_sentiment_distributions.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved eda_fig5_aspect_sentiment_distributions.png")

# Figure 6: Safety Score vs Zomato Rating with Confidence Segregation
fig, ax = plt.subplots(figsize=(10, 6))
has_safety = restaurants.dropna(subset=["safety_score_0_100"])
no_safety = restaurants[restaurants["safety_score_0_100"].isna()]

scatter = ax.scatter(has_safety["zomato_rating"], has_safety["safety_score_0_100"], c=has_safety["cost_for_two_inr"], cmap="viridis", s=has_safety["zomato_votes"]/15, alpha=0.8, edgecolors="black", label="Estimated Safety Score")
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label("Cost for Two (INR)", fontsize=10)

ax.scatter(no_safety["zomato_rating"], [0]*len(no_safety), color="crimson", marker="x", s=90, label=f"Safety Data Unavailable ({len(no_safety)} restaurants)")
ax.axhline(0, color="crimson", linestyle="--", alpha=0.3)

ax.set_title("Figure 6: Zomato Rating vs. FSSAI/Safety Score (Bubble size = Zomato Votes)", fontsize=13, fontweight="bold", pad=12)
ax.set_xlabel("Zomato Rating (1.0 - 5.0)", fontsize=11)
ax.set_ylabel("Food Safety Score (0 - 100)", fontsize=11)
ax.set_ylim(-5, 105)
ax.legend(loc="upper left")
plt.tight_layout()
plt.savefig(FIG_DIR / "eda_fig6_safety_score_vs_zomato_rating.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved eda_fig6_safety_score_vs_zomato_rating.png")

# Preprocessing & Data Splitting for reviews_training_corpus_real.csv
print("\nCleaning training corpus text...")
reviews_train_real["cleaned_text"] = reviews_train_real["review_text"].apply(clean_text)

print("Performing stratified 80/10/10 split on real training corpus...")
train_df, val_df, test_df = split_data(reviews_train_real, target_col="sentiment_label", random_state=42)

DATA_SPLIT_DIR = ROOT / "data" / "splits"
DATA_SPLIT_DIR.mkdir(parents=True, exist_ok=True)

train_df.to_csv(DATA_SPLIT_DIR / "train.csv", index=False)
val_df.to_csv(DATA_SPLIT_DIR / "val.csv", index=False)
test_df.to_csv(DATA_SPLIT_DIR / "test.csv", index=False)

print(f"Stratified splits saved:\n- Train: {len(train_df):,} rows ({len(train_df)/len(reviews_train_real):.1%})\n- Val:   {len(val_df):,} rows ({len(val_df)/len(reviews_train_real):.1%})\n- Test:  {len(test_df):,} rows ({len(test_df)/len(reviews_train_real):.1%})")
