# -*- coding: utf-8 -*-
"""Kolkata FoodLens & Food Review Intelligence - Master Unified Platform.

Combines:
1. Kolkata 100 Restaurants Browsable Directory & Search
2. Restaurant Deep Dive, Dynamic Re-scoring, & Live SQLite Review Submission
3. Context-Based Recommendations (Families, Students, Couples, Groups, Solo Diners)
4. Side-by-Side Restaurant Comparison with Aspect Radar Overlays
5. Public Health Food Safety & Hygiene Surveillance (Early Warning Engine for West Bengal)
6. Sentiment & Aspect Studio (Single Review Real-time Inference & Probabilities)
7. Batch Intelligence Center (Bulk Processing, Hygiene Risk Flagging, CSV Export)
8. Model Benchmark & Evaluation Lab (Metrics Comparison & Confusion Matrices)
9. Methodology, Architecture, & Academic Model Card
"""

from __future__ import annotations
import io
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Setup module search paths
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "models"))

from src.db import get_all_user_reviews, get_user_reviews, init_db, save_user_review
from models.sentiment_model.inference import predict_sentiment
from models.absa_model.predict_aspects import predict_aspects
from src.safety_engine import SafetyEngine
from src.recommendation import RecommendationEngine

# Page configuration
st.set_page_config(
    page_title="Kolkata FoodLens | Master Intelligence Dashboard",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)

def render_html(html_str: str) -> None:
    """Render raw HTML safely using st.html and textwrap.dedent without markdown code block interference."""
    st.html(textwrap.dedent(html_str).strip())

# Custom CSS Styling
render_html("""
<style>
    :root {
        --primary: #0F766E;
        --primary-light: #CCFBF1;
        --secondary: #1E293B;
        --accent: #F59E0B;
        --bg: #F8FAFC;
        --surface: #FFFFFF;
        --border: #E2E8F0;
        --text-main: #0F172A;
        --text-muted: #64748B;
        --danger: #EF4444;
        --success: #10B981;
    }

    .stApp {
        background-color: var(--bg);
        color: var(--text-main);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0F766E 0%, #115E59 40%, #042F2E 100%);
        color: white;
        padding: 2.2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 25px -5px rgba(15, 118, 110, 0.25);
    }
    .hero-title {
        font-size: 2.25rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0;
        color: #F0FDFA;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #CCFBF1;
        margin-top: 0.5rem;
        font-weight: 400;
        max-width: 860px;
        line-height: 1.55;
    }

    /* Metric Card styling */
    .metric-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: var(--text-main);
        line-height: 1.15;
    }
    .metric-subtitle {
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: 0.35rem;
    }

    /* Restaurant Card */
    .resto-card-inner {
        padding: 0.25rem 0.1rem;
    }
    .resto-name {
        font-size: 1.4rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .resto-sub {
        font-size: 0.88rem;
        color: #64748B;
        margin-bottom: 0.65rem;
    }

    /* Pills & Badges */
    .badge {
        display: inline-block;
        padding: 0.24rem 0.68rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 650;
        letter-spacing: 0.02em;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
    .badge-teal { background: #CCFBF1; color: #0F766E; }
    .badge-amber { background: #FEF3C7; color: #B45309; }
    .badge-rose { background: #FFE4E6; color: #BE123C; }
    .badge-gray { background: #F1F5F9; color: #475569; }
    .badge-indigo { background: #E0E7FF; color: #4338CA; }

    /* Score Block Triad */
    .score-triad {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.85rem;
        background: #F8FAFC;
        border-radius: 10px;
        padding: 0.95rem;
        margin-top: 0.85rem;
        margin-bottom: 0.85rem;
        border: 1px solid #EEF2F6;
    }
    .score-item {
        text-align: center;
    }
    .score-label {
        font-size: 0.72rem;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.04em;
    }
    .score-num {
        font-size: 1.3rem;
        font-weight: 800;
        margin-top: 0.15rem;
    }

    /* Section Header */
    .section-head {
        font-size: 1.45rem;
        font-weight: 800;
        color: #0F172A;
        margin-top: 0.5rem;
        margin-bottom: 0.85rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
</style>
""")

# Early Warning Food Safety Taxonomy (Informed by KMC/FSSAI Inspection Protocols)
FOOD_SAFETY_TRIGGERS = {
    "Critical Biological / Illness Hazard": [
        "food poisoning", "poisoning", "poisoned", "vomit", "vomiting", "vomited",
        "threw up", "throw up", "stomach ache", "stomach pain", "stomach cramps",
        "diarrhea", "diarrhoea", "nausea", "nauseous", "sick", "hospital", "doctor",
        "infection", "salmonella", "undercooked chicken", "undercooked meat", "raw chicken",
        "raw meat", "undercooked pork", "fever", "cramps"
    ],
    "Contamination, Spoilage & Pest Infestation": [
        "cockroach", "cockroaches", "roach", "roaches", "rat", "rats", "mouse", "mice",
        "hair", "insect", "insects", "bug", "bugs", "fly", "flies", "worm", "worms",
        "maggot", "maggots", "foreign object", "plastic", "glass", "mold", "mould",
        "moldy", "mouldy", "stale", "spoiled", "rotten", "foul smell", "smelly", "rancid",
        "adulterated", "bad smell", "expired", "stale oil", "burnt oil"
    ],
    "Kitchen Sanitation & Hygiene Violation": [
        "dirty table", "dirty utensils", "dirty plates", "dirty glasses", "unhygienic",
        "filthy", "disgusting", "dirty kitchen", "washroom", "toilet",
        "restroom", "stinky", "stained", "no gloves", "bare hands", "greasy",
        "smelly kitchen", "poor hygiene", "sanitation", "dustbin", "drain"
    ]
}

SAFETY_SAMPLE_REVIEWS = {
    "Biological Illness (Critical)": "Ordered the chicken biryani last night and woke up with severe food poisoning, nausea, and vomiting. The meat was undercooked and tasted stale.",
    "Pest & Spoilage (High)": "Found a dead cockroach inside the curry bowl! The fried fish also smelled like rancid, rotten oil. Completely unacceptable.",
    "Sanitation Violation (Moderate)": "The dining tables were sticky, dirty plates were left unwashed, and kitchen staff were handling food with bare hands right next to an open dustbin.",
    "Hygienic Dining (Compliant)": "Immaculate open kitchen, staff wearing proper hairnets and gloves, freshly prepared hot food, and very clean washrooms."
}

def scan_food_safety(text: str) -> Dict[str, Any]:
    lowered = text.lower()
    matches_by_cat = {}
    total_violations = 0
    for category, terms in FOOD_SAFETY_TRIGGERS.items():
        found = []
        for term in terms:
            if re.search(r"\b" + re.escape(term) + r"\b", lowered):
                found.append(term)
        if found:
            matches_by_cat[category] = sorted(list(set(found)))
            total_violations += len(found)

    if "Critical Biological / Illness Hazard" in matches_by_cat:
        severity = "Critical"
        badge_color = "#DC2626"
        bg_color = "#FEF2F2"
        border_color = "#F87171"
        rec = "URGENT MUNICIPAL ACTION: Potential foodborne illness cluster. Flag for priority physical health inspection."
    elif "Contamination, Spoilage & Pest Infestation" in matches_by_cat:
        severity = "High"
        badge_color = "#EA580C"
        bg_color = "#FFF7ED"
        border_color = "#FB923C"
        rec = "HIGH PRIORITY: Kitchen contamination / pest infestation. Food storage & ingredient freshness audit required."
    elif "Kitchen Sanitation & Hygiene Violation" in matches_by_cat:
        severity = "Moderate"
        badge_color = "#D97706"
        bg_color = "#FFFBEB"
        border_color = "#FCD34D"
        rec = "NOTICE: Sanitation & handling lapse. Premises hygiene and staff compliance check recommended."
    else:
        severity = "Low / None"
        badge_color = "#10B981"
        bg_color = "#F0FDF4"
        border_color = "#86EFAC"
        rec = "No immediate food safety hazard or health code violation indicators detected."

    return {
        "severity": severity,
        "is_flagged": len(matches_by_cat) > 0,
        "violations": matches_by_cat,
        "total_violations": total_violations,
        "badge_color": badge_color,
        "bg_color": bg_color,
        "border_color": border_color,
        "recommendation": rec
    }

