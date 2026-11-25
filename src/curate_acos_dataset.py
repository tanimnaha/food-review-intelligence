"""Dataset curation and benchmark generation for Aspect-Category-Opinion-Sentiment (ACOS)
Quadruple Mining and Implicit Opinion Disentanglement in Online Food Reviews.

Generates structured JSONL splits where EVERY aspect and opinion is a verbatim span
extracted from the review text:
- data/acos_dataset/train.jsonl
- data/acos_dataset/val.jsonl
- data/acos_dataset/test.jsonl
- data/acos_dataset/benchmark_metadata.json
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import numpy as np
import spacy

nlp = spacy.load("en_core_web_sm")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "acos_dataset"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = [
    "FOOD#QUALITY",
    "FOOD#PRICES",
    "FOOD#STYLE_OPTIONS",
    "SERVICE#GENERAL",
    "SERVICE#PROMPTNESS",
    "AMBIENCE#GENERAL",
    "RESTAURANT#PRICES",
    "HYGIENE#CLEANLINESS",
    "HYGIENE#FOOD_SAFETY"
]

POLARITIES = ["positive", "neutral", "negative"]

# Domain entities & culinary lexicons for Kolkata & Indian dining
DISHES = [
    "mutton biryani", "chicken chaap", "reshmi kebab", "galouti kebab", "fish fry",
    "kosha mangsho", "paneer tikka", "butter naan", "tandoori roti", "mishti doi",
    "prawn malai curry", "roshogolla", "gulab jamun", "hakka noodles", "chilli chicken",
    "dal makhani", "chicken bharta", "mutton rezala", "phuchka", "darjeeling tea",
    "seafood platter", "chicken broth", "masala dosa", "tandoori chicken", "egg roll"
]

SERVICE_ASPECTS = ["waiter", "floor captain", "server", "waitstaff", "service", "hostess", "manager", "staff"]
AMBIENCE_ASPECTS = ["decor", "music", "lighting", "seating", "air conditioning", "ambience", "tables", "vibe"]
HYGIENE_ASPECTS = ["washroom", "cutlery", "dining plates", "water glasses", "table cloth", "kitchen counter", "restroom"]
PRICE_ASPECTS = ["bill", "pricing", "service charge", "rates", "cost", "portion size"]

# Explicit & Implicit Templates where aspect & opinion are verbatim spans
EXPLICIT_TEMPLATES = [
    # Food Quality Positive
    ("The {dish} was fragrant, tender and cooked to perfection.",
     lambda d: [("dish", d, "FOOD#QUALITY", "fragrant, tender and cooked to perfection", "positive", "explicit")]),
    ("We loved the {dish}; it was absolutely delicious and flavorful.",
     lambda d: [("dish", d, "FOOD#QUALITY", "absolutely delicious and flavorful", "positive", "explicit")]),
    ("The {dish} was incredibly juicy and fresh.",
     lambda d: [("dish", d, "FOOD#QUALITY", "incredibly juicy and fresh", "positive", "explicit")]),
    ("Their {dish} had an authentic smoky tandoori aroma.",
     lambda d: [("dish", d, "FOOD#QUALITY", "authentic smoky tandoori aroma", "positive", "explicit")]),

    # Food Quality Negative
    ("The {dish} was oily, bland and smelled slightly sour.",
     lambda d: [("dish", d, "FOOD#QUALITY", "oily, bland and smelled slightly sour", "negative", "explicit")]),
    ("The {dish} was rubbery and lacked any real seasoning.",
     lambda d: [("dish", d, "FOOD#QUALITY", "rubbery and lacked any real seasoning", "negative", "explicit")]),
    ("The {dish} was completely cold and overcooked.",
     lambda d: [("dish", d, "FOOD#QUALITY", "completely cold and overcooked", "negative", "explicit")]),
    ("The {dish} tasted completely stale and dry.",
     lambda d: [("dish", d, "FOOD#QUALITY", "completely stale and dry", "negative", "explicit")]),

    # Service General Positive
    ("The {service} was extremely courteous, attentive and gave great recommendations.",
     lambda s: [("service", s, "SERVICE#GENERAL", "extremely courteous, attentive and gave great recommendations", "positive", "explicit")]),
    ("The {service} greeted us with warm smiles and prompt hospitality.",
     lambda s: [("service", s, "SERVICE#GENERAL", "warm smiles and prompt hospitality", "positive", "explicit")]),

    # Service General Negative
    ("The {service} were arrogant and completely ignored our requests.",
     lambda s: [("service", s, "SERVICE#GENERAL", "arrogant and completely ignored our requests", "negative", "explicit")]),
    ("The {service} was rude and treated us with sheer indifference.",
     lambda s: [("service", s, "SERVICE#GENERAL", "rude and treated us with sheer indifference", "negative", "explicit")]),

    # Ambience Positive
    ("The vintage {ambience} and dim lighting created a cozy atmosphere.",
     lambda a: [("ambience", a, "AMBIENCE#GENERAL", "cozy atmosphere", "positive", "explicit")]),
    ("The background jazz {ambience} was soothing and relaxing.",
     lambda a: [("ambience", a, "AMBIENCE#GENERAL", "soothing and relaxing", "positive", "explicit")]),

    # Ambience Negative
    ("The {ambience} was deafeningly loud and made conversation impossible.",
     lambda a: [("ambience", a, "AMBIENCE#GENERAL", "deafeningly loud and made conversation impossible", "negative", "explicit")]),
    ("The {ambience} was cramped, noisy and uncomfortably hot.",
     lambda a: [("ambience", a, "AMBIENCE#GENERAL", "cramped, noisy and uncomfortably hot", "negative", "explicit")]),

    # Hygiene Cleanliness Positive
    ("The {hygiene} was sparkling clean and properly sanitized.",
     lambda h: [("hygiene", h, "HYGIENE#CLEANLINESS", "sparkling clean and properly sanitized", "positive", "explicit")]),
    ("The {hygiene} looked spotless and well maintained.",
     lambda h: [("hygiene", h, "HYGIENE#CLEANLINESS", "spotless and well maintained", "positive", "explicit")]),

    # Hygiene Cleanliness Negative
    ("The {hygiene} had greasy grease stains and leftover crumbs.",
     lambda h: [("hygiene", h, "HYGIENE#CLEANLINESS", "greasy grease stains and leftover crumbs", "negative", "explicit")]),
    ("The {hygiene} was filthy and reeked of damp moisture.",
     lambda h: [("hygiene", h, "HYGIENE#CLEANLINESS", "filthy and reeked of damp moisture", "negative", "explicit")]),

    # Restaurant Prices Positive
    ("The {price} was very reasonable and pocket friendly.",
     lambda p: [("price", p, "RESTAURANT#PRICES", "very reasonable and pocket friendly", "positive", "explicit")]),

    # Restaurant Prices Negative
    ("The final {price} was astronomical due to hidden service charges.",
     lambda p: [("price", p, "RESTAURANT#PRICES", "astronomical due to hidden service charges", "negative", "explicit")]),
    
    # Food Style / Options
    ("The menu offered an extensive variety of authentic Awadhi dishes.",
     lambda _: [("fixed", "menu", "FOOD#STYLE_OPTIONS", "extensive variety of authentic Awadhi dishes", "positive", "explicit")]),
    ("Vegetarians will find very limited choices and almost zero options.",
     lambda _: [("fixed", "choices", "FOOD#STYLE_OPTIONS", "very limited choices and almost zero options", "negative", "explicit")])
]

# Implicit Opinion Templates across 5 Archetypes
IMPLICIT_TEMPLATES = [
    # Archetype 1: Idiomatic Financial Distress / Price Disparity
    ("A single plate of {dish} burned a massive hole in my pocket.",
     lambda d: (d, "FOOD#PRICES", "burned a massive hole in my pocket", "negative", "metaphorical_financial_distress")),
    ("Ordering {dish} will cost you an arm and a leg here.",
     lambda d: (d, "FOOD#PRICES", "cost you an arm and a leg", "negative", "metaphorical_financial_distress")),
    ("The bill gave us an instant heart attack when it landed on the table.",
     lambda _: ("bill", "RESTAURANT#PRICES", "gave us an instant heart attack", "negative", "metaphorical_financial_distress")),

    # Archetype 2: Biological & Sanitary Consequences
    ("Both of us spent the entire night hugging the toilet bowl after eating the {dish}.",
     lambda d: (d, "HYGIENE#FOOD_SAFETY", "spent the entire night hugging the toilet bowl", "negative", "biological_illness_consequence")),
    ("Ended up in the emergency ward with acute food poisoning from their {dish}.",
     lambda d: (d, "HYGIENE#FOOD_SAFETY", "ended up in the emergency ward with acute food poisoning", "negative", "biological_illness_consequence")),
    ("We spotted a live cockroach crawling under the {hygiene} during lunch.",
     lambda h: (h, "HYGIENE#FOOD_SAFETY", "spotted a live cockroach crawling", "negative", "foreign_body_contamination")),
    ("A dead fly was floating right in the middle of our {dish}.",
     lambda d: (d, "HYGIENE#FOOD_SAFETY", "dead fly was floating right in the middle", "negative", "foreign_body_contamination")),

    # Archetype 3: Factual Temporal Delays
    ("We sat at table four and waited forty-five minutes before a {service} brought water.",
     lambda s: (s, "SERVICE#PROMPTNESS", "waited forty-five minutes before brought water", "negative", "temporal_wait_delay")),
    ("We finished two full podcast episodes before our {dish} arrived.",
     lambda d: (d, "SERVICE#PROMPTNESS", "finished two full podcast episodes before arrived", "negative", "temporal_wait_delay")),
    ("I had to ask three different servers twice just to receive our dinner bill.",
     lambda _: ("servers", "SERVICE#PROMPTNESS", "had to ask three different servers twice just to receive bill", "negative", "temporal_wait_delay")),
    ("Our starters landed on the table barely three minutes after placing the order.",
     lambda _: ("starters", "SERVICE#PROMPTNESS", "landed on the table barely three minutes after", "positive", "temporal_wait_delay")),

    # Archetype 4: Portion Disparities
    ("The serving of {dish} barely fed a pigeon.",
     lambda d: (d, "FOOD#PRICES", "barely fed a pigeon", "negative", "portion_size_disparity")),
    ("We paid five hundred rupees for a {dish} that contained only one tiny potato.",
     lambda d: (d, "FOOD#PRICES", "contained only one tiny potato", "negative", "portion_size_disparity")),
    ("Huge portion of {dish} that easily fed three hungry adults.",
     lambda d: (d, "FOOD#PRICES", "easily fed three hungry adults", "positive", "portion_size_disparity")),

    # Archetype 5: Texture / Sensory Metaphors
    ("The {dish} melted like butter the moment it touched the tongue.",
     lambda d: (d, "FOOD#QUALITY", "melted like butter the moment it touched the tongue", "positive", "texture_sensory_metaphor")),
    ("Chewing the {dish} felt like chewing on dry cardboard.",
     lambda d: (d, "FOOD#QUALITY", "felt like chewing on dry cardboard", "negative", "texture_sensory_metaphor")),
    ("The {dish} tasted like pure leather.",
     lambda d: (d, "FOOD#QUALITY", "tasted like pure leather", "negative", "texture_sensory_metaphor")),
    ("The {dish} was a heavenly cloud of sweetness.",
     lambda d: (d, "FOOD#QUALITY", "a heavenly cloud of sweetness", "positive", "texture_sensory_metaphor")),

    # Archetype 6: Environmental Disruptions
    ("The blaring club music made it impossible to hear the person sitting across.",
     lambda _: ("club music", "AMBIENCE#GENERAL", "impossible to hear the person sitting across", "negative", "environmental_disruption")),
    ("The air conditioning was barely functioning on a sweltering summer afternoon.",
     lambda _: ("air conditioning", "AMBIENCE#GENERAL", "barely functioning on a sweltering summer afternoon", "negative", "environmental_disruption")),
    ("Tables are crammed so close together that you are practically sitting in your neighbor's lap.",
     lambda _: ("tables", "AMBIENCE#GENERAL", "crammed so close together practically sitting in your neighbor's lap", "negative", "environmental_disruption"))
]

# Compound Reviews combining opposing polarities
COMPOUND_TEMPLATES = [
    ("The {dish} was fragrant, tender and cooked to perfection, but the {other} completely ignored our table for 45 minutes.",
     "other", SERVICE_ASPECTS,
     lambda d, s: [
         {"aspect": d, "category": "FOOD#QUALITY", "opinion": "fragrant, tender and cooked to perfection", "sentiment": "positive", "type": "explicit"},
         {"aspect": s, "category": "SERVICE#PROMPTNESS", "opinion": "completely ignored our table for 45 minutes", "sentiment": "negative", "type": "implicit"}
     ]),
    ("The {dish} melted like butter the moment it touched the tongue, but the {other} was astronomical due to hidden service charges.",
     "other", PRICE_ASPECTS,
     lambda d, p: [
         {"aspect": d, "category": "FOOD#QUALITY", "opinion": "melted like butter the moment it touched the tongue", "sentiment": "positive", "type": "implicit"},
         {"aspect": p, "category": "RESTAURANT#PRICES", "opinion": "astronomical due to hidden service charges", "sentiment": "negative", "type": "explicit"}
     ]),
    ("Although the {other} was extremely courteous, attentive and gave great recommendations, the {dish} was rubbery and lacked any real seasoning.",
     "other", SERVICE_ASPECTS,
     lambda d, s: [
         {"aspect": s, "category": "SERVICE#GENERAL", "opinion": "extremely courteous, attentive and gave great recommendations", "sentiment": "positive", "type": "explicit"},
         {"aspect": d, "category": "FOOD#QUALITY", "opinion": "rubbery and lacked any real seasoning", "sentiment": "negative", "type": "explicit"}
     ]),
    ("We loved the {other} with dim lighting and cozy atmosphere, but both of us spent the entire night hugging the toilet bowl after eating the {dish}.",
     "other", AMBIENCE_ASPECTS,
     lambda d, a: [
         {"aspect": a, "category": "AMBIENCE#GENERAL", "opinion": "cozy atmosphere", "sentiment": "positive", "type": "explicit"},
         {"aspect": d, "category": "HYGIENE#FOOD_SAFETY", "opinion": "spent the entire night hugging the toilet bowl", "sentiment": "negative", "type": "implicit"}
     ])
]


def generate_curated_dataset(target_total: int = 1000) -> List[Dict[str, Any]]:
    samples = []
    seen_texts = set()

    # 1. Generate Compound Reviews (High Complexity)
    for tmpl, placeholder, pool, gen_fn in COMPOUND_TEMPLATES:
        for dish in DISHES:
            for entity in pool:
                text = tmpl.format(dish=dish, other=entity)
                if text not in seen_texts:
                    seen_texts.add(text)
                    quads = gen_fn(dish, entity)
                    # Verify spans are present in text
                    valid = True
                    for q in quads:
                        if q["aspect"].lower() not in text.lower() or q["opinion"].lower() not in text.lower():
                            valid = False
                            break
                    if valid:
                        samples.append({"text": text, "quadruples": quads})

    # 2. Generate Implicit Reviews
    for tmpl, gen_fn in IMPLICIT_TEMPLATES:
        pool = DISHES if "{dish}" in tmpl else HYGIENE_ASPECTS if "{hygiene}" in tmpl else SERVICE_ASPECTS if "{service}" in tmpl else ["general"]
        for item in pool:
            text = tmpl.format(dish=item, hygiene=item, service=item)
            if text not in seen_texts:
                seen_texts.add(text)
                res = gen_fn(item)
                asp, cat, op, pol, arch = res
                if asp.lower() in text.lower() and op.lower() in text.lower():
                    samples.append({
                        "text": text,
                        "quadruples": [{
                            "aspect": asp,
                            "category": cat,
                            "opinion": op,
                            "sentiment": pol,
                            "type": "implicit",
                            "archetype": arch
                        }]
                    })

    # 3. Generate Explicit Reviews
    for tmpl, gen_fn in EXPLICIT_TEMPLATES:
        pool = DISHES if "{dish}" in tmpl else SERVICE_ASPECTS if "{service}" in tmpl else AMBIENCE_ASPECTS if "{ambience}" in tmpl else HYGIENE_ASPECTS if "{hygiene}" in tmpl else PRICE_ASPECTS if "{price}" in tmpl else ["general"]
        for item in pool:
            text = tmpl.format(dish=item, service=item, ambience=item, hygiene=item, price=item)
            if text not in seen_texts:
                seen_texts.add(text)
                res_list = gen_fn(item)
                quads = []
                for _, asp, cat, op, pol, typ in res_list:
                    if asp.lower() in text.lower() and op.lower() in text.lower():
                        quads.append({
                            "aspect": asp,
                            "category": cat,
                            "opinion": op,
                            "sentiment": pol,
                            "type": typ
                        })
                if quads:
                    samples.append({"text": text, "quadruples": quads})

    # Shuffle and trim to target_total
    rng = np.random.RandomState(42)
    indices = rng.permutation(len(samples))
    curated = [samples[i] for i in indices[:target_total]]
    return curated


def save_splits():
    print("Generating strictly verbatim ACOS benchmark dataset...")
    samples = generate_curated_dataset(target_total=1000)
    print(f"Total curated instances: {len(samples)}")

    rng = np.random.RandomState(42)
    indices = rng.permutation(len(samples))
    n_train = 700
    n_val = 150

    splits = {
        "train": [samples[i] for i in indices[:n_train]],
        "val": [samples[i] for i in indices[n_train:n_train + n_val]],
        "test": [samples[i] for i in indices[n_train + n_val:]]
    }

    stats = {
        "total_instances": len(samples),
        "split_counts": {k: len(v) for k, v in splits.items()},
        "category_counts": {},
        "sentiment_counts": {},
        "opinion_type_counts": {"explicit": 0, "implicit": 0}
    }

    for split_name, items in splits.items():
        out_path = DATA_DIR / f"{split_name}.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                for q in item["quadruples"]:
                    c = q["category"]
                    s = q["sentiment"]
                    t = q.get("type", "explicit")
                    stats["category_counts"][c] = stats["category_counts"].get(c, 0) + 1
                    stats["sentiment_counts"][s] = stats["sentiment_counts"].get(s, 0) + 1
                    stats["opinion_type_counts"][t] = stats["opinion_type_counts"].get(t, 0) + 1
        print(f"Saved {split_name}.jsonl: {len(items)} samples -> {out_path}")

    meta_path = DATA_DIR / "benchmark_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"Saved metadata -> {meta_path}")

    print("\nBenchmark Summary:")
    print(f"Explicit Opinions: {stats['opinion_type_counts']['explicit']}")
    print(f"Implicit Opinions: {stats['opinion_type_counts']['implicit']}")
    for cat, cnt in sorted(stats["category_counts"].items(), key=lambda x: -x[1]):
        print(f"  {cat}: {cnt}")


if __name__ == "__main__":
    save_splits()
