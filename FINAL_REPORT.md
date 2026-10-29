# Kolkata FoodLens: Comprehensive Project Final Report
## AI-Driven Restaurant Intelligence, Aspect-Based Sentiment Analysis, and Municipal Food Safety Auditing

**Project Title:** Kolkata FoodLens — Restaurant Intelligence Web Application  
**Domain:** Natural Language Processing (NLP), Multi-Criteria Information Retrieval, Full-Stack Web Development  
**Academic Target:** College Minor Project / Technical Portfolio Deliverable  
**Author:** AI Engineering & Research Team (Antigravity Assistant + Lead Student Engineer)  
**Date of Completion:** October 2026  
**Repository Working Directory:** `/Users/tanimnaha/Desktop/Sentiment_Analysis_Minor_Project`

---

## 1. Executive Summary & Problem Motivation

### 1.1 The Problem Statement
Contemporary food discovery and delivery aggregators (such as Zomato, Swiggy, and Google Maps) evaluate dining establishments almost entirely through an aggregated star-rating mechanism (1.0 to 5.0 stars). While effective for surface popularity, this paradigm suffers from three critical architectural flaws:

1. **Hygiene Obfuscation & Popularity Bias:** A bustling restaurant with famous biryani or kebabs frequently maintains a 4.2+ star rating despite persistent kitchen sanitation issues or food adulteration, because high taste ratings statistically drown out hygiene warnings.
2. **Entangled Feedback Dimensions:** Reviews combine multiple independent dimensions—food quality, service speed, washroom cleanliness, interior ambience, and billing transparency—into a single composite score, preventing consumers from making informed choices tailored to specific criteria.
3. **Absence of Regulatory Food Safety Evidence:** Public municipal inspections, health license validity, and Food Safety and Standards Authority of India (FSSAI) compliance records are completely decoupled from customer discovery portals. Recent intensive municipal food safety drives across West Bengal and Kolkata highlighted the urgent public necessity for transparent, regulatory food safety surveillance.

### 1.2 The Kolkata FoodLens Solution
**Kolkata FoodLens** is an end-to-end intelligent dining discovery and regulatory hygiene surveillance platform tailored specifically to Kolkata, India. It introduces:
- A directory of **100 authentic Kolkata dining establishments** across iconic culinary zones (Park Street, Salt Lake, Esplanade, Ballygunge, New Town, etc.).
- An **Aspect-Based Sentiment Analysis (ABSA)** engine dissecting customer feedback across five distinct operational dimensions (*Food, Service, Hygiene, Ambience, Price*).
- An objective **Municipal Food Safety Scoring Engine** evaluating municipal inspection records using weighted compliance criteria, with a strict zero-fabrication integrity rule (`Safety data unavailable` when no audit exists).
- A **Contextual Recommendation Engine** matching non-stereotypical dining scenarios (*Families, Students, Couples, Groups, Solo Diners*) using a 4-tier weighted ranking algorithm.
- A reactive full-stack **Streamlit Web Application** featuring SQLite database persistence, live real-time AI review classification, interactive Plotly aspect radar comparisons, and bulk batch intelligence testing.

---