# Data Loading with Caching
@st.cache_data(show_spinner=False)
def load_datasets():
    data_dir = ROOT / "data" / "kolkata_dataset"
    restaurants = pd.read_csv(data_dir / "restaurants.csv")
    reviews = pd.read_csv(data_dir / "reviews_kolkata.csv")
    safety = pd.read_csv(data_dir / "safety_records.csv")
    suitability = pd.read_csv(data_dir / "restaurant_suitability.csv")
    return restaurants, reviews, safety, suitability

@st.cache_resource(show_spinner=False)
def get_engines():
    safety_eng = SafetyEngine()
    rec_eng = RecommendationEngine()
    return safety_eng, rec_eng

# Initialize DB and Core Engines
init_db()
restaurants_df, reviews_df, safety_df, suitability_df = load_datasets()
safety_engine, rec_engine = get_engines()

# Helper: Compute Restaurant Live Customer Experience Score and Aspects
def get_restaurant_analytics(restaurant_id: str):
    hist_revs = reviews_df[reviews_df["restaurant_id"] == restaurant_id]
    user_revs = get_user_reviews(restaurant_id)
    total_reviews_count = len(hist_revs) + len(user_revs)
    
    pos_count = int((hist_revs["sentiment_label"].str.lower() == "positive").sum())
    neu_count = int((hist_revs["sentiment_label"].str.lower() == "neutral").sum())
    neg_count = int((hist_revs["sentiment_label"].str.lower() == "negative").sum())
    
    for ur in user_revs:
        lab = ur["sentiment_label"].lower()
        if lab == "positive":
            pos_count += 1
        elif lab == "neutral":
            neu_count += 1
        else:
            neg_count += 1
            
    if total_reviews_count > 0:
        cust_exp_score = round(((pos_count + 0.5 * neu_count) / total_reviews_count) * 100.0, 1)
    else:
        cust_exp_score = 50.0
        
    aspect_counts = {}
    for aspect in ["food", "service", "hygiene", "ambience", "price"]:
        col = f"sentiment_{aspect}"
        a_pos = int((hist_revs[col].str.lower() == "positive").sum())
        a_neu = int((hist_revs[col].str.lower() == "neutral").sum())
        a_neg = int((hist_revs[col].str.lower() == "negative").sum())
        
        for ur in user_revs:
            u_val = ur.get(col, "neutral").lower()
            if u_val == "positive":
                a_pos += 1
            elif u_val == "negative":
                a_neg += 1
            else:
                a_neu += 1
                
        a_tot = a_pos + a_neu + a_neg
        if a_tot > 0:
            aspect_score = round(((a_pos + 0.5 * a_neu) / a_tot) * 100, 1)
        else:
            aspect_score = 50.0
            
        aspect_counts[aspect] = {
            "score": aspect_score,
            "pos": a_pos,
            "neu": a_neu,
            "neg": a_neg,
            "total": a_tot
        }
        
    return {
        "cust_exp_score": cust_exp_score,
        "total_reviews": total_reviews_count,
        "pos_count": pos_count,
        "neu_count": neu_count,
        "neg_count": neg_count,
        "aspects": aspect_counts,
        "user_reviews": user_revs
    }

# Session State Initialization
if "current_page" not in st.session_state:
    st.session_state.current_page = "🔍 Kolkata Directory & Search"
if "selected_restaurant_id" not in st.session_state:
    st.session_state.selected_restaurant_id = "KOL0001"

# Sidebar Navigation
with st.sidebar:
    render_html("""
    <div style="display:flex; align-items:center; gap:0.65rem; margin-bottom:1.2rem;">
        <div style="background:#0F766E; color:white; width:38px; height:38px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.35rem; font-weight:800;">FL</div>
        <div>
            <div style="font-weight:800; font-size:1.1rem; color:#0F172A; letter-spacing:-0.02em;">Kolkata FoodLens</div>
            <div style="font-size:0.75rem; color:#64748B;">Unified Restaurant & NLP Intelligence</div>
        </div>
    </div>
    """)
    
    nav_options = [
        "🔍 Kolkata Directory & Search",
        "🏛️ Restaurant Deep Dive & Submit Review",
        "🎯 Contextual Dining Recommendations",
        "⚖️ Side-by-Side Compare",
        "🛡️ Food Safety & Hygiene Surveillance",
        "✳️ Sentiment & Aspect Studio",
        "▦ Batch Intelligence Center",
        "📊 Model Benchmark & Evaluation Lab",
        "📖 Methodology & Architecture"
    ]
    
    # Match current index
    current_index = 0
    clean_current = st.session_state.current_page
    for idx, opt in enumerate(nav_options):
        # Match significant text
        key_token = opt.split(" ")[1] if len(opt.split(" ")) > 1 else opt
        if key_token.lower() in clean_current.lower():
            current_index = idx
            break
            
    selected_nav = st.radio(
        "Navigation",
        options=nav_options,
        index=current_index,
        label_visibility="collapsed"
    )
    st.session_state.current_page = selected_nav
    
    st.markdown("---")
    st.markdown("### 📊 Master System KPI")
    st.markdown("- **Restaurants**: 100 listings")
    st.markdown("- **Sentiment Benchmark**: 13,144 Yelp Reviews")
    st.markdown("- **Kolkata Synthetic Reviews**: 5,000 Annotations")
    st.markdown("- **FSSAI Audits**: 107 records (84 covered)")
    
    user_revs_all = get_all_user_reviews()
    st.markdown(f"- **Live User Reviews**: `{len(user_revs_all)}` in SQLite")
    
    st.markdown("---")
    render_html("""
    <div style="background:#F1F5F9; border-radius:8px; padding:0.75rem; font-size:0.74rem; color:#475569;">
        <strong>Academic Minor Project:</strong><br>
        Harmonizing customer NLP sentiment with municipal hygiene compliance and early risk surveillance in Kolkata, India.
    </div>
    """)

# Main Hero Banner
render_html("""
<div class="hero-banner">
    <div class="hero-title">Kolkata FoodLens & Review Intelligence 🍲</div>
    <div class="hero-subtitle">
        Go beyond the surface star rating. An integrated AI-driven intelligence platform combining 
        Aspect-Based Sentiment Analysis (ABSA), objective municipal FSSAI audits, and public health 
        hygiene risk surveillance for Kolkata dining establishments.
    </div>
</div>
""")

