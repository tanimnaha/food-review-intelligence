# Kolkata Restaurant Intelligence Dataset
Version 1.0 | Built: 2026-10-29 | 100 restaurants | ~5,000 synthetic reviews | 13,144 real training reviews

A relational dataset for building a restaurant review + sentiment analysis + food-safety
scoring web application (the "Kolkata FoodLens / BiteCheck" project idea).

## Files
| File | Rows | Description |
|---|---|---|
| restaurants.csv | 100 | Master directory of active Kolkata restaurants. Real listings. |
| reviews_kolkata.csv | 5,000 | 50 reviews per restaurant, sentiment + 5-aspect labels. SYNTHETIC. |
| reviews_training_corpus_real.csv | 13,144 | Real English restaurant reviews with ratings + derived sentiment labels. REAL text (Yelp open data). |
| aspect_based_sample_semeval.csv | 86 | Real aspect-based sentiment samples (SemEval restaurant domain). |
| safety_records.csv | 118 | Inspection-style safety records with FSSAI-style licence IDs. SYNTHETIC. |
| restaurant_suitability.csv | 351 | Long-format suitability tags per restaurant (derived rules). |

## Data dictionary (key fields)
### restaurants.csv
- restaurant_id (PK, e.g. KOL0001), name, address, neighbourhood
- latitude/longitude: APPROXIMATE (neighbourhood centroid + jitter; geo_precision column says so)
- primary_cuisine, cuisines, cost_for_two_inr, price_tier (1 Budget - 4 Luxury), price_range
- opening_hours, zomato_rating, zomato_votes (REAL, from compiled Zomato Kolkata listings)
- safety_score_0_100: SYNTHETIC estimate. safety_data_confidence = 'synthetic_estimated'
  or 'safety_data_unavailable' (never invent a score when evidence is missing)
- veg_focused: boolean

### reviews_kolkata.csv
- review_id (PK), restaurant_id (FK), restaurant_name, user_alias (fictional)
- rating 1-5, review_text, review_date (2024-01-01 to 2026-09-30), platform
- sentiment_label: positive / neutral / negative (overall)
- sentiment_food / sentiment_service / sentiment_hygiene / sentiment_ambience /
  sentiment_price: per-aspect labels for aspect-based sentiment analysis (ABSA)
- helpful_votes, verified_visit, language, data_origin

### reviews_training_corpus_real.csv
- review_id, rating (1-5 stars), sentiment_label (derived: >=4 positive, <=2 negative, else neutral)
- cuisine_domain (10 cuisine labels), review_text (REAL English reviews)

### safety_records.csv
- safety_record_id, restaurant_id, fssai_licence_no (SYNTHETIC 14-digit format),
  licence_status, inspection_date, inspection_type, outcome
  (Satisfactory / Needs Improvement / Major Violations), violations_noted
  (pest_control_lapse, cold_storage_temperature, waste_disposal, utensil_hygiene,
  cooking_oil_reuse, drinking_water_quality, staff_hygiene_training, labelling_and_storage),
  reinspection_required, data_origin

### restaurant_suitability.csv
- restaurant_id, tag (student_budget, family_friendly, date_night, group_friendly,
  solo_friendly, veg_friendly, kids_menu, wheelchair_accessible, outdoor_seating, late_night),
  tag_source

## Data provenance & honesty (IMPORTANT)
1. Restaurant listings, ratings, votes, addresses, cuisines, costs, timings: REAL, compiled
   from public Zomato Kolkata listings (github.com/Csengupta1101/Zomato-Kolkata-EDA).
   Review CONTENT was not taken from Zomato - do not present synthetic reviews as real ones.
2. reviews_kolkata.csv reviews are SYNTHETIC, generated from template pools seeded with
   Kolkata dining vocabulary (biryani/chaap, shorshe ilish, Tangra chilli chicken, kathi rolls,
   Park Street classics) and conditioned on each restaurant's real rating.
3. reviews_training_corpus_real.csv is REAL text from Yelp open data (via HuggingFace dataset
   yav1327/restaurant_reviews). Use it to TRAIN your sentiment/ABSA model; apply it to
   reviews_kolkata.csv and your app's user submissions.
4. Safety records and safety scores are SYNTHETIC placeholders. For a production app, replace
   them with real FSSAI/KMC data and show "safety data unavailable" when you have none.
5. Coordinates are approximate neighbourhood centroids, not exact locations.

## Suggested ML pipeline
1. Train baseline: reviews_training_corpus_real.csv -> TF-IDF + Logistic Regression, or a
   DistilBERT fine-tune, targeting sentiment_label.
2. Aspect model: weak-label reviews_kolkata.csv with the 5 sentiment_* columns -> multi-label
   aspect classifier. Validate on aspect_based_sample_semeval.csv.
3. App scores: per-restaurant customer experience score = weighted mean of aspect sentiments
   on reviews_kolkata.csv + future user reviews.
4. Safety score: join safety_records.csv; recompute as new evidence arrives; show confidence.