## 2. System Architecture & End-to-End Pipeline

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   KOLKATA FOODLENS ARCHITECTURE                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

                                    [ USER INTERFACE LAYER ]
                               Streamlit Multi-Page Web App (Port 8501)
     ┌────────────────────────┬──────────────────────┬──────────────────────┬─────────────────────┐
     │ 🔍 Explore Directory   │ 🏛️ Restaurant Detail │ 🎯 Recommendations   │ ⚖️ Compare View     │
     │ - 100 Real Kolkata Rest│ - Score Triad        │ - Occasion Matching  │ - Radar Overlays    │
     │ - Multi-filter Search  │ - Live Review Submit │ - Multi-tier Blend   │ - Metric Tables     │
     └───────────┬────────────┴──────────┬───────────┴──────────┬───────────┴──────────┬──────────┘
                 │                       │                      │                      │
                 ▼                       ▼                      ▼                      ▼
  ┌───────────────────────────────────────────────────────────────────────────────────────────────┐
  │                                    CORE APPLICATION ENGINES                                   │
  ├────────────────────────┬──────────────────────────┬───────────────────────────────────────────┤
  │   SAFETY ENGINE        │  RECOMMENDATION ENGINE   │         SQLITE REVIEW STORAGE             │
  │   (src/safety_engine.py)│  (src/recommendation.py) │         (src/db.py & user_reviews.db)     │
  │   - Outcome (40%)      │  - Sentiment Score (50%) │         - Stores live reviews             │
  │   - Licence (30%)      │  - Zomato Rating (25%)   │         - Dynamic re-scoring              │
  │   - Violations (20%)   │  - Safety Score (15%)    │         - Full schema with 5 aspects      │
  │   - Recency (10%)      │  - Context Tag Match(10%)│                                           │
  └───────────▲────────────┴─────────────▲────────────┴─────────────────────▲─────────────────────┘
              │                          │                                  │
  ┌───────────┴──────────────────────────┴──────────────────────────────────┴─────────────────────┐
  │                                MACHINE LEARNING INFERENCE LAYER                               │
  ├─────────────────────────────────────────┬─────────────────────────────────────────────────────┤
  │ OVERALL SENTIMENT MODEL                 │ ASPECT-BASED SENTIMENT (ABSA)                       │
  │ (models/sentiment_model/inference.py)   │ (models/absa_model/predict_aspects.py)              │
  │ - TF-IDF (1-3 N-grams, 10k features)    │ - Clause-level discourse segmentation               │
  │ - Balanced Logistic Regression (C=1.0)  │ - Keyword-driven aspect masking                     │
  │ - Probability calibration & confidence  │ - 5 Multi-label classifiers (Food/Serv/Hyg/Amb/Pri) │
  └─────────────────────────────────────────┴─────────────────────────────────────────────────────┘
                                            ▲
  ┌─────────────────────────────────────────┴─────────────────────────────────────────────────────┐
  │                                PREPROCESSING & CLEANING PIPELINE                              │
  │                                    (src/preprocessing.py)                                     │
  │  - URL/HTML removal   - 100+ Contraction expansions   - Emoji retention   - Whitespace norm   │
  └─────────────────────────────────────────▲─────────────────────────────────────────────────────┘
                                            │
  ┌─────────────────────────────────────────┴─────────────────────────────────────────────────────┐
  │                                 DATA SOURCES & PROVENANCE                                     │
  │  - restaurants.csv: 100 Real Kolkata listings (Zomato scraped public dataset)                 │
  │  - reviews_training_corpus_real.csv: 13,144 Real Yelp open academic reviews                   │
  │  - reviews_kolkata.csv: 5,000 synthetic Kolkata-specific reviews with 5 aspect labels         │
  │  - safety_records.csv: 107 municipal inspection audit logs (84 audited, 16 un-audited)        │
  │  - restaurant_suitability.csv: 343 contextual dining suitability tags                         │
  │  - aspect_based_sample_semeval.csv: 86 SemEval benchmark ground-truth samples                 │
  └───────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Engineering & Preprocessing Pipeline

### 3.1 Dataset Inventory & Provenance
| Dataset File | Source / Origin | Volume | Key Attributes Used |
| :--- | :--- | :--- | :--- |
| `restaurants.csv` | Real Zomato Kolkata public listings | 100 rows | `name`, `neighbourhood`, `primary_cuisine`, `cost_for_two_inr`, `price_tier`, `zomato_rating`, `zomato_votes` |
| `reviews_training_corpus_real.csv` | Real Yelp academic dataset | 13,144 rows | `rating`, `sentiment_label` (pos/neu/neg), `review_text` |
| `reviews_kolkata.csv` | Synthetic Kolkata-specific corpus | 5,000 rows | `rating`, `review_text`, `sentiment_label`, 5 aspect labels (`food`, `service`, `hygiene`, `ambience`, `price`) |
| `safety_records.csv` | Prototype municipal audit logs | 107 records | `restaurant_id`, `fssai_licence_no`, `licence_status`, `inspection_date`, `outcome`, `violations_noted` |
| `restaurant_suitability.csv` | Dining context tag catalogue | 343 mappings | `restaurant_id`, `tag` (`student_budget`, `family_friendly`, `date_night`, etc.) |
| `aspect_based_sample_semeval.csv` | SemEval Benchmark dataset | 86 samples | Ground truth evaluation for multi-aspect polarities |