# ==============================================================================
# TAB 1: KOLKATA RESTAURANT DIRECTORY & SEARCH
# ==============================================================================
if "Directory" in st.session_state.current_page or "Explore" in st.session_state.current_page:
    render_html('<div class="section-head">🔍 Explore Kolkata Restaurants</div>')
    
    c1, c2, c3, c4 = st.columns([1.5, 1.2, 1.2, 1.1])
    with c1:
        search_query = st.text_input("Search restaurant name or dish", placeholder="e.g. Arsalan, biryani, mocambo...")
    with c2:
        all_neighbourhoods = ["All Neighbourhoods"] + sorted(restaurants_df["neighbourhood"].dropna().unique().tolist())
        selected_nb = st.selectbox("Neighbourhood", options=all_neighbourhoods)
    with c3:
        all_cuisines = ["All Cuisines"] + sorted(restaurants_df["primary_cuisine"].dropna().unique().tolist())
        selected_cuisine = st.selectbox("Primary Cuisine", options=all_cuisines)
    with c4:
        price_filter = st.selectbox("Price Tier", options=["All Tiers", "Budget (Tier 1)", "Moderate (Tier 2)", "Premium (Tier 3)", "Fine Dining (Tier 4)"])
        
    c5, c6 = st.columns([2, 1])
    with c5:
        max_cost = st.slider("Maximum Cost for Two (₹)", min_value=150, max_value=3500, value=3500, step=50)
    with c6:
        veg_only = st.checkbox("🌱 Veg-focused only", value=False)
        
    filtered = restaurants_df.copy()
    if search_query:
        q = search_query.lower().strip()
        filtered = filtered[
            filtered["name"].str.lower().str.contains(q, na=False) |
            filtered["cuisines"].str.lower().str.contains(q, na=False) |
            filtered["address"].str.lower().str.contains(q, na=False)
        ]
    if selected_nb != "All Neighbourhoods":
        filtered = filtered[filtered["neighbourhood"] == selected_nb]
    if selected_cuisine != "All Cuisines":
        filtered = filtered[filtered["primary_cuisine"] == selected_cuisine]
    if price_filter != "All Tiers":
        tier_num = int(price_filter.split("Tier ")[1][0])
        filtered = filtered[filtered["price_tier"] == tier_num]
    filtered = filtered[filtered["cost_for_two_inr"] <= max_cost]
    if veg_only:
        filtered = filtered[filtered["veg_focused"] == True]
        
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        render_html(f"""
        <div class="metric-card">
            <div class="metric-title">Matched Restaurants</div>
            <div class="metric-value">{len(filtered)}</div>
            <div class="metric-subtitle">Out of 100 indexed</div>
        </div>
        """)
    with kpi2:
        avg_rating = filtered["zomato_rating"].mean() if not filtered.empty else 0
        render_html(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Community Rating</div>
            <div class="metric-value">★ {avg_rating:.2f}</div>
            <div class="metric-subtitle">From Zomato Kolkata records</div>
        </div>
        """)
    with kpi3:
        avg_cost = filtered["cost_for_two_inr"].mean() if not filtered.empty else 0
        render_html(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Cost for Two</div>
            <div class="metric-value">₹{int(avg_cost)}</div>
            <div class="metric-subtitle">Dining cost estimate</div>
        </div>
        """)
    with kpi4:
        safety_verified_count = int((filtered["safety_data_confidence"] != "safety_data_unavailable").sum())
        render_html(f"""
        <div class="metric-card">
            <div class="metric-title">Food Safety Audits</div>
            <div class="metric-value">{safety_verified_count} / {len(filtered)}</div>
            <div class="metric-subtitle">Verified FSSAI records</div>
        </div>
        """)
        
    st.write("")
    
    if filtered.empty:
        st.warning("No restaurants match the selected filters. Please adjust your search criteria.")
    else:
        for _, row in filtered.iterrows():
            rid = row["restaurant_id"]
            name = row["name"]
            nb = row["neighbourhood"]
            cuis = row["cuisines"]
            cost = row["cost_for_two_inr"]
            ptier = row["price_range"]
            z_rat = row["zomato_rating"]
            z_votes = int(row["zomato_votes"])
            
            analytics = get_restaurant_analytics(rid)
            cust_score = analytics["cust_exp_score"]
            safety_info = safety_engine.calculate_score(rid)
            
            if safety_info["safety_score"] is not None:
                safety_val_str = f"{safety_info['safety_score']} / 100"
                safety_color = "#0F766E" if safety_info["safety_score"] >= 75 else ("#D97706" if safety_info["safety_score"] >= 50 else "#DC2626")
                conf_badge = '<span class="badge badge-teal">Verified FSSAI Audit</span>'
            else:
                safety_val_str = "Unavailable"
                safety_color = "#94A3B8"
                conf_badge = '<span class="badge badge-gray">No Records On File</span>'
                
            cust_color = "#0F766E" if cust_score >= 70 else ("#D97706" if cust_score >= 50 else "#DC2626")
            veg_badge = '<span class="badge badge-teal">🌱 Veg Focused</span>' if row["veg_focused"] else ''
            badges_html = f'{conf_badge} {veg_badge} <span class="badge badge-indigo">★ {z_rat:.1f} ({z_votes:,} votes)</span>'
            
            with st.container(border=True):
                render_html(f"""
                <div class="resto-card-inner">
                    <div class="resto-name">{name} <span style="font-size:0.9rem; font-weight:normal; color:#64748B;">({nb})</span></div>
                    <div class="resto-sub">🍽️ {cuis} &bull; ₹{cost} for two &bull; {ptier}</div>
                    <div style="margin-bottom:0.75rem;">{badges_html}</div>
                    <div class="score-triad">
                        <div class="score-item">
                            <div class="score-label">1. Customer Experience</div>
                            <div class="score-num" style="color:{cust_color};">{cust_score} <span style="font-size:0.75rem; color:#64748B;">/ 100</span></div>
                            <div style="font-size:0.68rem; color:#64748B;">From {analytics['total_reviews']} reviews</div>
                        </div>
                        <div class="score-item">
                            <div class="score-label">2. Verified Safety</div>
                            <div class="score-num" style="color:{safety_color};">{safety_val_str}</div>
                            <div style="font-size:0.68rem; color:#64748B;">Outcome: {safety_info['outcome'] or 'No data'}</div>
                        </div>
                        <div class="score-item">
                            <div class="score-label">3. Confidence Level</div>
                            <div class="score-num" style="font-size:0.95rem; margin-top:0.35rem; color:#1E293B;">{safety_info['confidence_label']}</div>
                            <div style="font-size:0.68rem; color:#64748B;">Inspection Evidence</div>
                        </div>
                    </div>
                </div>
                """)
                
                if st.button("Inspect Details & Submit Review ➔", key=f"btn_inspect_{rid}", use_container_width=True):
                    st.session_state.selected_restaurant_id = rid
                    st.session_state.current_page = "🏛️ Restaurant Deep Dive & Submit Review"
                    st.rerun()

