"""Implicit Opinion Disentanglement Engine for Food Reviews.

Disentangles explicit opinion expressions from implicit opinions across 5 key archetypes:
1. Idiomatic & Metaphorical expressions ("burned a hole in my pocket", "melted like butter")
2. Factual Temporal Delays ("waited 45 minutes for water", "took forever to get bill")
3. Biological & Physical Consequences ("spent the night throwing up", "cockroach in salad")
4. Portion & Quantity Disparities ("only one tiny piece of potato in ₹400 biryani")
5. Ambience & Environmental Disruptions ("blaring music impossible to hear", "AC barely cooling")
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Tuple

EXPLICIT_SENTIMENT_ADJECTIVES = {
    # Positive
    "good", "great", "delicious", "tasty", "flavourful", "flavorful", "yummy", "excellent",
    "amazing", "wonderful", "superb", "fresh", "tender", "crispy", "juicy", "polite",
    "courteous", "attentive", "friendly", "clean", "spotless", "neat", "sanitized",
    "cozy", "beautiful", "lovely", "cheap", "inexpensive", "affordable", "reasonable",
    # Negative
    "bad", "terrible", "horrible", "awful", "disgusting", "bland", "stale", "salty",
    "oily", "overcooked", "undercooked", "dry", "rubbery", "rude", "arrogant",
    "slow", "dirty", "filthy", "greasy", "expensive", "costly", "pricey", "overpriced",
    "noisy", "loud", "cramped", "uncomfortable"
}

# Regex patterns for archetypes
IDIOMATIC_PATTERNS: List[Tuple[re.Pattern, str, str, str]] = [
    # (pattern, category, sentiment, archetype_label)
    (re.compile(r"burn(?:ed|t)?\s+(?:a\s+)?(?:massive\s+|huge\s+)?hole\s+in\s+(?:my|our)\s+pocket", re.I), "RESTAURANT#PRICES", "negative", "idiomatic_financial_loss"),
    (re.compile(r"cost\s+(?:an?\s+)?arm\s+and\s+(?:a\s+)?leg", re.I), "RESTAURANT#PRICES", "negative", "idiomatic_financial_loss"),
    (re.compile(r"rip\s*off", re.I), "RESTAURANT#PRICES", "negative", "idiomatic_financial_loss"),
    (re.compile(r"melt(?:ed)?\s+like\s+butter", re.I), "FOOD#QUALITY", "positive", "metaphor_texture_tenderness"),
    (re.compile(r"(?:chew(?:ing)?\s+on\s+)?(?:dry\s+)?cardboard", re.I), "FOOD#QUALITY", "negative", "metaphor_dryness"),
    (re.compile(r"(?:pure\s+|like\s+)leather", re.I), "FOOD#QUALITY", "negative", "metaphor_toughness"),
    (re.compile(r"heavenly\s+cloud", re.I), "FOOD#QUALITY", "positive", "metaphor_delight"),
    (re.compile(r"a\s+biohazard", re.I), "HYGIENE#CLEANLINESS", "negative", "metaphor_extreme_filth"),
]

DELAY_PATTERNS: List[Tuple[re.Pattern, str, str, str]] = [
    (re.compile(r"(?:waited|ignored(?:\s+our\s+table)?)\s+(?:for\s+)?(?:\w+\s+)?(?:[0-9]+|twenty|thirty|forty|fifty|forty-five)\s+minutes?", re.I), "SERVICE#PROMPTNESS", "negative", "factual_waiting_delay"),
    (re.compile(r"waited\s+(?:almost\s+|over\s+)?(?:an?\s+hour|two\s+hours)", re.I), "SERVICE#PROMPTNESS", "negative", "factual_waiting_delay"),
    (re.compile(r"took\s+forever\s+to", re.I), "SERVICE#PROMPTNESS", "negative", "factual_waiting_delay"),
    (re.compile(r"(?:ask(?:ed)?|flag(?:ged)?)\s+(?:three|several|different|twice|servers)", re.I), "SERVICE#PROMPTNESS", "negative", "factual_waiting_delay"),
    (re.compile(r"finished\s+(?:two|several)\s+(?:full\s+)?podcasts?", re.I), "SERVICE#PROMPTNESS", "negative", "factual_waiting_delay"),
    (re.compile(r"landed\s+on\s+(?:the\s+)?table\s+(?:within|barely)\s+[0-9]+\s+minutes?", re.I), "SERVICE#PROMPTNESS", "positive", "factual_promptness"),
]

BIO_SAFETY_PATTERNS: List[Tuple[re.Pattern, str, str, str]] = [
    (re.compile(r"(?:throwing|threw)\s+up|vomit(?:ed|ing)?", re.I), "HYGIENE#FOOD_SAFETY", "negative", "biological_illness_consequence"),
    (re.compile(r"(?:hugging|hugged)\s+(?:the\s+)?toilet\s+bowl", re.I), "HYGIENE#FOOD_SAFETY", "negative", "biological_illness_consequence"),
    (re.compile(r"food\s+poisoning|stomach\s+infection|stomach\s+bug", re.I), "HYGIENE#FOOD_SAFETY", "negative", "biological_illness_consequence"),
    (re.compile(r"ended\s+up\s+in\s+(?:the\s+)?(?:hospital|emergency\s+ward)", re.I), "HYGIENE#FOOD_SAFETY", "negative", "biological_illness_consequence"),
    (re.compile(r"cockroach|dead\s+fly|insect\s+crawling|hair\s+in\s+(?:my|the)", re.I), "HYGIENE#FOOD_SAFETY", "negative", "foreign_body_contamination"),
    (re.compile(r"chemical\s+smell|smell(?:ed)?\s+like\s+(?:diesel|kerosene|petrol)", re.I), "HYGIENE#FOOD_SAFETY", "negative", "chemical_adulteration_smell"),
]

PORTION_PATTERNS: List[Tuple[re.Pattern, str, str, str]] = [
    (re.compile(r"only\s+one\s+(?:tiny\s+)?(?:piece|potato|prawn)", re.I), "FOOD#PRICES", "negative", "portion_disparity"),
    (re.compile(r"barely\s+covered\s+(?:the\s+bottom)", re.I), "FOOD#PRICES", "negative", "portion_disparity"),
    (re.compile(r"(?:barely|hardly)\s+fed\s+(?:a\s+)?pigeon", re.I), "FOOD#PRICES", "negative", "portion_disparity"),
    (re.compile(r"(?:easily\s+)?fed\s+(?:three|four|multiple)\s+(?:hungry\s+)?(?:adults|people)", re.I), "FOOD#PRICES", "positive", "portion_generosity"),
    (re.compile(r"(?:pocket|budget)\s*friendly", re.I), "RESTAURANT#PRICES", "positive", "affordability_descriptor"),
]

AMBIENCE_PATTERNS: List[Tuple[re.Pattern, str, str, str]] = [
    (re.compile(r"blaring\s+(?:club\s+)?music|impossible\s+to\s+hear", re.I), "AMBIENCE#GENERAL", "negative", "auditory_disruption"),
    (re.compile(r"(?:ac|air\s+conditioning)\s+was\s+barely\s+(?:working|functioning|cooling)", re.I), "AMBIENCE#GENERAL", "negative", "thermal_discomfort"),
    (re.compile(r"practically\s+sitting\s+in\s+(?:your\s+)?neighbor", re.I), "AMBIENCE#GENERAL", "negative", "spatial_crowding"),
]


class ImplicitOpinionDisentangler:
    def __init__(self):
        pass

    def classify_opinion(
        self,
        sentence_text: str,
        aspect_text: str = "",
        opinion_span: str = ""
    ) -> Dict[str, Any]:
        """Classifies an opinion expression into explicit or implicit with archetype attribution."""
        target_text = f"{opinion_span} {sentence_text}".strip().lower()

        # Check explicit tokens
        words = set(re.findall(r"\b\w+\b", opinion_span.lower() if opinion_span else sentence_text.lower()))
        has_explicit_adj = bool(words & EXPLICIT_SENTIMENT_ADJECTIVES)

        # 1. Check Idiomatic Patterns
        for pattern, cat, sentiment, archetype in IDIOMATIC_PATTERNS:
            if pattern.search(target_text):
                return {
                    "opinion_type": "implicit",
                    "archetype": archetype,
                    "implied_category": cat,
                    "implied_sentiment": sentiment,
                    "is_metaphor": True,
                    "confidence": 0.94,
                    "explanation": f"Detected idiomatic/metaphorical opinion expression: '{pattern.pattern}' signifying {sentiment} {cat}."
                }

        # 2. Check Factual Delay Patterns
        for pattern, cat, sentiment, archetype in DELAY_PATTERNS:
            if pattern.search(target_text):
                return {
                    "opinion_type": "implicit",
                    "archetype": archetype,
                    "implied_category": cat,
                    "implied_sentiment": sentiment,
                    "is_metaphor": False,
                    "confidence": 0.92,
                    "explanation": f"Detected factual temporal metric without sentiment adjectives: '{pattern.pattern}' indicating {sentiment} {cat}."
                }

        # 3. Check Biological Safety & Contamination
        for pattern, cat, sentiment, archetype in BIO_SAFETY_PATTERNS:
            if pattern.search(target_text):
                return {
                    "opinion_type": "implicit",
                    "archetype": archetype,
                    "implied_category": cat,
                    "implied_sentiment": sentiment,
                    "is_metaphor": False,
                    "confidence": 0.96,
                    "explanation": f"Detected objective public health/illness symptom: '{pattern.pattern}' signaling critical {cat} failure."
                }

        # 4. Check Portion & Quantity Disparity
        for pattern, cat, sentiment, archetype in PORTION_PATTERNS:
            if pattern.search(target_text):
                return {
                    "opinion_type": "implicit",
                    "archetype": archetype,
                    "implied_category": cat,
                    "implied_sentiment": sentiment,
                    "is_metaphor": False,
                    "confidence": 0.90,
                    "explanation": f"Detected numerical portion vs cost disparity: '{pattern.pattern}' evaluating {cat}."
                }

        # 5. Check Ambience Disruption
        for pattern, cat, sentiment, archetype in AMBIENCE_PATTERNS:
            if pattern.search(target_text):
                return {
                    "opinion_type": "implicit",
                    "archetype": archetype,
                    "implied_category": cat,
                    "implied_sentiment": sentiment,
                    "is_metaphor": False,
                    "confidence": 0.89,
                    "explanation": f"Detected factual environmental/sensory disruption: '{pattern.pattern}' indicating negative {cat}."
                }

        # Default fallback: Explicit if sentiment adjective present, else neutral descriptor
        if has_explicit_adj:
            matched_adjs = list(words & EXPLICIT_SENTIMENT_ADJECTIVES)
            return {
                "opinion_type": "explicit",
                "archetype": "explicit_adjectival_modifier",
                "implied_category": "FOOD#QUALITY" if "food" in aspect_text.lower() else "SERVICE#GENERAL",
                "implied_sentiment": "positive" if any(a in matched_adjs for a in ["good", "great", "delicious", "tasty", "fresh"]) else "negative",
                "is_metaphor": False,
                "confidence": 0.85,
                "explanation": f"Contains explicit sentiment adjective(s): {matched_adjs}."
            }
        else:
            return {
                "opinion_type": "explicit",
                "archetype": "standard_factual_statement",
                "implied_category": "FOOD#QUALITY",
                "implied_sentiment": "neutral",
                "is_metaphor": False,
                "confidence": 0.70,
                "explanation": "Standard descriptive statement without strong polarity markers."
            }

    def disentangle_review(self, review_text: str) -> List[Dict[str, Any]]:
        """Processes a full review and breaks down all opinions into explicit vs implicit."""
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(review_text)
        results = []
        for sent in doc.sents:
            res = self.classify_opinion(sent.text)
            results.append({
                "sentence": sent.text,
                "opinion_type": res["opinion_type"],
                "archetype": res["archetype"],
                "implied_category": res["implied_category"],
                "implied_sentiment": res["implied_sentiment"],
                "explanation": res["explanation"]
            })
        return results
