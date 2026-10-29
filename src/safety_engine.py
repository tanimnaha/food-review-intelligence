"""Food Safety Scoring Engine for Kolkata FoodLens.

Recomputes an objective 0–100 food safety compliance score from municipal
inspection records using weighted criteria:
- Inspection Outcomes: 40%
- Compliance & Licence Status: 30%
- Violation Severity: 20%
- Recency of Evidence: 10%

Integrity Rule:
When a restaurant has no records, outputs None and status 'Safety data unavailable'.
Never fabricates a score when evidence is missing.
"""

from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "kolkata_dataset" / "safety_records.csv"

# Severity penalty weights per violation type
VIOLATION_PENALTIES = {
    "pest_control_lapse": 8,
    "cooking_oil_reuse": 8,
    "cold_storage_temperature": 6,
    "drinking_water_quality": 5,
    "utensil_hygiene": 4,
    "waste_disposal": 4,
    "staff_hygiene_training": 3,
    "labelling_and_storage": 2,
}

class SafetyEngine:
    def __init__(self, records_path: Optional[Path] = None):
        self.records_path = records_path or DATA_PATH
        if self.records_path.exists():
            self.df = pd.read_csv(self.records_path)
            self.df["inspection_date"] = pd.to_datetime(self.df["inspection_date"], errors="coerce")
        else:
            self.df = pd.DataFrame()

    def get_restaurant_records(self, restaurant_id: str) -> pd.DataFrame:
        if self.df.empty or "restaurant_id" not in self.df.columns:
            return pd.DataFrame()
        return self.df[self.df["restaurant_id"] == restaurant_id].sort_values("inspection_date", ascending=False)

    def calculate_score(self, restaurant_id: str, reference_date: Optional[datetime] = None) -> Dict[str, Any]:
        records = self.get_restaurant_records(restaurant_id)
        if records.empty:
            return {
                "restaurant_id": restaurant_id,
                "safety_score": None,
                "display_score": "Safety data unavailable",
                "confidence": "safety_data_unavailable",
                "confidence_label": "No inspection record on file",
                "fssai_licence_no": None,
                "last_inspected": None,
                "violations": [],
                "outcome": None,
                "breakdown": None
            }

        ref_date = reference_date or datetime(2026, 10, 29)
        latest = records.iloc[0]

        # 1. Inspection Outcome (Max 40 points)
        outcome = str(latest.get("outcome", "")).strip().lower()
        if "satisfactory" in outcome:
            outcome_score = 40.0
        elif "needs improvement" in outcome:
            outcome_score = 20.0
        elif "major violation" in outcome:
            outcome_score = 5.0
        else:
            outcome_score = 20.0

        # 2. Licence Status (Max 30 points)
        licence = str(latest.get("licence_status", "")).strip().lower()
        if "active" in licence:
            licence_score = 30.0
        elif "renewal due" in licence:
            licence_score = 15.0
        else:
            licence_score = 0.0

        # 3. Violation Severity (Max 20 points)
        raw_violations = str(latest.get("violations_noted", "")).strip()
        violation_list = []
        if raw_violations and raw_violations.lower() != "none" and raw_violations.lower() != "nan":
            violation_list = [v.strip() for v in raw_violations.split(";") if v.strip()]

        penalty = sum(VIOLATION_PENALTIES.get(v, 4) for v in violation_list)
        violation_score = max(0.0, 20.0 - penalty)

        # 4. Recency Score (Max 10 points)
        insp_date = latest["inspection_date"]
        if pd.notna(insp_date):
            days_ago = (ref_date - insp_date).days
            if days_ago <= 180:
                recency_score = 10.0
            elif days_ago <= 365:
                recency_score = 7.0
            elif days_ago <= 730:
                recency_score = 4.0
            else:
                recency_score = 2.0
            formatted_date = insp_date.strftime("%d %b %Y")
        else:
            recency_score = 5.0
            formatted_date = "Unknown"

        total_score = int(round(outcome_score + licence_score + violation_score + recency_score))
        total_score = max(0, min(100, total_score))

        return {
            "restaurant_id": restaurant_id,
            "safety_score": total_score,
            "display_score": f"{total_score} / 100",
            "confidence": "verified_inspection_records",
            "confidence_label": f"Verified ({len(records)} audit{'s' if len(records)>1 else ''})",
            "fssai_licence_no": latest.get("fssai_licence_no"),
            "last_inspected": formatted_date,
            "outcome": latest.get("outcome"),
            "violations": violation_list,
            "reinspection_required": bool(latest.get("reinspection_required", False)),
            "breakdown": {
                "outcome_score": outcome_score,
                "licence_score": licence_score,
                "violation_score": violation_score,
                "recency_score": recency_score
            }
        }

if __name__ == "__main__":
    engine = SafetyEngine()
    # Test on known restaurant with records and without records
    test_ids = ["KOL0001", "KOL0002", "KOL0015", "KOL0099", "KOL9999"]
    for rid in test_ids:
        res = engine.calculate_score(rid)
        print(f"\n[{rid}] Score: {res['display_score']} | Confidence: {res['confidence_label']} | Violations: {res['violations']}")