# ==============================================================================
# TAB 2: RESTAURANT DEEP DIVE & REVIEW SUBMISSION
# ==============================================================================
elif "Detail" in st.session_state.current_page or "Dive" in st.session_state.current_page:
    render_html('<div class="section-head">🏛️ Restaurant Deep Dive & Review Center</div>')
    
    rest_names = restaurants_df["name"].tolist()
    rest_ids = restaurants_df["restaurant_id"].tolist()
    name_to_id = dict(zip(rest_names, rest_ids))
    
    cur_id = st.session_state.selected_restaurant_id
    cur_idx = rest_ids.index(cur_id) if cur_id in rest_ids else 0
    
    sel_name = st.selectbox("Select Restaurant to Inspect:", options=rest_names, index=cur_idx)
    st.session_state.selected_restaurant_id = name_to_id[sel_name]
    rid = st.session_state.selected_restaurant_id
    
    resto_row = restaurants_df[restaurants_df["restaurant_id"] == rid].iloc[0]
    analytics = get_restaurant_analytics(rid)
    safety_info = safety_engine.calculate_score(rid)
    
    render_html(f"""
    <div style="background:white; border-radius:12px; padding:1.5rem; border:1px solid #E2E8F0; margin-bottom:1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <h2 style="margin:0; font-size:2rem; font-weight:800; color:#0F172A;">{resto_row['name']}</h2>
                <div style="color:#64748B; font-size:0.95rem; margin-top:0.35rem;">
                    📍 {resto_row['address']} &bull; <strong>{resto_row['neighbourhood']}</strong>
                </div>
                <div style="color:#0F766E; font-size:0.9rem; font-weight:600; margin-top:0.25rem;">
                    🍽️ {resto_row['cuisines']} &bull; 🕒 {resto_row['opening_hours']} &bull; ₹{resto_row['cost_for_two_inr']} for two
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:1.6rem; font-weight:800; color:#F59E0B;">★ {resto_row['zomato_rating']:.1f}</div>
                <div style="font-size:0.75rem; color:#64748B;">{int(resto_row['zomato_votes']):,} Zomato Ratings</div>
            </div>
        </div>
    </div>
    """)
    
    col_sc1, col_sc2, col_sc3 = st.columns(3)
    with col_sc1:
        render_html(f"""
        <div class="metric-card" style="border-top: 4px solid #0F766E;">
            <div class="metric-title">1. Customer Experience Score</div>
            <div class="metric-value" style="color:#0F766E;">{analytics['cust_exp_score']} <span style="font-size:0.9rem; color:#64748B;">/ 100</span></div>
            <div class="metric-subtitle">
                Synthesized from <strong>{analytics['total_reviews']}</strong> total reviews<br>
                👍 {analytics['pos_count']} Pos &bull; ⚖️ {analytics['neu_count']} Neu &bull; 👎 {analytics['neg_count']} Neg
            </div>
        </div>
        """)
        
    with col_sc2:
        if safety_info["safety_score"] is not None:
            s_val = f"{safety_info['safety_score']} <span style='font-size:0.9rem; color:#64748B;'>/ 100</span>"
            s_color = "#0F766E" if safety_info["safety_score"] >= 75 else "#D97706"
            s_sub = f"Outcome: <strong>{safety_info['outcome']}</strong><br>Last Audit: {safety_info['last_inspected']}"
        else:
            s_val = "<span style='font-size:1.3rem; color:#64748B;'>Safety data unavailable</span>"
            s_color = "#64748B"
            s_sub = "Never fabricate scores when records are missing.<br>Status: <strong>No Municipal Audit File</strong>"
            
        render_html(f"""
        <div class="metric-card" style="border-top: 4px solid #3B82F6;">
            <div class="metric-title">2. Verified Safety Score</div>
            <div class="metric-value" style="color:{s_color};">{s_val}</div>
            <div class="metric-subtitle">{s_sub}</div>
        </div>
        """)
        
    with col_sc3:
        lic_display = str(int(safety_info['fssai_licence_no'])) if safety_info['fssai_licence_no'] is not None and pd.notna(safety_info['fssai_licence_no']) else 'Not registered'
        render_html(f"""
        <div class="metric-card" style="border-top: 4px solid #8B5CF6;">
            <div class="metric-title">3. Evidence Confidence</div>
            <div class="metric-value" style="font-size:1.35rem; color:#1E293B;">{safety_info['confidence_label']}</div>
            <div class="metric-subtitle">
                FSSAI Reg: <code>{lic_display}</code><br>
                Data Source: West Bengal Municipal Audit Protocol
            </div>
        </div>
        """)
        
    st.write("")
    col_absa, col_audit = st.columns([1.2, 1])
    with col_absa:
        st.markdown("#### 🎯 Aspect-Based Sentiment Breakdown")
        aspect_data = []
        for asp, vals in analytics["aspects"].items():
            aspect_data.append({
                "Aspect": asp.capitalize(),
                "Score": vals["score"],
                "Positive": vals["pos"],
                "Neutral": vals["neu"],
                "Negative": vals["neg"]
            })
        
        categories = [d["Aspect"] for d in aspect_data] + [aspect_data[0]["Aspect"]]
        scores = [d["Score"] for d in aspect_data] + [aspect_data[0]["Score"]]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=scores,
            theta=categories,
            fill='toself',
            name=resto_row['name'],
            line_color='#0F766E',
            fillcolor='rgba(15, 118, 110, 0.25)'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=320,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        asp_cols = st.columns(5)
        for i, asp_item in enumerate(aspect_data):
            with asp_cols[i]:
                c_score = asp_item["Score"]
                render_html(f"""
                <div style="background:white; border:1px solid #E2E8F0; border-radius:8px; padding:0.5rem; text-align:center;">
                    <div style="font-size:0.68rem; color:#64748B; font-weight:700;">{asp_item['Aspect']}</div>
                    <div style="font-size:1.1rem; font-weight:800; color:#0F172A;">{c_score}</div>
                </div>
                """)
                
    with col_audit:
        st.markdown("#### 🛡️ Food Safety Audit History")
        records = safety_engine.get_restaurant_records(rid)
        if records.empty:
            st.info("No municipal inspection records logged for this listing in the West Bengal food safety database.")
        else:
            for idx, r_row in records.iterrows():
                o_str = str(r_row['outcome'])
                o_badge = "badge-teal" if "satisfactory" in o_str.lower() else ("badge-amber" if "improvement" in o_str.lower() else "badge-rose")
                re_insp = "⚠️ Re-inspection required" if r_row['reinspection_required'] else "✅ Approved"
                
                v_str = str(r_row['violations_noted'])
                v_formatted = "None noted (Clean compliance)" if v_str.lower() in ["none", "nan", ""] else ", ".join([v.replace("_", " ").title() for v in v_str.split(";")])
                    
                render_html(f"""
                <div style="background:white; border-left:4px solid #0F766E; border-radius:8px; padding:0.9rem; margin-bottom:0.75rem; border-top:1px solid #E2E8F0; border-right:1px solid #E2E8F0; border-bottom:1px solid #E2E8F0;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge {o_badge}">{r_row['outcome']}</span>
                        <span style="font-size:0.75rem; color:#64748B;">Date: {r_row['inspection_date'].strftime('%d %b %Y') if pd.notna(r_row['inspection_date']) else 'N/A'}</span>
                    </div>
                    <div style="font-size:0.8rem; color:#1E293B; margin-top:0.4rem;">
                        <strong>Type:</strong> {r_row['inspection_type']} &bull; <strong>Licence:</strong> {r_row['licence_status']}
                    </div>
                    <div style="font-size:0.78rem; color:#475569; margin-top:0.25rem;">
                        <strong>Violations:</strong> {v_formatted}
                    </div>
                    <div style="font-size:0.74rem; color:#64748B; margin-top:0.25rem;">
                        {re_insp}
                    </div>
                </div>
                """)
                
    st.markdown("---")
    
    # Review Submission Section
    st.markdown("### ✍️ Submit a Live Review with AI Sentiment Analysis")
    with st.form(key=f"submit_review_form_{rid}"):
        cf1, cf2 = st.columns([2, 1])
        with cf1:
            reviewer_name = st.text_input("Your Name / Alias", placeholder="e.g. Sourav Mukherjee", value="")
        with cf2:
            reviewer_rating = st.selectbox("Star Rating (1-5)", options=[5, 4, 3, 2, 1], index=0)
            
        review_content = st.text_area(
            "Review Text",
            placeholder="Describe your dining experience, taste of the food, service promptness, cleanliness, hygiene, ambience, or pricing...",
            height=110
        )
        btn_submit = st.form_submit_button("⚡ Analyze & Submit Review")
        
    if btn_submit:
        if not review_content.strip():
            st.error("Please enter your review text before submitting.")
        else:
            with st.spinner("Running sentiment classification and aspect polarity models..."):
                pred_sentiment = predict_sentiment(review_content)
                pred_aspects = predict_aspects(review_content)
                new_rev_id = save_user_review(
                    restaurant_id=rid,
                    user_name=reviewer_name,
                    rating=reviewer_rating,
                    review_text=review_content,
                    sentiment=pred_sentiment,
                    aspects=pred_aspects
                )
                
            st.success(f"Review successfully analyzed and stored in SQLite database! (Review ID: #{new_rev_id})")
            
            sent_label = pred_sentiment["label"].upper()
            sent_conf = pred_sentiment["confidence"] * 100.0
            badge_color = "#10B981" if sent_label == "POSITIVE" else ("#F59E0B" if sent_label == "NEUTRAL" else "#EF4444")
            
            render_html(f"""
            <div style="background:#F0FDFA; border:1px solid #99F6E4; border-radius:10px; padding:1.1rem; margin-top:0.75rem; margin-bottom:1rem;">
                <div style="font-weight:750; font-size:1.05rem; color:#0F766E; margin-bottom:0.5rem;">
                    🤖 Real-Time AI Inference Result:
                </div>
                <div style="display:flex; align-items:center; gap:1rem; flex-wrap:wrap; margin-bottom:0.75rem;">
                    <div>Overall Sentiment: <span style="background:{badge_color}; color:white; padding:0.25rem 0.75rem; border-radius:9999px; font-weight:700;">{sent_label} ({sent_conf:.1f}% confidence)</span></div>
                </div>
                <div style="font-size:0.85rem; color:#1E293B; margin-bottom:0.35rem; font-weight:600;">Aspect-Level Sentiment Extraction:</div>
                <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
                    <span class="badge {'badge-teal' if pred_aspects['food']=='positive' else ('badge-rose' if pred_aspects['food']=='negative' else 'badge-gray')}">Food: {pred_aspects['food'].upper()}</span>
                    <span class="badge {'badge-teal' if pred_aspects['service']=='positive' else ('badge-rose' if pred_aspects['service']=='negative' else 'badge-gray')}">Service: {pred_aspects['service'].upper()}</span>
                    <span class="badge {'badge-teal' if pred_aspects['hygiene']=='positive' else ('badge-rose' if pred_aspects['hygiene']=='negative' else 'badge-gray')}">Hygiene: {pred_aspects['hygiene'].upper()}</span>
                    <span class="badge {'badge-teal' if pred_aspects['ambience']=='positive' else ('badge-rose' if pred_aspects['ambience']=='negative' else 'badge-gray')}">Ambience: {pred_aspects['ambience'].upper()}</span>
                    <span class="badge {'badge-teal' if pred_aspects['price']=='positive' else ('badge-rose' if pred_aspects['price']=='negative' else 'badge-gray')}">Price: {pred_aspects['price'].upper()}</span>
                </div>
            </div>
            """)
            st.button("🔄 Refresh Analytics with New Review", on_click=lambda: None)
            
    # Reviews List Feed
    st.markdown("### 💬 Customer Reviews & Feedback Feed")
    tab_all, tab_live, tab_hist = st.tabs(["All Reviews", "Live Submissions (SQLite)", "Historical Dataset Reviews"])
    
    with tab_live:
        live_revs = get_user_reviews(rid)
        if not live_revs:
            st.info("No live reviews submitted yet for this restaurant. Be the first to submit above!")
        else:
            for l_rev in live_revs:
                s_col = "#10B981" if l_rev['sentiment_label'] == 'positive' else ("#F59E0B" if l_rev['sentiment_label'] == 'neutral' else "#EF4444")
                render_html(f"""
                <div style="background:white; border-left:4px solid {s_col}; border-radius:8px; padding:1rem; margin-bottom:0.75rem; border-top:1px solid #E2E8F0; border-right:1px solid #E2E8F0; border-bottom:1px solid #E2E8F0;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong>{l_rev['user_name']}</strong>
                        <span style="font-size:0.78rem; color:#64748B;">{l_rev['created_at']} &bull; <span class="badge badge-teal">Live SQLite Submission</span></span>
                    </div>
                    <div style="color:#F59E0B; margin:0.25rem 0;">{'★'*l_rev['rating']}{'☆'*(5-l_rev['rating'])}</div>
                    <p style="font-size:0.9rem; color:#1E293B; margin:0.4rem 0;">{l_rev['review_text']}</p>
                    <div style="display:flex; gap:0.35rem; flex-wrap:wrap; margin-top:0.35rem;">
                        <span class="badge badge-indigo">Sentiment: {l_rev['sentiment_label'].upper()} ({l_rev['sentiment_confidence']*100:.0f}%)</span>
                        <span class="badge badge-gray">Food: {l_rev['sentiment_food']}</span>
                        <span class="badge badge-gray">Service: {l_rev['sentiment_service']}</span>
                        <span class="badge badge-gray">Hygiene: {l_rev['sentiment_hygiene']}</span>
                    </div>
                </div>
                """)
                
    with tab_hist:
        hist_revs = reviews_df[reviews_df["restaurant_id"] == rid].head(25)
        for _, h_rev in hist_revs.iterrows():
            s_col = "#10B981" if str(h_rev['sentiment_label']).lower() == 'positive' else ("#F59E0B" if str(h_rev['sentiment_label']).lower() == 'neutral' else "#EF4444")
            render_html(f"""
            <div style="background:white; border-left:4px solid {s_col}; border-radius:8px; padding:0.9rem; margin-bottom:0.65rem; border-top:1px solid #E2E8F0; border-right:1px solid #E2E8F0; border-bottom:1px solid #E2E8F0;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong>{h_rev['user_alias']}</strong>
                    <span style="font-size:0.75rem; color:#64748B;">{h_rev['review_date']} &bull; Source: {h_rev['platform']}</span>
                </div>
                <div style="color:#F59E0B; margin:0.2rem 0;">{'★'*int(h_rev['rating'])}{'☆'*(5-int(h_rev['rating']))}</div>
                <p style="font-size:0.88rem; color:#1E293B; margin:0.3rem 0;">{h_rev['review_text']}</p>
                <div style="display:flex; gap:0.3rem; flex-wrap:wrap;">
                    <span class="badge badge-indigo">Sentiment: {str(h_rev['sentiment_label']).upper()}</span>
                    <span class="badge badge-gray">Food: {h_rev['sentiment_food']}</span>
                    <span class="badge badge-gray">Service: {h_rev['sentiment_service']}</span>
                    <span class="badge badge-gray">Hygiene: {h_rev['sentiment_hygiene']}</span>
                </div>
            </div>
            """)
            
    with tab_all:
        all_revs_to_show = []
        for ur in live_revs:
            all_revs_to_show.append({
                "author": ur["user_name"],
                "source": "Live User Review",
                "date": ur["created_at"],
                "rating": ur["rating"],
                "text": ur["review_text"],
                "sentiment": ur["sentiment_label"]
            })
        for _, hr in hist_revs.head(15).iterrows():
            all_revs_to_show.append({
                "author": hr["user_alias"],
                "source": f"{hr['platform']} Listing",
                "date": hr["review_date"],
                "rating": int(hr["rating"]),
                "text": hr["review_text"],
                "sentiment": hr["sentiment_label"]
            })
            
        for r_item in all_revs_to_show[:15]:
            render_html(f"""
            <div style="background:white; border-radius:8px; padding:0.8rem; margin-bottom:0.5rem; border:1px solid #E2E8F0;">
                <div style="display:flex; justify-content:space-between;">
                    <strong>{r_item['author']}</strong>
                    <span style="font-size:0.75rem; color:#64748B;">{r_item['source']} &bull; {r_item['date']}</span>
                </div>
                <div style="color:#F59E0B; font-size:0.85rem;">{'★'*r_item['rating']} &bull; <span class="badge badge-teal">{r_item['sentiment'].upper()}</span></div>
                <div style="font-size:0.85rem; color:#334155; margin-top:0.25rem;">{r_item['text']}</div>
            </div>
            """)

