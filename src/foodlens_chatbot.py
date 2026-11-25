"""Interactive Conversational AI Assistant for ACOS FoodLens.

Provides intelligent natural language interaction across 5 core capabilities:
1. Review Parsing & ACOS Quadruple Extraction (Aspect, Category, Opinion, Sentiment, SDP)
2. Kolkata Restaurant Search & Recommendation (Cuisine, Zone, Price, Occasion)
3. Specific Restaurant Deep-Dive & Verified FSSAI Hygiene Audit Inquiries
4. Food Safety Surveillance & Health Violation Warnings
5. Academic Methodology, Research Architecture, & Technical Q&A

Team Members: Tanim Naha, Srilekha, Subhamita, Yashamoti
Faculty Guide: Dr. Saberi Goswami
Amity School of Engineering & Technology, Amity University Kolkata
"""

from __future__ import annotations
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from src.acos_pipeline import ACOSPipeline
from src.safety_engine import SafetyEngine
from src.recommendation import RecommendationEngine

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "kolkata_dataset"


class FoodLensChatbotEngine:
    def __init__(self):
        self.pipeline = ACOSPipeline()
        self.safety_engine = SafetyEngine()
        self.rec_engine = RecommendationEngine()
        
        # Load restaurant corpora
        rest_path = DATA_DIR / "restaurants.csv"
        if rest_path.exists():
            self.restaurants_df = pd.read_csv(rest_path)
        else:
            self.restaurants_df = pd.DataFrame()

        rev_path = DATA_DIR / "reviews_kolkata.csv"
        if rev_path.exists():
            self.reviews_df = pd.read_csv(rev_path)
        else:
            self.reviews_df = pd.DataFrame()

        safe_path = DATA_DIR / "safety_records.csv"
        if safe_path.exists():
            self.safety_df = pd.read_csv(safe_path)
        else:
            self.safety_df = pd.DataFrame()

    def respond(self, user_msg: str) -> str:
        """Processes user input message and returns natural markdown response."""
        msg = user_msg.strip()
        msg_lower = msg.lower()

        # 1. Check for Academic / Methodology / Architecture / Dataset Queries
        academic_res = self._handle_academic_queries(msg_lower)
        if academic_res:
            return academic_res

        # 2. Check for Explicit Review Analysis Intent
        if self._is_review_analysis_query(msg, msg_lower):
            return self._handle_review_analysis(msg)

        # 3. Check for Restaurant Comparison Queries (e.g. "Compare Arsalan and Peter Cat")
        comp_res = self._handle_comparison_query(msg_lower)
        if comp_res:
            return comp_res

        # 4. Check for Specific Restaurant Name Queries (handles e.g. "Arsalan's food safety score")
        specific_rest_res = self._handle_specific_restaurant(msg_lower)
        if specific_rest_res:
            return specific_rest_res

        # 5. Check for General Food Safety / Hygiene Inquiries
        safety_res = self._handle_food_safety_queries(msg_lower)
        if safety_res:
            return safety_res

        # 6. Check for Restaurant Recommendations & General Dining Queries
        rec_res = self._handle_recommendations(msg_lower)
        if rec_res:
            return rec_res

        # 7. Greeting / Help Fallback
        if any(w in msg_lower for w in ["hi", "hello", "hey", "help", "who are you", "what can you do"]):
            return self._get_welcome_message()

        # Default intelligent response
        return self._handle_fallback_review_check(msg)

    def _is_review_analysis_query(self, msg: str, msg_lower: str) -> bool:
        """Determines if the user wants a review parsed."""
        trigger_prefixes = ["analyze", "evaluate", "parse", "check this review", "review:", "quadruple", "extract:"]
        if any(msg_lower.startswith(p) for p in trigger_prefixes):
            return True
        # Do not treat direct questions as customer reviews
        question_starters = ("what ", "how ", "why ", "who ", "which ", "where ", "when ", "can ", "could ", "do ", "does ", "is ", "are ", "compare ", "list ", "show ", "tell me ")
        if msg_lower.endswith("?") or msg_lower.startswith(question_starters):
            return False
        # If text has multiple dining words and looks like a statement, treat as review
        culinary_indicators = ["biryani", "food", "waiter", "staff", "service", "ambience", "decor",
                               "chicken", "kebab", "mutton", "bill", "table", "clean", "hygiene",
                               "taste", "delicious", "terrible", "bad", "slow", "oily", "overpriced",
                               "seafood", "platter", "toilet", "prawn", "roti", "pocket"]
        found_indicators = sum(1 for w in culinary_indicators if w in msg_lower)
        if found_indicators >= 2 and len(msg.split()) >= 5:
            return True
        return False

    def _handle_review_analysis(self, msg: str) -> str:
        """Runs ACOS extraction and formats a structured response."""
        # Clean prefix if present (e.g. 'Analyze review:', 'Analyze:', 'review:')
        clean_text = re.sub(r"^(?:analyze|evaluate|parse|check(?:\s+this)?\s+review|review)\s*(?:review)?\s*[:\-\s]*", "", msg, flags=re.I).strip()
        if not clean_text:
            clean_text = msg

        quads = self.pipeline.extract_quadruples(clean_text)
        
        # Check Polarity Blindness
        sentiments = [q["sentiment"] for q in quads]
        has_pos = "positive" in sentiments
        has_neg = "negative" in sentiments
        is_polar_blind = has_pos and has_neg

        res = [f"### 🔬 Syntax-Aware ACOS Analysis\n"]
        res.append(f"**Target Review Snippet:** *\"{clean_text}\"*\n")

        if is_polar_blind:
            res.append(
                "> 💡 **Polarity Blindness Averted:** This review contains opposing sentiments. "
                "A traditional coarse classifier would compress this into **Neutral**, hiding both culinary excellence "
                "and service/hygiene failure. Our syntax-aware engine isolated both distinct polarities!\n"
            )

        if not quads:
            res.append("No explicit or implicit aspect quadruples could be reliably identified in this sentence.")
            return "\n".join(res)

        res.append(f"**Identified {len(quads)} Aspect Quadruple(s) $\\langle a, c, o, s, \\tau \\rangle$:**\n")
        for i, q in enumerate(quads, 1):
            pol_emoji = "🟢 Positive" if q["sentiment"] == "positive" else ("🔴 Negative" if q["sentiment"] == "negative" else "🟡 Neutral")
            typ_str = f"**{q['type'].upper()}** ({q.get('archetype', 'syntax')})"
            
            res.append(f"#### Quadruple #{i}: `{q['aspect']}` [{pol_emoji}]")
            res.append(f"- **Aspect Target ($a$):** `{q['aspect']}`")
            res.append(f"- **Culinary Category ($c$):** `{q['category']}`")
            res.append(f"- **Opinion Expression ($o$):** *\"{q['opinion']}\"*")
            res.append(f"- **Sentiment Polarity ($s$):** {pol_emoji}")
            res.append(f"- **Typology ($\\tau$):** {typ_str}")
            res.append(f"- **Shortest Dependency Path:** `{q.get('syntactic_path', 'N/A')}`")
            res.append(f"- **Explanation:** {q.get('explanation', '')} *(Confidence: {q.get('confidence', 0.90)*100:.1f}%)*\n")

        res.append("---")
        res.append("*(You can also test this in the **'Syntax-Aware ACOS Studio'** tab to view the live SVG dependency tree!)*")
        return "\n".join(res)

    def _handle_specific_restaurant(self, msg_lower: str) -> Optional[str]:
        """Looks up a specific restaurant by name."""
        if self.restaurants_df.empty:
            return None

        # Clean words
        target_name = None
        for name in self.restaurants_df["name"].dropna().unique():
            if name.lower() in msg_lower or (len(name) > 4 and name.lower() in msg_lower.replace("'", "")):
                target_name = name
                break

        if not target_name:
            return None

        row = self.restaurants_df[self.restaurants_df["name"] == target_name].iloc[0]
        r_id = str(row["restaurant_id"])
        neighbourhood = row.get("neighbourhood", "Kolkata")
        cuisines = row.get("cuisines", row.get("primary_cuisine", "Multi-cuisine"))
        cost = row.get("cost_for_two_inr", "N/A")
        rating = row.get("zomato_rating", "N/A")
        safety_score = row.get("safety_score_0_100", None)

        # Lookup safety record
        safety_res = self.safety_engine.calculate_score(r_id)
        outcome = safety_res.get("outcome", "No record")
        licence = safety_res.get("licence_status", "N/A")
        violations = safety_res.get("violations_noted", [])

        res = [f"### 🏛️ Restaurant Profile: **{target_name}**\n"]
        res.append(f"- **Location / Zone:** {neighbourhood}")
        res.append(f"- **Cuisines:** {cuisines}")
        res.append(f"- **Cost for Two:** ₹{cost}")
        res.append(f"- **Zomato Community Rating:** ⭐ {rating} / 5.0")
        
        if pd.notna(safety_score) and safety_res.get("safety_score") is not None:
            s_val = safety_res["safety_score"]
            s_badge = "🟢 Compliant" if s_val >= 70 else ("🟡 Moderate Risk" if s_val >= 50 else "🔴 Critical Risk")
            res.append(f"- **Verified Municipal Safety Score:** **{s_val:.1f} / 100** ({s_badge})")
            res.append(f"- **Inspection Outcome:** `{outcome}` (FSSAI Licence: `{licence}`)")
            if violations:
                res.append(f"- **Recorded Violations:** {', '.join([v.replace('_', ' ').capitalize() for v in violations])}")
        else:
            res.append(f"- **Municipal Safety Score:** *Safety data unavailable (No FSSAI inspection record on file)*")

        res.append(f"\n*(To submit a review or view aspect breakdown, switch to **'Restaurant Deep Dive'** and select **{target_name}**!)*")
        return "\n".join(res)

    def _handle_comparison_query(self, msg_lower: str) -> Optional[str]:
        """Compares two restaurants side-by-side when both names appear in the prompt."""
        if self.restaurants_df.empty:
            return None
        if not any(w in msg_lower for w in ["compare", " vs ", "versus", "better", "difference"]):
            return None

        matched_rows = []
        for name in self.restaurants_df["name"].dropna().unique():
            if name.lower() in msg_lower:
                matched_rows.append(self.restaurants_df[self.restaurants_df["name"] == name].iloc[0])
            if len(matched_rows) >= 2:
                break

        if len(matched_rows) < 2:
            return None

        r1, r2 = matched_rows[0], matched_rows[1]
        s1 = self.safety_engine.calculate_score(str(r1["restaurant_id"])).get("safety_score")
        s2 = self.safety_engine.calculate_score(str(r2["restaurant_id"])).get("safety_score")
        s1_str = f"{s1:.1f}/100" if s1 is not None else "Unavailable"
        s2_str = f"{s2:.1f}/100" if s2 is not None else "Unavailable"

        return (
            f"### ⚖️ Side-by-Side Comparison: **{r1['name']}** vs. **{r2['name']}**\n\n"
            f"| Metric | **{r1['name']}** | **{r2['name']}** |\n"
            f"| :--- | :---: | :---: |\n"
            f"| **Neighbourhood** | {r1.get('neighbourhood', 'Kolkata')} | {r2.get('neighbourhood', 'Kolkata')} |\n"
            f"| **Primary Cuisine** | {r1.get('primary_cuisine', 'N/A')} | {r2.get('primary_cuisine', 'N/A')} |\n"
            f"| **Cost for Two** | ₹{r1.get('cost_for_two_inr', 'N/A')} | ₹{r2.get('cost_for_two_inr', 'N/A')} |\n"
            f"| **Zomato Rating** | ⭐ {r1.get('zomato_rating', 'N/A')} | ⭐ {r2.get('zomato_rating', 'N/A')} |\n"
            f"| **Municipal Safety** | 🛡️ **{s1_str}** | 🛡️ **{s2_str}** |\n\n"
            "*(Open the **'Side-by-Side Compare'** tab for aspect radar charts!)*"
        )

    def _handle_recommendations(self, msg_lower: str) -> Optional[str]:
        """Provides context-aware restaurant recommendations."""
        is_rec_query = any(w in msg_lower for w in [
            "recommend", "best", "where to eat", "find", "top", "suggest",
            "places for", "restaurants", "good place", "highest rated",
            "cheapest", "budget", "vegetarian", "veg ", "list "
        ])
        if not is_rec_query or self.restaurants_df.empty:
            return None

        # Filter by cuisine with domain-aware culinary mappings
        df = self.restaurants_df.copy()
        cuisine_match = None
        
        cuisine_keywords = {
            "biryani": ["biryani", "mughlai", "kebab", "north indian"],
            "chinese": ["chinese", "asian", "tibetan", "momo"],
            "bengali": ["bengali", "fish", "seafood"],
            "north indian": ["north indian", "mughlai", "kebab", "tandoor"],
            "continental": ["continental", "cafe", "italian", "pizza"],
            "rolls": ["rolls", "roll", "fast food", "street food"],
            "dessert": ["dessert", "mishti", "bakery", "sweet"]
        }

        for c_label, kw_list in cuisine_keywords.items():
            if c_label in msg_lower or any(kw in msg_lower for kw in kw_list if len(kw) > 4):
                cuisine_match = c_label.capitalize()
                pattern = "|".join(kw_list)
                filtered = df[
                    df["cuisines"].str.contains(pattern, case=False, na=False) |
                    df["primary_cuisine"].str.contains(pattern, case=False, na=False) |
                    df["name"].str.contains(pattern, case=False, na=False)
                ]
                if not filtered.empty:
                    df = filtered
                break

        # Filter by zone / neighbourhood
        zone_match = None
        for z in ["park street", "salt lake", "new town", "ballygunge", "gariahat", "esplanade", "dum dum", "south kolkata", "camac street"]:
            if z in msg_lower:
                zone_match = z.title()
                zone_filtered = df[df["neighbourhood"].str.contains(z.replace(" city", ""), case=False, na=False)]
                if not zone_filtered.empty:
                    df = zone_filtered
                break

        # Filter by budget
        budget_match = None
        if any(w in msg_lower for w in ["budget", "cheap", "inexpensive", "student", "under 500", "under 600"]):
            budget_match = "Budget (< ₹600)"
            budget_filtered = df[df["cost_for_two_inr"] <= 600]
            if not budget_filtered.empty:
                df = budget_filtered

        # Sort by rating and safety score
        df = df.copy()
        df["combined_rank"] = df["zomato_rating"].fillna(3.5) * 10 + df["safety_score_0_100"].fillna(50) * 0.5
        top_picks = df.sort_values("combined_rank", ascending=False).head(4)

        heading_parts = ["Top Dining Recommendations"]
        if cuisine_match:
            heading_parts.append(f"for **{cuisine_match}**")
        if zone_match:
            heading_parts.append(f"in **{zone_match}**")
        if budget_match:
            heading_parts.append(f"({budget_match})")

        res = [f"### 🎯 {' '.join(heading_parts)}\n"]
        for _, r in top_picks.iterrows():
            name = r["name"]
            zone = r.get("neighbourhood", "Kolkata")
            cuis = r.get("primary_cuisine", "Multi-cuisine")
            cost = r.get("cost_for_two_inr", "N/A")
            rating = r.get("zomato_rating", "N/A")
            safety = r.get("safety_score_0_100", None)
            safety_str = f"Safety: {safety:.0f}/100" if pd.notna(safety) else "Safety: Unverified"

            res.append(f"1. **{name}** ({zone})")
            res.append(f"   - **Cuisine:** {cuis}  |  **Cost for Two:** ₹{cost}")
            res.append(f"   - **Rating:** ⭐ {rating}  |  🛡️ **{safety_str}**\n")

        res.append("*(You can view full multi-criteria aspect scores in the **'Contextual Dining Recommendations'** tab!)*")
        return "\n".join(res)

    def _handle_food_safety_queries(self, msg_lower: str) -> Optional[str]:
        """Handles hygiene, food safety, and violation queries."""
        safety_words = ["hygiene", "food safety", "violations", "fssai", "inspection", "cockroach", "illness", "unsafe", "poisoning"]
        if not any(w in msg_lower for w in safety_words):
            return None

        if "how" in msg_lower and ("score" in msg_lower or "calculate" in msg_lower or "formula" in msg_lower):
            return (
                "### 🛡️ Verified Food Safety Scoring Formula (0–100 Scale)\n\n"
                "Our platform calculates an objective food hygiene compliance score directly from official municipal inspection audits:\n\n"
                "$$\\text{Verified Safety Score} = \\text{Outcome (40 pts)} + \\text{Licence (30 pts)} + \\text{Violation Penalty (20 pts)} + \\text{Recency (10 pts)}$$\n\n"
                "- **Inspection Outcome (40 pts):** Satisfactory = 40, Needs Improvement = 20, Major Violations = 5.\n"
                "- **Licence Status (30 pts):** Active = 30, Renewal Due = 15, Suspended = 0.\n"
                "- **Violation Deductions (20 pts):** -8 for pest control lapses, -8 for cooking oil reuse, -6 for cold storage failures, -5 for drinking water quality.\n"
                "- **Recency (10 pts):** $\\le 6$ months = 10 pts, 6–12 months = 7 pts, $> 24$ months = 2 pts.\n\n"
                "> ⚠️ **Strict Non-Fabrication Rule:** If a restaurant has no verified inspection record on file, "
                "the system displays **'Safety data unavailable'** to prevent subjective or fabricated ratings."
            )

        if not self.safety_df.empty:
            flagged = self.safety_df[self.safety_df["outcome"].isin(["Needs Improvement", "Major Violations"])].head(4)
            res = ["### 🚨 Food Safety & Public Health Surveillance Alerts\n"]
            res.append("The following establishments were identified with recorded sanitation compliance violations in municipal inspection logs:\n")
            
            for _, s in flagged.iterrows():
                r_id = s["restaurant_id"]
                r_name = r_id
                if not self.restaurants_df.empty:
                    m = self.restaurants_df[self.restaurants_df["restaurant_id"] == r_id]
                    if not m.empty:
                        r_name = m.iloc[0]["name"]
                
                outcome = s.get("outcome", "Violation")
                date = str(s.get("inspection_date", ""))[:10]
                viols = str(s.get("violations_noted", "general")).replace("_", " ").split(";")
                res.append(f"- **{r_name}**: Outcome: `{outcome}` ({date})")
                res.append(f"  *Issues noted:* {', '.join(viols)}")

            res.append("\n*(Check the **'Food Safety & Hygiene Surveillance'** tab for full early-warning disease monitoring!)*")
            return "\n".join(res)

        return None

    def _handle_academic_queries(self, msg_lower: str) -> Optional[str]:
        """Provides answers to technical, academic, and supervisor questions."""
        # Faculty Guide
        if any(w in msg_lower for w in ["guide", "supervisor", "faculty", "mentor", "saberi", "goswami"]):
            return (
                "### 🎓 Academic Supervision & Credits\n\n"
                "- **Faculty Guide:** **Dr. Saberi Goswami**, Faculty Guide\n"
                "- **Department:** Department of Computer Science & Engineering, Amity School of Engineering & Technology (ASET)\n"
                "- **Institution:** Amity University, Kolkata, West Bengal, India\n"
                "- **Team Members:** **Tanim Naha, Srilekha, Subhamita, Yashamoti** (7th Semester B.Tech CSE, Course: Minor Project ETMN100)\n"
                "- **Project Title:** *'Beyond Polarity: Syntax-Aware Deep Aspect Quadruple Mining and Implicit Opinion Disentanglement in Online Food Reviews'*"
            )

        # What is ACOS / Polarity Blindness
        if "polarity blindness" in msg_lower:
            return (
                "### 💡 What is Polarity Blindness?\n\n"
                "**Polarity Blindness** occurs when a standard sentiment analyzer assigns a single document-level label "
                "(Positive/Neutral/Negative) to compound reviews containing opposing aspect polarities.\n\n"
                "**Example:**\n"
                "> *\"The mutton biryani was fragrant, but the waiter was extremely rude.\"*\n\n"
                "- Traditional sentiment models compute $+1$ (biryani) and $-1$ (waiter) $\\rightarrow$ **Neutral**.\n"
                "- This obscures both the culinary quality and the service failure.\n"
                "- Our **Syntax-Aware ACOS Engine** resolves this by extracting independent 5-tuples: "
                "`[mutton biryani, FOOD#QUALITY, fragrant, positive]` and `[waiter, SERVICE#GENERAL, extremely rude, negative]`."
            )

        if "acos" in msg_lower or "quadruple" in msg_lower or "5-tuple" in msg_lower or "formulation" in msg_lower:
            return (
                "### 📐 Aspect-Category-Opinion-Sentiment (ACOS) Formulation\n\n"
                "We formalize sentiment extraction as mining structured 5-tuples:\n"
                "$$\\mathcal{Q} = \\langle a, c, o, s, \\tau \\rangle$$\n\n"
                "1. **$a$ (Aspect Target):** Explicit entity or implicit target (`mutton biryani`, `server`, `washroom`).\n"
                "2. **$c$ (Category):** One of 9 structured culinary dimensions (`FOOD#QUALITY`, `FOOD#PRICES`, `FOOD#STYLE_OPTIONS`, `SERVICE#GENERAL`, `SERVICE#PROMPTNESS`, `AMBIENCE#GENERAL`, `RESTAURANT#PRICES`, `HYGIENE#CLEANLINESS`, `HYGIENE#FOOD_SAFETY`).\n"
                "3. **$o$ (Opinion Span):** Verbatim evaluative phrase (`fragrant and tender`, `cost an arm and a leg`).\n"
                "4. **$s$ (Sentiment Polarity):** $s \\in \\{\\text{positive}, \\text{neutral}, \\text{negative}\\}$.\n"
                "5. **$\\tau$ (Typology):** $\\tau \\in \\{\\text{explicit}, \\text{implicit}\\}$ indicating the opinion mechanism."
            )

        if "shortest dependency path" in msg_lower or "sdp" in msg_lower or "syntax" in msg_lower:
            return (
                "### 🌳 Shortest Dependency Path (SDP) & Dependency Graphs\n\n"
                "- Rather than relying on arbitrary linear word distance (which confuses distant words), our engine converts sentences into **directed NetworkX dependency trees**.\n"
                "- **Shortest Dependency Path (SDP)** calculates the minimum graph geodesic distance between aspect candidate nouns and opinion adjectives.\n"
                "- **Advantage:** Correctly resolves long-distance copular relations (*nsubj -> AUX -> acomp*) across 8+ tokens without degradation, and traverses `neg` child edges to handle inverted polarity.\n"
                "- **Empirical Benefit:** Contributed a **+4.5% F1 gain** and a **+9.87% Precision gain** in our ablation study."
            )

        if "implicit" in msg_lower or "archetype" in msg_lower:
            return (
                "### 🎭 The 5 Implicit Opinion Archetypes\n\n"
                "When customers communicate strong sentiment without explicit adjectives, our Implicit Disentanglement Engine identifies 5 distinct archetypes:\n\n"
                "1. **Metaphorical Financial Distress:** *\"Burned a massive hole in my pocket\"* $\\rightarrow$ `FOOD#PRICES` (Negative)\n"
                "2. **Biological & Sanitary Symptoms:** *\"Spent the night hugging the toilet bowl\"* $\\rightarrow$ `HYGIENE#FOOD_SAFETY` (Negative)\n"
                "3. **Factual Temporal Delays:** *\"Finished two podcasts before food arrived\"* $\\rightarrow$ `SERVICE#PROMPTNESS` (Negative)\n"
                "4. **Portion Size Disparities:** *\"Contained only one tiny potato and barely fed a pigeon\"* $\\rightarrow$ `FOOD#PRICES` (Negative)\n"
                "5. **Sensory Texture Metaphors:** *\"Melted like butter the moment it touched the tongue\"* $\\rightarrow$ `FOOD#QUALITY` (Positive)\n\n"
                "> 📈 **Ablation Gain:** Enabled a **+41.3% absolute gain in implicit opinion recovery** (50.0% vs. 8.70% baseline)."
            )

        if "benchmark" in msg_lower or "result" in msg_lower or "f1" in msg_lower or "ablation" in msg_lower:
            return (
                "### 📊 Empirical Benchmark & Ablation Study Results\n\n"
                "Evaluated on held-out test split (`test.jsonl`, 150 instances, 502 quadruples across 9 categories under exact quadruple matching):\n\n"
                "| Configuration | Quadruple Precision | Quadruple Recall | **Quadruple F1** | Explicit F1 | **Implicit F1** |\n"
                "| :--- | :---: | :---: | :---: | :---: | :---: |\n"
                "| **Proposed (Syntax Graph + Disentangler)** | **64.45%** | **56.20%** | **60.04%** | **63.66%** | **50.00%** |\n"
                "| **Ablation A: w/o Dependency Syntax** | 54.58% | 56.61% | 55.58% | 60.70% | 40.32% |\n"
                "| **Ablation B: w/o Implicit Disentangler** | 60.11% | 45.45% | 51.76% | 63.66% | 8.70% |\n\n"
                "- **Syntax Dependency Gain:** +4.46% F1, +9.87% Precision\n"
                "- **Implicit Disentangler Gain:** +41.30% Implicit F1"
            )

        if any(w in msg_lower for w in ["neural", "bilstm", "lstm", "pytorch", "architecture", "embedding", "attention", "model"]):
            return (
                "### 🧠 Deep Multi-Task Neural Architecture (`SyntaxAwareACOSNet`)\n\n"
                "Our deep neural model combines syntactic structure with multi-task representation learning:\n\n"
                "1. **Multi-Channel Input:** Fuses Word, POS tag, and Dependency relation embeddings ($d=192$).\n"
                "2. **2-Layer Bidirectional LSTM:** Encodes sequential left/right review context ($h=128$).\n"
                "3. **Graph-Guided Self-Attention:** Masks multi-head attention using the NetworkX dependency adjacency matrix so attention strictly follows grammatical arcs.\n"
                "4. **5 Joint Prediction Heads:** Aspect BIO, Opinion BIO, 9-Class Category, 3-Class Sentiment, and Binary Implicit/Explicit flag.\n"
                "5. **Hardware & Performance:** Trained on Apple Silicon MPS (`syntax_acos_model.pt`), achieving **100% validation accuracy** and sub-2ms inference."
            )

        if any(w in msg_lower for w in ["dataset", "corpus", "categories", "split", "how many"]):
            return (
                "### 📚 Benchmark Corpus & Kolkata Directory\n\n"
                "- **ACOS Verbatim Benchmark (`data/acos_dataset/`):** **1,000 curated reviews** (700 Train / 150 Val / 150 Test) with **1,560 verbatim quadruples** (931 explicit, 629 implicit) across **9 culinary categories**.\n"
                "- **Kolkata Restaurant Directory:** **100 real Zomato-listed restaurants** across Park Street, Salt Lake, Ballygunge, Gariahat, Esplanade, and South Kolkata.\n"
                "- **Municipal FSSAI Audit Logs:** **107 inspection records** covering 84 establishments, with strict zero-fabrication for unverified listings."
            )

        if any(w in msg_lower for w in ["future", "major project", "roadmap", "next"]):
            return (
                "### 🚀 Future Roadmap Towards Major Project\n\n"
                "1. **Graph Neural Networks (GCN / GAT):** Upgrade syntactic attention to multi-hop relational message passing over dependency trees.\n"
                "2. **Code-Mixed Bengali NLP (Banglish):** Fine-tune IndicBERT/BanglaBERT on Romanized Bengali food reviews.\n"
                "3. **LLM Knowledge Distillation:** Distill Llama-3/Mistral into compact edge student models for sub-15ms mobile inference.\n"
                "4. **Civic Health Alerts:** Route critical `HYGIENE#FOOD_SAFETY` quadruples directly to KMC/FSSAI health desks."
            )

        return None

    def _get_welcome_message(self) -> str:
        return (
            "### 👋 Hello! I am your ACOS FoodLens Dining Intelligence Assistant!\n\n"
            "I can assist you across both practical dining discovery and our academic research:\n\n"
            "1. **🔍 Review Parsing & ACOS Quadruple Extraction**: Paste any review to extract Aspect, Category, Opinion, Sentiment, and Shortest Dependency Paths.\n"
            "2. **🍽️ Restaurant Recommendations & Comparisons**: Ask for top biryani spots, compare two restaurants, or filter by budget.\n"
            "3. **🛡️ Municipal Food Safety Inquiries**: Look up verified FSSAI hygiene audit scores, inspection outcomes, and violation histories.\n"
            "4. **🎓 Academic Methodology Q&A**: Ask about polarity blindness, `SyntaxAwareACOSNet`, our 9 culinary categories, ablation results, or supervisor **Dr. Saberi Goswami**.\n\n"
            "**Try asking me:**\n"
            "- *\"Analyze this review: The mutton biryani was tender, but the waiter was rude.\"*\n"
            "- *\"Compare Arsalan and Peter Cat\"*\n"
            "- *\"Explain how the neural network architecture works\"*"
        )

    def _handle_fallback_review_check(self, msg: str) -> str:
        """If user sends a review statement, analyze it; if it's an unrecognized question, guide them helpfully."""
        msg_lower = msg.lower().strip()
        question_starters = ("what ", "how ", "why ", "who ", "which ", "where ", "when ", "can ", "could ", "do ", "does ", "is ", "are ", "compare ", "list ", "show ", "tell me ")
        if msg_lower.endswith("?") or msg_lower.startswith(question_starters):
            return (
                f"I'd love to help with *\"{msg}\"*! Here is how you can ask me so I can fetch the exact answer:\n\n"
                "- **For Dining Discovery:** *\"Recommend top biryani in Park Street\"* or *\"Compare Arsalan and Peter Cat\"*\n"
                "- **For Restaurant Profiles:** *\"Tell me about Mocambo\"* or *\"How is Arsalan's food safety score?\"*\n"
                "- **For Review Analysis:** Start with **`Analyze:`** followed by any review (e.g., *\"Analyze: The biryani was cold and the waiter ignored us.\"*)\n"
                "- **For Research & Viva Q&A:** Ask about **ACOS**, **polarity blindness**, **Shortest Dependency Path**, **implicit archetypes**, **neural network**, **dataset**, **benchmark results**, or **faculty guide**."
            )
        if len(msg.split()) >= 4:
            return self._handle_review_analysis(msg)
        return self._get_welcome_message()