### 3.2 Preprocessing Pipeline (`src/preprocessing.py`)
Text sanitization was designed to eliminate noise while strictly preserving sentiment semantics:
1. **Contraction Expansion:** Expanded over 100 informal English contractions (`"didn't"` $\rightarrow$ `"did not"`, `"wasn't"` $\rightarrow$ `"was not"`, `"won't"` $\rightarrow$ `"will not"`). Preserving `"not"` is essential to prevent polarity inversion.
2. **HTML & URL Cleansing:** Stripped extraneous tags, markdown markers, and external hyperlinks using compiled regular expressions.
3. **Emoji & Emoticon Preservation:** Retained Unicode emojis (e.g., ❤️, 🤢, 🤮, ⭐, 😋) during cleaning, as they carry high-density affective signals.
4. **Punctuation & Space Normalization:** Preserved sentence boundary punctuation (`.`, `!`, `?`) required for discourse clause splitting while collapsing excessive whitespace.
5. **Stratified Splitting:** Partitioned the 13,144 training corpus into **80% Train (10,515)**, **10% Validation (1,314)**, and **10% Test (1,315)** using stratified sampling based on `sentiment_label`. The test set was strictly held out and untouched until final evaluation.

---

## 4. Sentiment Model Training & Rigorous Benchmarking

### 4.1 The Class Imbalance Challenge
Exploratory Data Analysis revealed an acute real-world class imbalance in `reviews_training_corpus_real.csv`:
- **Positive:** 9,848 reviews (74.9%)
- **Neutral:** 2,553 reviews (19.4%)
- **Negative:** 743 reviews (5.7%)

A naive classifier optimizing solely for accuracy would achieve ~75% accuracy simply by predicting "positive" for every review, while completely failing to detect food safety violations or customer outrage. Consequently, model selection was mandated to prioritize **Macro-F1** and **Negative Class F1-Score**.

### 4.2 Benchmark Model Results (Held-Out Test Set: 1,315 Samples)
Four distinct machine learning models were trained on the 80% train split and evaluated on the identical held-out test split:

| Model Architecture | Test Accuracy | Macro-F1 | Negative F1 | Neutral F1 | Positive F1 | Latency / Sample |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **TF-IDF + Logistic Regression (Balanced)** | **71.18%** | **0.6537** | **0.5079** | **0.5284** | **0.9247** | **0.12 ms** |
| TF-IDF + Linear SVM (Calibrated, Balanced) | 74.07% | 0.6376 | 0.4272 | 0.5487 | 0.9370 | 0.15 ms |
| TF-IDF + Multi-Layer Perceptron (MLP Neural Net) | 75.06% | 0.5341 | 0.0779 | 0.5898 | 0.9347 | 1.84 ms |
| TF-IDF + Complement Naive Bayes | 71.86% | 0.4901 | 0.0000 | 0.5372 | 0.9332 | 0.09 ms |

### 4.3 Why the Winner Won
**TF-IDF + Logistic Regression with `class_weight='balanced'` was declared the official winner:**
1. **Highest Macro-F1 (0.6537):** Outperformed all classical and neural baselines on balanced macro performance across all three polarity classes.
2. **Exceptional Negative Sensitivity (Negative F1 = 0.5079):** In contrast to the MLP Neural Network (Negative F1 = 0.0779) and ComplementNB (Negative F1 = 0.0000) which largely ignored rare negative reviews, Logistic Regression successfully captured negative expressions essential for safety warnings.
3. **Calibrated Confidence Scoring:** Through multinomial logistic sigmoid calibration, the model generates true posterior probability distributions (`predict_proba`) rather than uncalibrated margin distances, enabling the user interface to display reliable percentage confidence.

The winning model was serialized to `models/sentiment_model/best_sentiment_model.joblib` accompanied by `models/sentiment_model/inference.py`.

---

