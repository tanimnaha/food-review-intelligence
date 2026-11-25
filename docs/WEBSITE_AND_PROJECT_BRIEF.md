# Kolkata FoodLens: Comprehensive Project & Website Technical Brief

**Project Title**: Comparative Analysis of Machine Learning Algorithms for Sentiment Classification of Online Food Reviews  
**Application Name**: Kolkata FoodLens – Unified Restaurant & NLP Intelligence Platform  
**Target Domain**: Online Food Reviews, Dining Recommendations, and Public Health Hygiene Surveillance for Kolkata, West Bengal  
**Tech Stack**: Python 3.12, Streamlit, Scikit-Learn, Pandas, NumPy, SQLite 3 (WAL mode), Plotly, Matplotlib, Seaborn  

---

## 1. Executive Summary & Core Motivation

### 1.1 The "Star-Rating Paradox" in Restaurant Aggregators
Commercial dining aggregators (e.g., Zomato, Swiggy, Yelp, Google Maps) rely heavily on simplistic 1-to-5 star ratings. This creates three critical failures in real-world consumer decision-making and civic oversight:
1. **Conflation of Popularity with Food Safety**: A cafe can achieve a 4.6-star rating due to trendy ambient lighting, photogenic desserts, and influencer marketing, while its back-kitchen harbors severe hygiene violations (e.g., repeated frying oil reuse, pest contamination, improper temperature holding).
2. **The "Averaging Out" of Critical Violations**: In a restaurant with 2,000 reviews, 50 severe warnings about acute food poisoning or unsanitary washrooms are statistically drowned out by 1,950 4-star and 5-star ratings.
3. **Manual Reading Bottleneck**: An ordinary consumer or a municipal health inspector cannot read through thousands of lengthy paragraphs to identify recurring operational failures.

### 1.2 The Kolkata FoodLens Solution
**Kolkata FoodLens** resolves this paradox by decoupling superficial popularity from verifiable operational quality. It builds a multi-criteria natural language processing (NLP) and civic intelligence engine that:
- Classifies customer sentiment into **Positive, Negative, and Neutral** categories using cost-sensitive learning to handle severe real-world class imbalance.
- Deconstructs compound reviews into **5 fine-grained dining dimensions** (Food Quality, Service, Hygiene, Ambience, Price/Value) using Aspect-Based Sentiment Analysis (ABSA).
- Deploys an automated **Public Health Early-Warning Scanner** grounded in peer-reviewed inspection analytics from the **U.S. CDC, NYC Department of Health (Harrison et al.)**, and **Harvard Smart Inspection Analytics (Glaeser et al.)**.
- Implements a transparent **4-Layer Recommendation Utility Formula** combining sentiment, community ratings, verified municipal safety scores, and context tags.

---

## 2. System Architecture & Mathematical Foundations

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 KOLKATA FOODLENS PIPELINE                              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [ Raw User Review ]                                                                   │
│          │                                                                             │
│          ▼                                                                             │
│  1. Text Normalization ────► Lowercasing, Regex Cleaning, Contraction Expansion        │
│          │                                                                             │
│          ▼                                                                             │
│  2. Feature Extraction ────► Sublinear TF-IDF (Unigrams + Bigrams, max_features=25k)   │
│          │                                                                             │
│          ├──────────────────────────────┬──────────────────────────────┐               │
│          ▼                              ▼                              ▼               │
│  3. Sentiment Engine            4. ABSA Engine                 5. Public Health        │
│     (Balanced Logistic Reg)        (Clause Segmentation)          Surveillance Engine  │
│     Macro F1: 0.7217               5 Dining Dimensions            8 Violation Categories│
│     Negative / Neutral / Pos       Food / Service / Hygiene       Bio-Illness Flags    │
│                                    Ambience / Price               Priority Ranking     │
│          │                              │                              │               │
│          └──────────────────────────────┴──────────────────────────────┘               │
│                                         │                                              │
│                                         ▼                                              │
│                 6. Multi-Criteria Recommendation Algorithm                             │
│                    50% Sentiment + 25% Zomato + 15% Safety + 10% Context               │
│                                         │                                              │
│                                         ▼                                              │
│                 7. Responsive Streamlit Web Application (9 Pages)                      │
│                    SQLite Database Persistence (WAL Mode)                              │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 The 4-Layer Recommendation Utility Formula
Instead of sorting restaurants by star ratings, every recommendation is computed deterministically:

$$\text{Final Score} = 0.50 \cdot S_{\text{sentiment}} + 0.25 \cdot R_{\text{zomato}} + 0.15 \cdot H_{\text{safety}} + 0.10 \cdot C_{\text{context}}$$