# ==============================================================================
# TAB 3: CONTEXTUAL DINING RECOMMENDATIONS (FIXED RANK KEYERROR)
# ==============================================================================
elif "Recommendation" in st.session_state.current_page:
    render_html('<div class="section-head">🎯 Context-Aware Dining Recommendations</div>')
    st.markdown("""
    Our multi-criteria algorithm blends four objective signals:
    **50% Customer Experience Sentiment** + **25% Zomato Community Rating** + **15% Verified Municipal Safety Score** + **10% Dining Context Tag Matching**.
    *No demographic or gender stereotyping is used; recommendations are strictly context-driven.*
    """)
    
    rc1, rc2, rc3 = st.columns([1.2, 1.2, 1.2])
    with rc1:
        occasion_choice = st.selectbox(
            "Dining Occasion / Context",
            options=[
                "Family Outing (Kids & Family Friendly)",
                "Students / Budget Hangout",
                "Romantic Date Night (Cozy & Outdoor)",
                "Large Group Party / Late Night",
                "Solo Dining (Comfortable & Fast)",
                "Any Occasion"
            ]
        )
        occasion_key_map = {
            "Family Outing (Kids & Family Friendly)": "family",
            "Students / Budget Hangout": "students",
            "Romantic Date Night (Cozy & Outdoor)": "couples",
            "Large Group Party / Late Night": "groups",
            "Solo Dining (Comfortable & Fast)": "solo",
            "Any Occasion": "any"
        }
        chosen_occ = occasion_key_map[occasion_choice]
        
    with rc2:
        rec_cuisine = st.selectbox(
            "Cuisine Preference",
            options=["Any Cuisine", "Bengali", "North Indian", "Chinese", "Mughlai", "Continental", "Rolls", "Desserts", "Cafe", "Biryani"]
        )
        c_param = None if rec_cuisine == "Any Cuisine" else rec_cuisine
        
    with rc3:
        rec_nb = st.selectbox(
            "Preferred Neighbourhood",
            options=["Any Neighbourhood", "Park Street", "Salt Lake", "Ballygunge", "Esplanade", "New Town", "Shyambazar", "Bhowanipore", "Gariahat"]
        )
        nb_param = None if rec_nb == "Any Neighbourhood" else rec_nb
        
    rc4, rc5 = st.columns([2, 1])
    with rc4:
        rec_budget = st.slider("Budget Limit for Two (₹)", min_value=200, max_value=3500, value=1500, step=100)
    with rc5:
        rec_veg_only = st.checkbox("🌱 Strictly Vegetarian", value=False)
        
    results = rec_engine.recommend(
        max_budget=rec_budget,
        occasion=chosen_occ,
        cuisine=c_param,
        neighbourhood=nb_param,
        veg_only=rec_veg_only,
        top_k=8
    )
    
    st.markdown(f"#### Top {len(results)} Recommendations for Your Scenario")
    if not results:
        st.warning("No restaurants match all selected criteria. Try widening your budget or selecting 'Any Neighbourhood'.")
    else:
        for rank_idx, item in enumerate(results, 1):
            rid = item["restaurant_id"]
            name = item["name"]
            nb = item["neighbourhood"]
            cuis = item["primary_cuisine"]
            cost = item["cost_for_two_inr"]
            z_rat = item["zomato_rating"]
            sent_score = item["sentiment_score"]
            safety_display = item["safety_display"]
            m_score = item["composite_rank_score"]
            tags = item["tags"]
            
            tag_badges = " ".join([f'<span class="badge badge-teal">{t.replace("_", " ").title()}</span>' for t in tags])
            
            with st.container(border=True):
                render_html(f"""
                <div class="resto-card-inner">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <span class="badge badge-indigo">Rank #{rank_idx} Match</span>
                            <span style="font-size:1.4rem; font-weight:800; color:#0F172A; margin-left:0.35rem;">{name}</span>
                            <div class="resto-sub">📍 {nb} &bull; 🍽️ {cuis} &bull; ₹{cost} for two</div>
                            <div>{tag_badges}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:1.6rem; font-weight:850; color:#0F766E;">{m_score}</div>
                            <div style="font-size:0.75rem; color:#64748B;">Composite Match Score</div>
                        </div>
                    </div>
                    
                    <div class="score-triad" style="margin-top:0.75rem;">
                        <div class="score-item">
                            <div class="score-label">Sentiment (50%)</div>
                            <div class="score-num" style="font-size:1.15rem; color:#0F766E;">{sent_score} <span style="font-size:0.7rem; color:#64748B;">/ 100</span></div>
                        </div>
                        <div class="score-item">
                            <div class="score-label">Zomato Rating (25%)</div>
                            <div class="score-num" style="font-size:1.15rem; color:#F59E0B;">★ {z_rat:.1f}</div>
                        </div>
                        <div class="score-item">
                            <div class="score-label">Safety Compliance (15%)</div>
                            <div class="score-num" style="font-size:1.1rem; color:#1E293B;">{safety_display}</div>
                        </div>
                    </div>
                </div>
                """)
                
                if st.button(f"View Details for {name} ➔", key=f"btn_rec_{rid}", use_container_width=True):
                    st.session_state.selected_restaurant_id = rid
                    st.session_state.current_page = "🏛️ Restaurant Deep Dive & Submit Review"
                    st.rerun()

