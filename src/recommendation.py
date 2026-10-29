"""Context-Based Dining Recommendation Engine for Kolkata FoodLens.

Implements content-based ranking combining:
- Customer Experience / Sentiment Score: 50%
- Zomato Food Community Rating: 25%
- Verified Municipal Safety Score (where available): 15%
- Occasion & Suitability Tag Match: 10%

Integrity:
- Excludes gender/age stereotyping; strictly uses contextual dining tags.
- Missing safety records do not penalize or inflate scores dishonestly.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "kolkata_dataset"

import sys
sys.path.insert(0, str(ROOT / "src"))
from safety_engine import SafetyEngine

OCCASION_TAG_MAP = {
    "family": ["family_friendly", "kids_menu"],
    "students": ["student_budget"],
    "couples": ["date_night", "outdoor_seating"],
    "groups": ["group_friendly", "late_night"],
    "solo": ["solo_friendly"],
}

class RecommendationEngine:
    def __init__(self):
        self.restaurants = pd.read_csv(DATA_DIR / "restaurants.csv")
        self.reviews = pd.read_csv(DATA_DIR / "reviews_kolkata.csv")
        self.suitability = pd.read_csv(DATA_DIR / "restaurant_suitability.csv")
        self.safety_engine = SafetyEngine()

        # Precompute restaurant sentiment scores from reviews (0-100 scale)
        self.sentiment_scores = self._compute_sentiment_scores()

        # Build restaurant tags dictionary
        self.restaurant_tags = self.suitability.groupby("restaurant_id")["tag"].apply(set).to_dict()

    def _compute_sentiment_scores(self) -> Dict[str, float]:
        scores = {}
        grouped = self.reviews.groupby("restaurant_id")
        for rid, group in grouped:
            total = len(group)
            if total == 0:
                scores[rid] = 50.0
                continue
            pos = (group["sentiment_label"].str.lower() == "positive").sum()
            neu = (group["sentiment_label"].str.lower() == "neutral").sum()
            # Pos = 1.0, Neu = 0.5, Neg = 0.0
            score = ((pos + 0.5 * neu) / total) * 100.0
            scores[rid] = round(score, 1)
        return scores

    def recommend(
        self,
        max_budget: Optional[int] = None,
        occasion: str = "any",
        cuisine: Optional[str] = None,
        neighbourhood: Optional[str] = None,
        veg_only: bool = False,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """Filter and rank Kolkata restaurants based on multi-criteria criteria."""
        df = self.restaurants.copy()

        # 1. Filter: Budget
        if max_budget is not None and max_budget > 0:
            df = df[df["cost_for_two_inr"] <= max_budget]

        # 2. Filter: Veg only
        if veg_only:
            # Check veg_focused flag or veg_friendly tag
            veg_rids = set(df[df["veg_focused"] == True]["restaurant_id"])
            for rid, tags in self.restaurant_tags.items():
                if "veg_friendly" in tags:
                    veg_rids.add(rid)
            df = df[df["restaurant_id"].isin(veg_rids)]

        # 3. Filter: Cuisine (loose substring match)
        if cuisine and cuisine.lower() != "any":
            c_low = cuisine.lower().strip()
            df = df[
                df["primary_cuisine"].str.lower().str.contains(c_low, na=False) |
                df["cuisines"].str.lower().str.contains(c_low, na=False)
            ]

        # 4. Filter: Neighbourhood
        if neighbourhood and neighbourhood.lower() != "any":
            n_low = neighbourhood.lower().strip()
            # Handle common aliases
            if "salt lake" in n_low or "bidhannagar" in n_low:
                n_filter = "salt lake"
            elif "new town" in n_low or "newtown" in n_low:
                n_filter = "new town"
            else:
                n_filter = n_low
            df = df[df["neighbourhood"].str.lower().str.contains(n_filter, na=False)]

        if df.empty:
            return []

        # Target tags for occasion
        target_tags = OCCASION_TAG_MAP.get(occasion.lower(), [])

        ranked_results = []
        for _, row in df.iterrows():
            rid = row["restaurant_id"]

            # Component 1: Sentiment Score (0-100)
            sent_score = self.sentiment_scores.get(rid, 65.0)

            # Component 2: Zomato Rating (0-100)
            z_rating = float(row.get("zomato_rating", 3.5))
            zomato_score = max(0.0, min(100.0, ((z_rating - 1.0) / 4.0) * 100.0))

            # Component 3: Safety Score (0-100 or None)
            safety_info = self.safety_engine.calculate_score(rid)
            safety_val = safety_info["safety_score"]

            # Component 4: Occasion / Suitability Tag match (0-100)
            r_tags = self.restaurant_tags.get(rid, set())
            if target_tags:
                matched = len(r_tags.intersection(target_tags))
                tag_score = (matched / len(target_tags)) * 100.0
            else:
                tag_score = 100.0

            # Composite weighted rank
            if safety_val is not None:
                # 50% Sentiment + 25% Zomato + 15% Safety + 10% Tags
                composite = (
                    0.50 * sent_score +
                    0.25 * zomato_score +
                    0.15 * float(safety_val) +
                    0.10 * tag_score
                )
            else:
                # Redistribute 15% safety proportionally: 60% Sentiment + 30% Zomato + 10% Tags
                composite = (
                    0.60 * sent_score +
                    0.30 * zomato_score +
                    0.10 * tag_score
                )

            ranked_results.append({
                "restaurant_id": rid,
                "name": row["name"],
                "address": row["address"],
                "neighbourhood": row["neighbourhood"],
                "primary_cuisine": row["primary_cuisine"],
                "cost_for_two_inr": row["cost_for_two_inr"],
                "zomato_rating": row["zomato_rating"],
                "zomato_votes": row["zomato_votes"],
                "sentiment_score": sent_score,
                "safety_score": safety_val,
                "safety_display": safety_info["display_score"],
                "safety_confidence": safety_info["confidence_label"],
                "tags": sorted(list(r_tags)),
                "composite_rank_score": round(composite, 2),
            })

        ranked_results.sort(key=lambda x: x["composite_rank_score"], reverse=True)
        return ranked_results[:top_k]

if __name__ == "__main__":
    engine = RecommendationEngine()
    print("Testing Query 1: Students in Salt Lake under Rs 800:")
    q1 = engine.recommend(max_budget=800, occasion="students", neighbourhood="Bidhannagar", top_k=3)
    for r in q1:
        print(f"  - {r['name']} | Cost: Rs {r['cost_for_two_inr']} | Zomato: {r['zomato_rating']}★ | Sentiment: {r['sentiment_score']}% | Safety: {r['safety_display']} | Rank: {r['composite_rank_score']}")

    print("\nTesting Query 2: Family dinner in Park Street:")
    q2 = engine.recommend(occasion="family", neighbourhood="Park Street", top_k=3)
    for r in q2:
        print(f"  - {r['name']} | Cost: Rs {r['cost_for_two_inr']} | Zomato: {r['zomato_rating']}★ | Sentiment: {r['sentiment_score']}% | Safety: {r['safety_display']} | Rank: {r['composite_rank_score']}")