Where:
1. **$S_{\text{sentiment}}$ (50% Weight) — Customer Experience Sentiment Score**:
   Derived from all classified reviews of that establishment:
   $$S_{\text{sentiment}} = \left(\frac{N_{\text{pos}} + 0.5 \cdot N_{\text{neu}}}{N_{\text{total}}}\right) \times 100$$
2. **$R_{\text{zomato}}$ (25% Weight) — Normalized Community Rating**:
   $$R_{\text{zomato}} = \left(\frac{\text{Rating}}{5.0}\right) \times 100$$
3. **$H_{\text{safety}}$ (15% Weight) — Verified Municipal Safety Score**:
   Computed from municipal FSSAI inspection audits based on 4 criteria:
   - Inspection Outcomes (Passed, Notice Issued, Failed): **40%**
   - FSSAI License & Compliance Validity: **30%**
   - Severity of Recorded Violations: **20%**
   - Recency of Evidence (Decay factor over time): **10%**  
   *(Strict Integrity Rule: If an establishment has never been inspected, the system outputs `None` and displays "Safety Data Unavailable"—it never fabricates or hallucinates a score).*
4. **$C_{\text{context}}$ (10% Weight) — Dining Context Tag Match**:
   Non-stereotypical matching against curated occasion tags (`family`, `students`, `couples`, `groups`, `solo`).

---

### 2.2 Text Preprocessing & Token Normalization (`src/preprocessing.py`)
Unstructured dining reviews present significant linguistic noise. The pipeline executes:
- **`expand_contractions(text)`**: Expands 120+ colloquial English contractions (e.g., `"didn't"` $\rightarrow$ `"did not"`, `"won't"` $\rightarrow$ `"will not"`, `"can't"` $\rightarrow$ `"cannot"`). This is critical because standard regex tokenizers often strip punctuation, converting `"wasn't tasty"` into `"was tasty"` and reversing sentiment polarity.
- **`clean_text(text, keep_emojis=True)`**: Strips HTML tags, web URLs, and special characters while preserving emojis (e.g., ❤️, 🤢, 🔥, 🤮) by mapping them to descriptive tokens or retaining their Unicode representations.
- **Negation-Preserving Filtering**: Standard stopword removal discards negation words (`"not"`, `"no"`, `"never"`). Our customized dictionary explicitly retains all negation operators.

---

### 2.3 Feature Extraction: Sublinear TF-IDF
We transform normalized strings into numerical vectors using Scikit-Learn's `TfidfVectorizer`:
- **N-Gram Range `(1, 2)`**: Captures individual words (unigrams like `"delicious"`) and modifier pairs (bigrams like `"not clean"`, `"overpriced biryani"`, `"rude waiter"`).
- **Sublinear Term Frequency (`sublinear_tf=True`)**: Replaces raw term frequency $tf$ with $1 + \log(tf)$ for $tf > 0$. In lengthy reviews, repeating the word `"bad"` five times does not mean the review is five times worse; logarithmic dampening prevents high-frequency tokens from dominating vector space distances.
- **Vocabulary Bounds**: `max_features=25,000`, `min_df=2` (prunes typographical typos appearing only once).

---

### 2.4 Model Benchmarks & Why Logistic Regression Won
We evaluated four candidate architectures on **13,144 authentic restaurant reviews** partitioned into an **80/10/10 stratified split** (Train = 10,515; Validation = 1,314; Test = 1,315):

| Candidate Architecture | Test Accuracy | Macro Precision | Macro Recall | Macro F1 | Neutral Class F1 |
|:---|:---:|:---:|:---:|:---:|:---:|
| **TF-IDF + Complement Naive Bayes** | 71.86% | 47.64% | 50.47% | 0.4901 | **0.00% (Failed)** |
| **TF-IDF + MLP (Neural Network)** | 75.06% | 83.60% | 53.12% | 0.5341 | 7.79% |
| **TF-IDF + Linear SVM (LinearSVC)** | **83.97%** | 74.58% | 59.95% | 0.7073 | 42.72% |
| **TF-IDF + Logistic Regression (Balanced)** | 71.18% / 82.55% | 62.97% | **69.82%** | **0.7217** | **50.40% (Winner)** |