# ==============================================================================
# TAB 4: RESTAURANT COMPARE VIEW
# ==============================================================================
elif "Compare" in st.session_state.current_page:
    render_html('<div class="section-head">⚖️ Side-by-Side Restaurant Comparison</div>')
    st.markdown("Compare 2 or 3 Kolkata dining establishments across Sentiment, Aspect Scores, Safety Compliance, and Price.")
    
    all_names = restaurants_df["name"].tolist()
    default_sel = [all_names[0], all_names[1], all_names[2]] if len(all_names) >= 3 else all_names[:2]
    
    chosen_names = st.multiselect(
        "Select 2 or 3 Restaurants to Compare:",
        options=all_names,
        default=default_sel,
        max_selections=3
    )
    
    if len(chosen_names) < 2:
        st.info("Please select at least 2 restaurants to compare.")
    else:
        comp_records = []
        radar_traces = []
        
        for name in chosen_names:
            row = restaurants_df[restaurants_df["name"] == name].iloc[0]
            rid = row["restaurant_id"]
            analytics = get_restaurant_analytics(rid)
            safety = safety_engine.calculate_score(rid)
            
            lic_str = str(int(safety['fssai_licence_no'])) if safety['fssai_licence_no'] is not None and pd.notna(safety['fssai_licence_no']) else "N/A"
            comp_records.append({
                "Restaurant": name,
                "Neighbourhood": row["neighbourhood"],
                "Cuisine": row["primary_cuisine"],
                "Cost for Two": f"₹{row['cost_for_two_inr']}",
                "Price Tier": row["price_range"],
                "Zomato Rating": f"★ {row['zomato_rating']:.1f} ({int(row['zomato_votes'])} votes)",
                "Customer Experience Score": f"{analytics['cust_exp_score']} / 100",
                "Verified Safety Score": f"{safety['safety_score']} / 100" if safety['safety_score'] is not None else "Safety data unavailable",
                "Safety Confidence": safety['confidence_label'],
                "FSSAI Licence": lic_str
            })
            
            asp_scores = [analytics["aspects"][k]["score"] for k in ["food", "service", "hygiene", "ambience", "price"]]
            asp_scores.append(asp_scores[0])
            categories = ["Food", "Service", "Hygiene", "Ambience", "Price", "Food"]
            
            radar_traces.append(go.Scatterpolar(
                r=asp_scores,
                theta=categories,
                fill='toself',
                name=name
            ))
            
        comp_df = pd.DataFrame(comp_records).set_index("Restaurant").T
        st.dataframe(comp_df, use_container_width=True)
        
        st.markdown("#### 🎯 Aspect Satisfaction Comparison")
        fig_comp = go.Figure(data=radar_traces)
        fig_comp.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=380,
            margin=dict(l=40, r=40, t=30, b=30)
        )
        st.plotly_chart(fig_comp, use_container_width=True)

# ==============================================================================
# TAB 5: PUBLIC HEALTH FOOD SAFETY SURVEILLANCE (EARLY WARNING ENGINE)
# ==============================================================================
elif "Surveillance" in st.session_state.current_page:
    render_html('<div class="section-head">🛡️ Public Health Food Safety & Hygiene Surveillance</div>')
    st.markdown("""
    **Automated early-warning inspection engine mapping unstructured consumer reviews to municipal health code violation risks.**  
    Motivated by intensive food safety crackdowns across West Bengal and Kolkata by the Kolkata Municipal Corporation (KMC) and Health Department.
    Operationalizes public health methodologies from the **CDC & NYC Department of Health (Harrison et al.)** and **Harvard Smart Inspection Initiatives (Glaeser et al.)**.
    """)
    
    col1, col2 = st.columns([1.1, 0.9], gap="large")
    with col1:
        st.markdown("#### Test a Health & Food Safety Review")
        st.caption("Click a preset below or enter any real-world customer review:")
        
        s_cols = st.columns(2)
        for idx, (label, sample_txt) in enumerate(SAFETY_SAMPLE_REVIEWS.items()):
            col_target = s_cols[idx % 2]
            if col_target.button(f"{label}", key=f"safety_sample_btn_{idx}", use_container_width=True):
                st.session_state.safety_audit_text = sample_txt
                
        safety_text_val = st.session_state.get("safety_audit_text", SAFETY_SAMPLE_REVIEWS["Biological Illness (Critical)"])
        
        with st.form("safety_audit_form"):
            safety_input = st.text_area(
                "Review text for health & hygiene audit:",
                value=safety_text_val,
                height=140,
                placeholder="Example: The chicken was undercooked, smelled bad, and gave me severe food poisoning and stomach cramps."
            )
            btn_audit = st.form_submit_button("🚨 Run Food Safety Surveillance Audit", type="primary", use_container_width=True)
            
        if btn_audit and safety_input.strip():
            audit_res = scan_food_safety(safety_input.strip())
            pred_sent = predict_sentiment(safety_input.strip())
            
            render_html(f"""
            <div style="background:{audit_res['bg_color']}; border:2px solid {audit_res['border_color']}; border-radius:10px; padding:1.25rem; margin-top:1rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                    <span style="font-weight:900; letter-spacing:.05em; font-size:1rem; text-transform:uppercase; color:{audit_res['badge_color']};">
                        AUDIT RESULT: {audit_res['severity'].upper()} RISK
                    </span>
                    <span style="background:{audit_res['badge_color']}; color:#fff; padding:.25rem .75rem; border-radius:99px; font-size:.76rem; font-weight:800;">
                        PREDICTED SENTIMENT: {pred_sent['label'].upper()} ({pred_sent['confidence']*100:.1f}%)
                    </span>
                </div>
                <p style="margin:.75rem 0 .4rem; font-size:.95rem; line-height:1.5; color:#1E293B;">
                    <strong>Municipal Advisory:</strong> {audit_res['recommendation']}
                </p>
            </div>
            """)
            
            if audit_res["is_flagged"]:
                st.markdown("##### ⚠️ Detected Health & Safety Code Indicators")
                for cat, terms in audit_res["violations"].items():
                    terms_pills = " ".join([f'<span class="badge badge-rose">{t}</span>' for t in terms])
                    render_html(f"<div style='margin-bottom:6px; font-size:0.9rem;'>• <strong>{cat}:</strong> {terms_pills}</div>")
            else:
                st.success("✅ No critical biological illness, pest infestation, or sanitation triggers detected in this review.")
                
    with col2:
        st.markdown("#### Surveillance Taxonomy & Public Health Triggers")
        st.markdown("""
        **1. Critical Biological Hazard (Red Alert)**
        - Severe illness signals: *food poisoning, vomiting, diarrhea, stomach cramps, hospital, Salmonella, raw chicken*.
        - Action: Priority physical inspection dispatch.
        
        **2. Contamination & Pest Spoilage (Orange Alert)**
        - Vector risks: *cockroach, rat, fly, maggot, foreign objects, moldy, rancid oil, bad smell*.
        - Action: Kitchen storage and ingredient freshness audit.
        
        **3. Kitchen Sanitation Lapse (Yellow Alert)**
        - Physical hygiene failures: *dirty utensils, unwashed plates, sticky tables, filthy washrooms, bare hands*.
        - Action: Mandatory hygiene training and sanitation notice.
        """)