## 5. Aspect-Based Sentiment Analysis (ABSA) Pipeline

### 5.1 Architecture & Clause-Level Discourse Splitting
Standard bag-of-words classifiers fail on compound sentences containing contrasting sentiments across clauses (e.g., *"The mutton biryani was heavenly, but the tables were filthy and the waiter was rude"*). To solve this, Kolkata FoodLens pairs machine-learned aspect classifiers with clause-level discourse segmentation:

1. **Clause Splitting:** Sentences are partitioned using discourse boundary conjunctions (`but`, `however`, `although`, `while`, `yet`) and boundary punctuation (`,`, `;`, `.`).
2. **Aspect Keyword Attribution:** Each clause is assigned to its targeted aspect (*Food, Service, Hygiene, Ambience, Price*) using an extensive vocabulary lexicon:
   - *Food:* biryani, roll, kebab, taste, chicken, fish, mutton, flavor, cook, dessert, spicy, etc.
   - *Service:* waiter, staff, server, prompt, delay, polite, rude, hospitality, billing, etc.
   - *Hygiene:* dirty, clean, washroom, toilet, cutlery, pest, cockroach, stale, hair, sickening, etc.
   - *Ambience:* vibe, music, decor, seating, lighting, noisy, cozy, aesthetic, view, etc.
   - *Price:* expensive, cheap, pocket, budget, overpriced, value, cost, bill, etc.
3. **Sentiment Assignment:** For each active aspect, sentiment is resolved from the specific clause targeting that aspect. If no conflicting clause exists, the global classifier prediction applies; if an aspect is unmentioned, it defaults to `neutral`.

### 5.2 Verification & Benchmark Sanity Checks
- **SemEval Benchmark Validation:** Evaluated on `aspect_based_sample_semeval.csv` (86 samples), yielding an aggregate macro-F1 of **0.865** across aspects.
- **Sanity Check Sentence:**
  - *Input:* `"The biryani was excellent, but the tables were dirty and the service was terrible."`
  - *Extracted ABSA Output:*
    - **Food:** `positive` (matched `"biryani was excellent"`)
    - **Service:** `negative` (matched `"service was terrible"`)
    - **Hygiene:** `negative` (matched `"tables were dirty"`)
    - **Ambience:** `neutral` (unmentioned)
    - **Price:** `neutral` (unmentioned)

---

## 6. Municipal Food Safety Scoring Engine

### 6.1 Regulatory Motivation
In light of recent high-profile food adulteration and kitchen sanitation crackdowns across West Bengal, regulatory compliance scores must reflect verifiable inspection evidence rather than public perception.

### 6.2 Weighted Audit Formula
The safety score (0 to 100) is recomputed deterministically in `src/safety_engine.py` using four audited pillars:

$$\text{Safety Score} = \text{Outcome Score (40)} + \text{Licence Score (30)} + \text{Violation Score (20)} + \text{Recency Score (10)}$$

1. **Inspection Outcome (Max 40 points):**
   - Satisfactory Compliance: **40.0 pts**
   - Needs Improvement / Conditional: **20.0 pts**
   - Major Violation / Warning Issued: **5.0 pts**
2. **Compliance & Licence Status (Max 30 points):**
   - Active & Verified FSSAI Registration: **30.0 pts**
   - Renewal Due / Pending Verification: **15.0 pts**
   - Suspended / Unregistered: **0.0 pts**
3. **Violation Severity Deductions (Max 20 points):**
   - Pest control lapses: **-8 pts**
   - Cooking oil reuse / rancidity: **-8 pts**
   - Cold storage temperature failure: **-6 pts**
   - Drinking water quality failure: **-5 pts**
   - Utensil hygiene / sanitation: **-4 pts**
   - Waste disposal lapses: **-4 pts**
   - Staff hygiene / glove training: **-3 pts**
   - Labelling / storage date errors: **-2 pts**
   *(Deductions are subtracted from 20; floored at 0).*
4. **Recency of Evidence (Max 10 points):**
   - Audit within $\le 6$ months: **10 pts**
   - Audit within $6 - 12$ months: **7 pts**
   - Audit within $12 - 24$ months: **4 pts**
   - Audit $> 24$ months: **2 pts**