#### Key Engineering Insight: The Neutral-Class Dilemma
- In real-world dining feedback, the dataset is severely skewed: **68.7% Positive, 18.8% Negative, and only 12.5% Neutral**.
- Standard Naive Bayes and uncalibrated models collapsed on Neutral reviews, assigning 0% recall to the minority class.
- While Linear SVM maximized raw accuracy by prioritizing the dominant Positive class, **Logistic Regression with `class_weight='balanced'` achieved the highest Macro F1 (0.7217)**. It automatically balances loss penalties inversely proportional to class frequencies:
  $$w_c = \frac{N_{\text{total}}}{N_{\text{classes}} \cdot N_c}$$
  This enabled the production model to correctly classify **50.4% of neutral reviews** and **69.8% of negative reviews**, ensuring consumer warnings are never missed.

---

### 2.5 Aspect-Based Sentiment Analysis (ABSA) Engine (`src/train_absa.py`)
To prevent monolithic sentiment distortion, the ABSA engine segments sentences into clauses and evaluates sentiment across five specific hospitality pillars:
1. **Food Quality**: Taste, freshness, seasoning, authentic flavors, temperature.
2. **Service**: Waiter responsiveness, order delay, billing speed, hospitality.
3. **Hygiene**: Washroom cleanliness, kitchen sanitation, cutlery washing, pest presence.
4. **Ambience**: Lighting, seating comfort, background noise, decor, air conditioning.
5. **Price / Value**: Portion sizing, billing transparency, affordability for college students.

---

### 2.6 Database Architecture (`src/db.py`)
- **Storage**: SQLite 3 database (`data/reviews.db`) with Write-Ahead Logging (`WAL` mode) enabled for rapid concurrent read/write transactions.
- **Schema**:
  - `review_id` (Primary Key, integer auto-increment)
  - `restaurant_id` (Foreign Key string, e.g., `"KOL0001"`)
  - `user_name` (Text string)
  - `rating` (Integer 1 to 5)
  - `review_text` (Raw text)
  - `sentiment_label` (Predicted label: `positive`, `neutral`, `negative`)
  - `sentiment_score` (Confidence probability $0.00$ to $1.00$)
  - `aspect_breakdown` (JSON string containing polarities for Food, Service, Hygiene, Ambience, Price)
  - `timestamp` (UTC ISO-8601 string)

---

## 3. Deep-Dive: The 9 Website Pages Explained

### Page 1: 🔍 Kolkata Directory & Search
- **Primary Function**: Broad consumer exploration and multi-attribute discovery portal.
- **Search & Filter Controls**:
  - Full-text search matching restaurant names, signature cuisines, and addresses.
  - Neighbourhood dropdown covering 15+ Kolkata zones (Park Street, Salt Lake, Ballygunge, New Town, Gariahat, Shyambazar, etc.).
  - Cuisine selector (Bengali, Mughlai, Chinese, Continental, North Indian, Street Food).
  - Price Tier dropdown (Budget, Moderate, Premium, Fine Dining).
  - Cost for Two interactive slider (₹150 to ₹3,500).
  - Veg-focused filter checkbox.
- **Visual Presentation**: Responsive cards displaying Zomato star ratings, AI Sentiment Scores, FSSAI compliance badges, opening hours, and a direct `'Deep Dive'` navigation trigger.

### Page 2: 🏛️ Restaurant Deep Dive & Submit Review
- **Primary Function**: Comprehensive single-restaurant profile audit and live review ingestion.
- **Analytical Modules**:
  - Metadata header displaying physical location, operational hours, cost, and verified FSSAI licence number.
  - Interactive **Plotly 5-Axis Radar Chart** visualizing the restaurant's operational strengths and weaknesses across Food, Service, Hygiene, Ambience, and Price.
  - Dynamic progress bars showing the ratio of Positive, Neutral, and Negative historical reviews.
  - Paginated review log filtered into All, Live Submissions, and Historical Dataset.
- **Live Submission Center**: Users input a reviewer name, star rating (1–5), and text review. Upon submission:
  1. The review is normalized via `clean_text()`.
  2. Sentiment polarity and confidence are inferred via the trained pipeline.
  3. Aspect clauses are extracted via the ABSA engine.
  4. The record is committed to SQLite (`data/reviews.db`).
  5. The UI recalculates the restaurant's live metrics immediately without a server restart.

### Page 3: 🎯 Contextual Dining Recommendations
- **Primary Function**: Context-driven recommendation engine eliminating demographic stereotyping.
- **Input Selections**:
  - Dining Occasion: *Family Outing (Kids & Family Friendly), Students / Budget Hangout, Romantic Date Night, Large Group Party / Late Night, Solo Dining*.
  - Target Neighbourhood.
  - Maximum Budget ceiling.
  - Mandatory verified safety compliance filter.
- **Output**: Ranked recommendation cards displaying the composite match score, cost, Zomato rating, and a detailed mathematical breakdown card showing exact contributions from Sentiment (50%), Zomato (25%), Safety (15%), and Context (10%).