# ==============================================================================
# TAB 6: SENTIMENT & ASPECT STUDIO (LIVE INFERENCE PLAYGROUND)
# ==============================================================================
elif "Studio" in st.session_state.current_page or "Playground" in st.session_state.current_page:
    render_html('<div class="section-head">✳️ Live Sentiment & Aspect Analysis Studio</div>')
    st.markdown("Interactive natural language processing workbench evaluating overall sentiment and 5 fine-grained dining aspects.")
    
    sample_reviews = [
        "The mutton biryani was fragrant and cooked to perfection, but the washroom was filthy and waiters were rude.",
        "Loved the authentic flavours, attentive staff, and cozy decor. Highly recommend to everyone visiting Park Street!",
        "Completely overpriced. Stale chicken, cold naan, and waited 45 minutes for our bill.",
        "Decent rolls for a quick bite after college. Inexpensive and hygienic enough for street food."
    ]
    
    quick_pick = st.selectbox("Or choose a sample review:", options=["Custom text..."] + sample_reviews)
    default_val = "" if quick_pick == "Custom text..." else quick_pick
    
    test_text = st.text_area(
        "Enter Review Text:",
        value=default_val,
        placeholder="Type or paste any customer review here...",
        height=130
    )
    
    if st.button("Run AI Model Inference", type="primary"):
        if not test_text.strip():
            st.error("Please enter review text to analyze.")
        else:
            with st.spinner("Processing text cleaning, TF-IDF vectorization, and inference..."):
                sent_res = predict_sentiment(test_text)
                absa_res = predict_aspects(test_text)
                
            st.markdown("#### Overall Sentiment Classification")
            c_lbl, c_gauge = st.columns([1, 2])
            with c_lbl:
                lbl = sent_res["label"].upper()
                conf = sent_res["confidence"] * 100.0
                col_b = "#10B981" if lbl == "POSITIVE" else ("#F59E0B" if lbl == "NEUTRAL" else "#EF4444")
                render_html(f"""
                <div style="background:white; border-left:6px solid {col_b}; border-radius:10px; padding:1.2rem; border-top:1px solid #E2E8F0; border-right:1px solid #E2E8F0; border-bottom:1px solid #E2E8F0;">
                    <div style="font-size:0.8rem; color:#64748B; text-transform:uppercase; font-weight:700;">Predicted Sentiment</div>
                    <div style="font-size:2rem; font-weight:800; color:{col_b}; margin-top:0.2rem;">{lbl}</div>
                    <div style="font-size:0.85rem; color:#1E293B; margin-top:0.4rem;">Model Confidence: <strong>{conf:.1f}%</strong></div>
                </div>
                """)
                
            with c_gauge:
                probs = sent_res["probabilities"]
                prob_df = pd.DataFrame([
                    {"Sentiment": "Negative", "Probability": probs.get("negative", 0.0), "Color": "#EF4444"},
                    {"Sentiment": "Neutral", "Probability": probs.get("neutral", 0.0), "Color": "#F59E0B"},
                    {"Sentiment": "Positive", "Probability": probs.get("positive", 0.0), "Color": "#10B981"}
                ])
                fig_p = px.bar(
                    prob_df,
                    x="Probability",
                    y="Sentiment",
                    orientation="h",
                    color="Sentiment",
                    color_discrete_map={"Negative": "#EF4444", "Neutral": "#F59E0B", "Positive": "#10B981"},
                    range_x=[0, 1.0],
                    text="Probability"
                )
                fig_p.update_traces(texttemplate='%{x:.1%}', textposition='outside')
                fig_p.update_layout(height=170, margin=dict(l=10, r=40, t=10, b=10), showlegend=False)
                st.plotly_chart(fig_p, use_container_width=True)
                
            st.markdown("#### Aspect-Level Polarity Extraction (ABSA)")
            acols = st.columns(5)
            aspect_icons = {"food": "🍲 Food", "service": "🧑‍🍳 Service", "hygiene": "🧼 Hygiene", "ambience": "🕯️ Ambience", "price": "💰 Price"}
            for i, (asp_key, asp_val) in enumerate(absa_res.items()):
                with acols[i]:
                    bg_badge = "#10B981" if asp_val == "positive" else ("#F59E0B" if asp_val == "neutral" else "#EF4444")
                    render_html(f"""
                    <div style="background:white; border-radius:10px; padding:0.9rem; text-align:center; border:1px solid #E2E8F0;">
                        <div style="font-size:0.85rem; font-weight:700; color:#1E293B;">{aspect_icons.get(asp_key, asp_key.capitalize())}</div>
                        <div style="background:{bg_badge}; color:white; border-radius:9999px; font-size:0.75rem; font-weight:750; padding:0.25rem 0.6rem; margin-top:0.5rem; text-transform:uppercase;">
                            {asp_val}
                        </div>
                    </div>
                    """)

# ==============================================================================
# TAB 7: BATCH INTELLIGENCE CENTER (BULK INFERENCE & FOOD SAFETY FLAGGING)
# ==============================================================================
elif "Batch" in st.session_state.current_page:
    render_html('<div class="section-head">▦ Batch Intelligence Center</div>')
    st.markdown("Process large batches of customer reviews to extract sentiment polarities, ABSA dimensions, and public health hygiene flags in bulk.")
    
    uploaded_file = st.file_uploader("Upload CSV review file (must have a review_text column)", type=["csv"])
    btn_sample_batch = st.button("Load Pre-generated Synthetic Batch (500 reviews)")
    
    batch_df = None
    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
    elif btn_sample_batch:
        batch_sample_path = ROOT / "synthetic_food_reviews_batch_test.csv"
        if batch_sample_path.exists():
            batch_df = pd.read_csv(batch_sample_path)
        else:
            batch_df = reviews_df.head(200)[["review_id", "restaurant_name", "rating", "review_text"]]
            
    if batch_df is not None:
        text_col = "review_text" if "review_text" in batch_df.columns else batch_df.columns[0]
        st.write(f"Loaded **{len(batch_df)}** reviews. Target text column: `{text_col}`")
        
        if st.button("🚀 Run Batch Intelligence Pipeline", type="primary"):
            with st.spinner(f"Classifying {len(batch_df)} reviews with TF-IDF Sentiment, ABSA, and Food Safety Surveillance..."):
                results_list = []
                for txt in batch_df[text_col]:
                    s = predict_sentiment(str(txt))
                    a = predict_aspects(str(txt))
                    sf = scan_food_safety(str(txt))
                    results_list.append({
                        "pred_sentiment": s["label"],
                        "sentiment_confidence": s["confidence"],
                        "food_aspect": a["food"],
                        "service_aspect": a["service"],
                        "hygiene_aspect": a["hygiene"],
                        "ambience_aspect": a["ambience"],
                        "price_aspect": a["price"],
                        "safety_risk_level": sf["severity"],
                        "food_safety_flagged": sf["is_flagged"],
                    })
                res_df = pd.concat([batch_df.reset_index(drop=True), pd.DataFrame(results_list)], axis=1)
                
            st.success(f"Successfully processed {len(res_df)} reviews!")
            
            bcol1, bcol2, bcol3 = st.columns(3)
            with bcol1:
                fig_dist = px.pie(
                    res_df,
                    names="pred_sentiment",
                    title="Predicted Sentiment Share",
                    color="pred_sentiment",
                    color_discrete_map={"positive": "#10B981", "neutral": "#F59E0B", "negative": "#EF4444"}
                )
                st.plotly_chart(fig_dist, use_container_width=True)
            with bcol2:
                hyg_counts = res_df["hygiene_aspect"].value_counts().reset_index()
                hyg_counts.columns = ["Hygiene Status", "Count"]
                fig_hyg = px.bar(
                    hyg_counts,
                    x="Hygiene Status",
                    y="Count",
                    title="Hygiene Aspect Distribution",
                    color="Hygiene Status",
                    color_discrete_map={"positive": "#10B981", "neutral": "#F59E0B", "negative": "#EF4444"}
                )
                st.plotly_chart(fig_hyg, use_container_width=True)
            with bcol3:
                safe_counts = res_df["safety_risk_level"].value_counts().reset_index()
                safe_counts.columns = ["Safety Risk", "Count"]
                fig_safe = px.bar(
                    safe_counts,
                    x="Safety Risk",
                    y="Count",
                    title="Food Safety Surveillance Risks",
                    color="Safety Risk",
                    color_discrete_map={"Critical": "#DC2626", "High": "#EA580C", "Moderate": "#D97706", "Low / None": "#10B981"}
                )
                st.plotly_chart(fig_safe, use_container_width=True)
                
            st.dataframe(res_df.head(25), use_container_width=True)
            
            csv_buffer = io.StringIO()
            res_df.to_csv(csv_buffer, index=False)
            st.download_button(
                "📥 Download Processed CSV with AI & Safety Labels",
                data=csv_buffer.getvalue(),
                file_name="kolkata_foodlens_batch_results.csv",
                mime="text/csv"
            )