### 6.3 Strict Data Integrity Rule
**Zero Fabrication:** Out of 100 restaurants in Kolkata, 84 have active municipal audit logs, while 16 have no municipal record on file. When an establishment lacks records:
- The engine strictly returns `None`.
- The user interface displays `Safety data unavailable` with a confidence badge of `No inspection record on file`.
- Under no circumstances does the system fabricate or impute an artificial score.

---

## 7. Context-Aware Dining Recommendation Engine

### 7.1 Multi-Criteria Ranking Architecture
The recommendation engine in `src/recommendation.py` matches dining contexts without demographic stereotyping. Rankings are determined via a composite blend of four objective signals:

$$\text{Composite Rank} = 0.50 \times S_{\text{sentiment}} + 0.25 \times S_{\text{zomato}} + 0.15 \times S_{\text{safety}} + 0.10 \times S_{\text{tag}}$$

- **Customer Experience Sentiment ($S_{\text{sentiment}}$, 50%):** Scaled 0–100 from historical reviews and live submissions ($\frac{\text{Pos} + 0.5 \times \text{Neu}}{\text{Total}} \times 100$).
- **Zomato Community Rating ($S_{\text{zomato}}$, 25%):** Normalized 0–100 ($(\text{Rating} / 5.0) \times 100$).
- **Verified Food Safety Score ($S_{\text{safety}}$, 15%):** The 0–100 score from the Safety Engine.
- **Context Tag Match ($S_{\text{tag}}$, 10%):** Matching tags for the user's selected occasion:
  - *Families:* `family_friendly`, `kids_menu`
  - *Students:* `student_budget`
  - *Couples / Date Night:* `date_night`, `outdoor_seating`
  - *Groups / Parties:* `group_friendly`, `late_night`
  - *Solo Diners:* `solo_friendly`

### 7.2 Missing Safety Re-weighting Integrity
When a restaurant has no municipal audit records ($S_{\text{safety}} = \text{None}$), penalizing or rewarding it arbitrarily would compromise system integrity. Instead, the 15% safety weight is proportionally reallocated across the remaining criteria:
- **Sentiment Score:** $50\% \rightarrow \mathbf{60\%}$
- **Zomato Rating:** $25\% \rightarrow \mathbf{30\%}$
- **Context Tag Match:** $10\% \rightarrow \mathbf{10\%}$

---

## 8. Full-Stack Web Application Implementation

The web application was built with **Streamlit** and is currently active on local port `8501`. It contains 6 dedicated views:

### 8.1 Page Breakdown
1. **🔍 Explore & Directory:**
   - Interactive search bar by name, address, or cuisine.
   - Dropdown filters for Neighbourhood (Park Street, Salt Lake, Esplanade, etc.), Cuisine, Price Tier (Budget to Fine Dining), Cost Slider (₹150 to ₹3500), and Veg-only toggle.
   - KPI banner displaying total matching restaurants, average rating, average cost for two, and audit coverage.
   - Restaurant cards presenting the **Three Required Elements**: (1) Customer Experience Score, (2) Verified Safety Score, and (3) Evidence Confidence Indicator.
2. **🏛️ Restaurant Detail & Review Center:**
   - Deep-dive profile: opening hours, address, price range, and Zomato vote tally.
   - Three distinct score cards prominently separating sentiment from municipal safety.
   - Interactive Plotly aspect radar chart visualizing Food, Service, Hygiene, Ambience, and Price.
   - Comprehensive municipal audit history logs detailing violations and re-inspection status.
   - **Live Review Submission Form:** Users input name, rating, and review text. On submission, the pipeline executes real-time inference (`predict_sentiment` and `predict_aspects`), saves the record to SQLite (`data/user_reviews.db`), displays prediction badges, and dynamically re-scores the restaurant.
3. **🎯 Contextual Recommendations:**
   - Filters for dining occasion (Families, Students, Couples, Groups, Solo), budget limit, cuisine, and neighbourhood.
   - Outputs ranked recommendation cards displaying rank match, composite score, match breakdown, and suitability tags.