### Page 4: ⚖️ Side-by-Side Compare
- **Primary Function**: Comparative multi-establishment evaluation workbench.
- **Workflow**:
  - User selects 2 or 3 Kolkata restaurants via `st.multiselect`.
  - The engine generates an overlaid **Multi-Trace Radar Chart** directly contrasting the restaurants' performance across all 5 ABSA aspects.
  - Below the chart, a comparison matrix compares Average Cost, Zomato Rating, AI Sentiment Score, Verified Safety Score, and Total Reviews Analyzed.

### Page 5: 🛡️ Food Safety & Hygiene Surveillance
- **Primary Function**: Public health early-warning audit scanner mapping unstructured consumer reviews to municipal health code violation risks.
- **Inspiration & Lineage**: Implements smart inspection methodologies from the **CDC / NYC Department of Health (Harrison et al.)** and **Harvard Business School (Glaeser et al.)**.
- **Violation Taxonomies Scanned**:
  1. *Pest Control Lapses* (cockroaches, rats, insects)
  2. *Cooking Oil Reuse* (black oil, rancid smell, reused frying oil)
  3. *Cold Storage Temperature* (warm chicken, melted dairy)
  4. *Drinking Water Quality* (unfiltered tap water, foul ice)
  5. *Utensil Hygiene* (greasy plates, unwashed glasses)
  6. *Improper Waste Disposal* (overflowing garbage bins near dining)
  7. *Staff Personal Hygiene* (coughing, unwashed hands, no hairnets)
  8. *Misleading Labelling / Stale Storage* (expired sauces, unlabelled meat)
- **Biological Illness Markers**: Scans for acute foodborne illness keywords (*vomiting, acute diarrhea, food poisoning, cramps, hospitalization*).
- **Outputs**:
  - Risk Penalty Score ($0$ to $100$).
  - Identified health code violations list.
  - **Municipal Inspection Priority Level**:
    - **CRITICAL PRIORITY**: Immediate 24–48 hour municipal inspection required; acute bio-hazard flagged.
    - **HIGH PRIORITY**: Re-inspection required within 7 days.
    - **MEDIUM PRIORITY**: Routine compliance verification.
    - **LOW / SAFE**: Normal compliance.

### Page 6: ✳️ Sentiment & Aspect Studio
- **Primary Function**: Real-time single-review NLP testing playground.
- **Features**:
  - Review input box with pre-loaded stress-test cases.
  - Instant classification into Positive, Neutral, or Negative with confidence percentage.
  - Interactive probability distribution bar chart showing exact probabilities for each class.
  - Sentence-level ABSA breakdown highlighting which specific phrases correspond to Food, Service, Hygiene, Ambience, or Price, along with polarity badges.

### Page 7: ▦ Batch Intelligence Center
- **Primary Function**: Bulk processing portal for enterprise restaurant chains and municipal health authorities.
- **Capabilities**:
  - Upload custom CSV files containing thousands of reviews, or load a pre-compiled 500-review synthetic batch.
  - Streamlined batch execution: runs text cleaning, sentiment classification, ABSA extraction, and public health risk tagging across all rows simultaneously.
  - KPI summary dashboard displaying Total Reviews, Sentiment Ratios, and Total Health Red Flags.
  - Dedicated **Alerts Table** isolating only the high-risk reviews flagged for food safety violations.
  - Instant **1-Click Export to CSV** downloading the enriched intelligence dataset.

### Page 8: 📊 Model Benchmark & Evaluation Lab
- **Primary Function**: Academic transparency laboratory presenting comparative empirical findings.
- **Features**:
  - Formatted performance table across 8 metrics (Accuracy, Macro Precision, Macro Recall, Macro F1, Weighted F1, Negative F1, Neutral F1, Positive F1).
  - Comparative bar charts illustrating model performance.
  - **Interactive Confusion Matrix Inspector**: Allows selecting any candidate classifier (Logistic Regression, Linear SVM, Naive Bayes) to view exact True vs. Predicted counts and analyze off-diagonal errors.

### Page 9: 📖 Methodology & Architecture
- **Primary Function**: Academic model card and system architecture documentation.
- **Content**:
  - Full documentation of the 4-layer utility formula.
  - Mathematical description of the NLP pipeline, tokenization, sublinear TF-IDF, and balanced loss functions.
  - Ethical governance protocols: strict elimination of demographic bias, zero synthetic data hallucination for uninspected establishments, and privacy preservation.
  - Comprehensive roadmap for transitioning from Minor Project to Major Project (Transformer fine-tuning with RoBERTa, Bengali-English code-mixed NLP, and live KMC municipal API integration).