# ==============================================================================
# TAB 8: MODEL BENCHMARK & EVALUATION LAB
# ==============================================================================
elif "Benchmark" in st.session_state.current_page or "Evaluation" in st.session_state.current_page:
    render_html('<div class="section-head">📊 Model Benchmark & Evaluation Lab</div>')
    st.markdown("""
    Rigorous performance benchmarking across four classifiers trained on **13,144 real restaurant reviews** 
    and evaluated on a strictly held-out test set of **1,315 reviews**.
    """)
    
    comp_csv_path = ROOT / "reports" / "model_comparison.csv"
    if comp_csv_path.exists():
        comp_df = pd.read_csv(comp_csv_path)
        # Format for clean display
        display_comp = comp_df.copy()
        for col in ["accuracy", "macro_precision", "macro_recall", "macro_f1", "weighted_f1", "negative_f1", "neutral_f1", "positive_f1"]:
            if col in display_comp.columns:
                display_comp[col] = display_comp[col].apply(lambda x: f"{x*100:.2f}%")
        st.dataframe(display_comp, use_container_width=True)
        
    barchart_path = ROOT / "reports" / "figures" / "model_comparison_barchart.png"
    if barchart_path.exists():
        st.image(str(barchart_path), caption="Model Comparison on Held-Out Test Set (Macro-F1, Accuracy, Negative-F1)")
        
    st.markdown("#### Confusion Matrix Inspector")
    cm_choice = st.selectbox(
        "Select Model to Inspect Confusion Matrix:",
        options=[
            "TF-IDF + Logistic Regression (Balanced Winner)",
            "TF-IDF + Linear SVM (Balanced)",
            "TF-IDF + Multi-Layer Perceptron (MLP Neural Net)",
            "TF-IDF + Complement Naive Bayes"
        ]
    )
    cm_map = {
        "TF-IDF + Logistic Regression (Balanced Winner)": "cm_TF_IDF_plus_LogisticRegression.png",
        "TF-IDF + Linear SVM (Balanced)": "cm_TF_IDF_plus_LinearSVM.png",
        "TF-IDF + Multi-Layer Perceptron (MLP Neural Net)": "cm_TF_IDF_plus_MLP_Neural_Net.png",
        "TF-IDF + Complement Naive Bayes": "cm_TF_IDF_plus_ComplementNB.png"
    }
    cm_file = ROOT / "reports" / "figures" / cm_map[cm_choice]
    if cm_file.exists():
        st.image(str(cm_file), caption=f"Normalized Confusion Matrix: {cm_choice}", width=540)

# ==============================================================================
# TAB 9: METHODOLOGY & MODEL CARD
# ==============================================================================
elif "Methodology" in st.session_state.current_page or "About" in st.session_state.current_page:
    render_html('<div class="section-head">📖 System Architecture & Methodology</div>')
    
    st.markdown("""
    ### 1. Executive Summary
    **Kolkata FoodLens** is an end-to-end intelligent dining discovery and food hygiene audit platform tailored for the city of Kolkata, India.
    Designed as a comprehensive computer science minor project, it solves a fundamental flaw in existing restaurant aggregators: **the conflation of customer popularity with municipal food safety**.
    
    ### 2. Multi-Criteria Architecture
    The platform processes four independent layers of intelligence:
    
    1. **Customer Experience Score (50%)**: Derived from customer reviews using a class-balanced TF-IDF + Logistic Regression classifier trained on 13,144 authentic restaurant reviews.
    2. **Zomato Food Community Rating (25%)**: Incorporating crowd-sourced ratings (1.0 to 5.0 stars) from authentic Zomato listings.
    3. **Verified Food Safety Score (15%)**: Computed via an objective audit algorithm from municipal FSSAI inspection records.
    4. **Context & Suitability Tag Matching (10%)**: Strictly non-stereotypical matching across dining contexts (family, students, couples, groups, solo).
    
    ```
    Customer Review Corpus ──> Text Preprocessing & Emojis ──> TF-IDF + Logistic Regression ──> Customer Experience Score (50%)
                                                           └──> Clause-Level ABSA Engine     ──> 5-Aspect Polarity Breakdown
    
    Municipal Inspection Logs ───────────────────────────────> Safety Scoring Engine          ──> Verified Safety Score 0-100 (15%)
    
    Zomato Community Ratings ───────────────────────────────────────────────────────────────> Zomato Rating 1-5 (25%)
    
    Dining Context Suitability ─────────────────────────────────────────────────────────────> Occasion Match (10%)
    
                                  │
                                  ▼
                     Multi-Criteria Ranking Engine ──> Ranked Dining Recommendations
                                                   └──> Live Streamlit UI & SQLite DB
    ```
    
    ### 3. Food Safety Integrity Rules
    - **Never Fabricate Data**: If a restaurant does not have a verified municipal inspection record, the system explicitly displays `Safety data unavailable` with a confidence indicator of `No inspection record on file`.
    - **Re-weighting Integrity**: When a restaurant lacks safety records, the 15% safety weight is proportionally reallocated to customer experience (60%), Zomato rating (30%), and context tags (10%), preventing artificial penalties or unearned bonuses.
    
    ### 4. Mathematical Formulations
    
    #### A. Food Safety Score (0–100 Scale)
    $$\\text{Safety Score} = \\text{Outcome (40 pts)} + \\text{Licence (30 pts)} + \\text{Violation Penalty (20 pts)} + \\text{Recency (10 pts)}$$
    - **Inspection Outcome**: Satisfactory = 40 pts, Needs Improvement = 20 pts, Major Violations = 5 pts.
    - **Licence Status**: Active = 30 pts, Renewal Due = 15 pts, Suspended = 0 pts.
    - **Violation Deductions**: 20 pts minus calibrated severity deductions (pest lapses = -8, cooking oil reuse = -8, cold storage = -6, water quality = -5).
    - **Recency**: $\\le 6$ months = 10 pts; 6-12 months = 7 pts; 12-24 months = 4 pts; $> 24$ months = 2 pts.
    
    #### B. Customer Experience Score (0–100 Scale)
    $$\\text{Customer Experience Score} = \\left( \\frac{\\text{Positive Reviews} + 0.5 \\times \\text{Neutral Reviews}}{\\text{Total Reviews}} \\right) \\times 100$$
    
    ### 5. Data Provenance & Academic Disclaimers
    - **100 Kolkata Restaurants**: Real, authentic restaurant listings scraped from public Zomato Kolkata data.
    - **Model Training Corpus**: 13,144 real restaurant reviews from the open Yelp academic research dataset.
    - **Aspect Validation**: Validated against the SemEval restaurant benchmark dataset.
    - **Demo Synthetic Reviews & Safety Logs**: Synthetic reviews and municipal safety audit records were synthetically generated for prototype development and testing.
    """)