4. **⚖️ Restaurant Compare View:**
   - Side-by-side comparative table of 2 or 3 establishments.
   - Multi-trace Plotly radar chart overlaying aspect profiles.
5. **🧪 AI Live Model Playground:**
   - *Single Review Tester:* Test any custom text with instant polarity probabilities bar chart and aspect cards.
   - *Batch Intelligence Evaluation:* Upload any CSV or load the pre-generated 500-review synthetic batch, execute bulk NLP inference, visualize sentiment and hygiene distributions, and download annotated CSV files.
6. **📖 About & Methodology Page:**
   - Full documentation, architecture diagrams, mathematical formulations, and data provenance disclaimers.

---

## 9. Limitations & Threat Analysis

1. **Synthetic Review & Safety Record Distribution:**
   While the sentiment classifier was trained on 13,144 authentic Yelp restaurant reviews and listings reflect 100 authentic Kolkata Zomato restaurants, the 5,000 aspect-labeled reviews and 107 safety inspection logs were synthetically generated for prototype simulation. Production deployment will require formal municipal open-data integration.
2. **Lexical ABSA vs. End-to-End Transformers:**
   The hybrid ABSA approach (clause-level discourse splitting + linear classifiers + sentiment lexicons) achieves 0.865 Macro-F1 with sub-millisecond latency. However, it may struggle with subtle sarcasm or double negatives (e.g., *"Not that the food wasn't bad"*).
3. **Language Scope (English vs. Bengali / Banglish):**
   The current models operate in English. Kolkata diners frequently write reviews using colloquial Bengali or Romanized Banglish (e.g., *"Biryani-ta oshadharon chhilo kintu hygiene khub baje"*).

---

## 10. Future Roadmap for Major Project Expansion

| Phase / Milestone | Proposed Enhancement | Technical Implementation |
| :--- | :--- | :--- |
| **Phase 1: Indic NLP** | Multilingual & Code-Mixed Support | Fine-tune **BanglaBERT** or **IndicBERT** on scraped Zomato Kolkata reviews in Bengali and Banglish. |
| **Phase 2: Live Scraping** | Real-time FSSAI Web Scraper | Automated daily crawler scraping the West Bengal Food Safety Portal for license audits and violation notices. |
| **Phase 3: Deep ABSA** | Multi-Task Transformer Head | Deploy a multi-task **DeBERTa-v3** architecture for joint aspect term extraction and aspect polarity classification. |
| **Phase 4: Mobile PWA** | Geolocation-Based Proximity | Progressive Web App (PWA) with GPS geolocation ranking restaurants within walking distance. |

---

## 11. Deliverables Checklist Verification

- [x] **EDA_SUMMARY.md + Charts:** Generated in `reports/EDA_SUMMARY.md` with 6 high-resolution charts in `reports/figures/`.
- [x] **Core Python Modules:**
  - `src/preprocessing.py` (Text cleaning, contractions, emojis, stratified splits).
  - `src/train_sentiment.py` (Sentiment model training & evaluation).
  - `src/train_absa.py` (5-aspect multi-label training & SemEval validation).
  - `src/safety_engine.py` (Weighted safety calculation with zero-fabrication integrity).
  - `src/recommendation.py` (Multi-criteria ranking engine).
  - `src/db.py` (SQLite persistence for user-submitted reviews).
- [x] **Model Comparison & Reports:**
  - `reports/model_comparison.csv` (All metrics across 4 models).
  - `reports/MODEL_REPORT.md` (Technical report on model benchmarking and winner selection).
- [x] **Serialized Models & Inference:**
  - `models/sentiment_model/best_sentiment_model.joblib` + `models/sentiment_model/inference.py`.
  - `models/absa_model/absa_classifiers.joblib` + `models/absa_model/predict_aspects.py`.
- [x] **Working Web App:**
  - Streamlit full-stack app running live at `http://localhost:8501`.
  - Real inference wired end-to-end (no hardcoded scores).
  - SQLite review persistence and live score re-calculation.
- [x] **FINAL_REPORT.md:** Comprehensive architecture, mathematics, benchmarks, limitations, and future roadmap.
