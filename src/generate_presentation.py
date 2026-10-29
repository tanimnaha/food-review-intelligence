# -*- coding: utf-8 -*-
"""Generate Academic Minor Project Presentation for Kolkata FoodLens.

Generates high-fidelity PowerPoint presentation matching Amity University
minor project guidelines, incorporating West Bengal food safety inspections,
NLP aspect-based sentiment analysis, benchmark results, and web architecture.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PPTX = ROOT / "presentation" / "Kolkata_FoodLens_Minor_Project_Presentation.pptx"
TEMPLATE_PPTX = ROOT / "presentation" / "Project_presentation_template.pptx"

# Academic Color Palette
COLOR_NAVY = RGBColor(15, 30, 45)       # #0F1E2D - Primary Dark
COLOR_TEAL = RGBColor(15, 118, 110)     # #0F766E - Accent Teal
COLOR_EMERALD = RGBColor(16, 185, 129)  # #10B981 - Success
COLOR_AMBER = RGBColor(217, 119, 6)     # #D97706 - Warning / Highlight
COLOR_SLATE = RGBColor(71, 85, 105)     # #475569 - Muted Text
COLOR_LIGHT_BG = RGBColor(248, 250, 252)# #F8FAFC - Card BG
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_BORDER = RGBColor(226, 232, 240)

def add_header(slide, title_text, category_text="AMITY UNIVERSITY KOLKATA • B.TECH CSE MINOR PROJECT (ETMN100)"):
    # Header container
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_cat = tf.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(9.5)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_TEAL
    
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY
    p_title.space_before = Pt(3)

def add_card(slide, left, top, width, height, title, items, bg_color=COLOR_LIGHT_BG, border_color=COLOR_BORDER):
    # Shape card
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.2)
    
    # Text
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.2)
    tf.margin_bottom = Inches(0.2)
    
    if title:
        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(13)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_NAVY
        p_title.space_after = Pt(6)
        first_item = True
    else:
        first_item = False
        
    for item in items:
        if first_item and not title:
            p = tf.paragraphs[0]
            first_item = False
        else:
            p = tf.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_NAVY
        p.space_after = Pt(4)

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    # -------------------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_NAVY
    bg1.line.fill.background()
    
    tb1 = slide1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(11.0), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "AMITY SCHOOL OF ENGINEERING & TECHNOLOGY  |  AMITY UNIVERSITY KOLKATA"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_EMERALD
    
    p = tf1.add_paragraph()
    p.text = "Kolkata FoodLens"
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(8)
    
    p = tf1.add_paragraph()
    p.text = "AI-Driven Restaurant Intelligence, Aspect-Based Sentiment Analysis & Food Safety Surveillance"
    p.font.size = Pt(18)
    p.font.bold = False
    p.font.color.rgb = RGBColor(204, 251, 241)
    p.space_before = Pt(4)
    
    p = tf1.add_paragraph()
    p.text = (
        "A Multi-Criteria Decision Support Platform Decoupling Customer Popularity from "
        "Municipal Hygiene Auditing in Kolkata, India"
    )
    p.font.size = Pt(12.5)
    p.font.color.rgb = RGBColor(148, 163, 184)
    p.space_before = Pt(8)
    
    p = tf1.add_paragraph()
    p.text = (
        "Author: Tanim Naha  |  Enrollment: B.Tech Computer Science & Engineering\n"
        "Course: Minor Project (ETMN100)  |  Semester: 5th Semester  |  Academic Year: 2026–2027\n"
        "Faculty Guide: Department of Computer Science & Engineering"
    )
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(28)
    
    # -------------------------------------------------------------------------
    # SLIDE 2: Table of Contents
    # -------------------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Presentation Structure & Roadmap")
    
    toc_items_col1 = [
        ("01", "Problem Motivation", "Conflation of star ratings & recent West Bengal food safety drives"),
        ("02", "Literature Survey", "ABSA foundations, CDC/NYC Health surveillance & Harvard smart inspections"),
        ("03", "System Architecture", "End-to-end multi-layer pipeline: NLP inference to SQLite database"),
        ("04", "Data Engineering", "100 Kolkata listings, 13,144 Yelp corpus, 5,000 synthetic ABSA reviews"),
        ("05", "Sentiment Benchmark", "TF-IDF + Balanced Logistic Regression vs SVM vs Neural MLP"),
    ]
    toc_items_col2 = [
        ("06", "ABSA Engine", "5-Aspect polarity extraction (Food, Service, Hygiene, Ambience, Price)"),
        ("07", "Food Safety Engine", "Weighted municipal compliance scoring with zero-fabrication integrity"),
        ("08", "Context Recommendations", "Multi-criteria ranking blend: 50% Sentiment + 25% Zomato + 15% Safety + 10% Tags"),
        ("09", "Web Application & Live Demo", "Streamlit 9-tab dashboard with real-time SQLite review updates"),
        ("10", "Future Roadmap & References", "Major project expansion: IndicBERT multilingual NLP & automated crawlers"),
    ]
    
    for i, (num, title, desc) in enumerate(toc_items_col1):
        add_card(slide2, Inches(0.8), Inches(1.8 + i * 1.0), Inches(5.6), Inches(0.88), f"{num}. {title}", [desc])
    for i, (num, title, desc) in enumerate(toc_items_col2):
        add_card(slide2, Inches(6.8), Inches(1.8 + i * 1.0), Inches(5.6), Inches(0.88), f"{num}. {title}", [desc])

    # -------------------------------------------------------------------------
    # SLIDE 3: Problem Statement & Local Motivation
    # -------------------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Problem Statement: Conflation of Popularity & Hygiene")
    
    add_card(
        slide3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
        "The Conventional Aggregator Flaw",
        [
            "Aggregators (Zomato, Swiggy, Google) compress diner feedback into a single 1.0–5.0 star score.",
            "Popularity Bias: High food taste scores mathematically drown out severe kitchen hygiene complaints.",
            "A bustling Kolkata biryani restaurant often maintains a 4.3★ rating despite recurring washroom cleanliness or stale food issues.",
            "Entangled Feedback: Diners cannot isolate Food taste from Service promptness or Sanitary compliance.",
            "Information Asymmetry: Consumers lack direct access to objective regulatory inspection records."
        ]
    )
    
    add_card(
        slide3, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
        "West Bengal Food Safety Crackdown & Motivation",
        [
            "Municipal Enforcement Reality: Recent intensive spot inspections across Kolkata and West Bengal (KMC & Health Dept) revealed critical hygiene violations, stale meat, and adulterated cooking oil.",
            "Inspection Bottleneck: Kolkata has over 15,000+ commercial food vendors, but fewer than 60 active municipal food safety inspectors.",
            "Manual audits cannot inspect thousands of eateries daily without automated algorithmic prioritization.",
            "The FoodLens Solution: Decouple Customer Experience from Verified Safety, and provide early-warning NLP surveillance from online consumer reviews to trigger prioritized inspections."
        ],
        border_color=COLOR_TEAL
    )

    # -------------------------------------------------------------------------
    # SLIDE 4: Literature Survey & Academic Context
    # -------------------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Literature Survey & Public Health Foundations")
    
    add_card(
        slide4, Inches(0.8), Inches(1.8), Inches(3.7), Inches(4.8),
        "Aspect-Based Sentiment (ABSA)",
        [
            "Pontiki et al. (SemEval 2014-2016): Defined foundational ABSA tasks for restaurant reviews.",
            "Clause-Level Discourse: Single reviews routinely express mixed sentiments across clauses (e.g. delicious biryani vs dirty tables).",
            "Limitation in Literature: General sentiment models assign a single document polarity, losing actionable aspect signals.",
            "FoodLens Approach: Discourse clause splitting with multi-label aspect classification."
        ]
    )
    
    add_card(
        slide4, Inches(4.8), Inches(1.8), Inches(3.7), Inches(4.8),
        "Smart Health Inspection NLP",
        [
            "Harrison et al. (CDC & NYC Health): Pioneered text classification on unstructured Yelp reviews to predict foodborne illness outbreaks (80% precision).",
            "Glaeser et al. (Harvard Smart Inspections): Demonstrated machine learning prioritizes municipal food inspections 30-40% more effectively than random sampling.",
            "Municipal Translation: Adapting these methodologies for Kolkata's local culinary and regulatory landscape."
        ]
    )
    
    add_card(
        slide4, Inches(8.8), Inches(1.8), Inches(3.7), Inches(4.8),
        "Multi-Criteria Decision Systems",
        [
            "Triantaphyllou (MCDM Theory): Real-world consumer decision-making requires multi-objective trade-offs.",
            "Conflation Hazard: Combining safety with subjective taste produces invalid rankings.",
            "FoodLens Innovation: Explicitly decoupled score triad (Customer Experience, Verified Safety, Confidence Level) with non-stereotypical context matching."
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 5: Proposed Methodology & Architecture
    # -------------------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Proposed Methodology & System Architecture")
    
    add_card(
        slide5, Inches(0.8), Inches(1.8), Inches(3.7), Inches(4.8),
        "1. NLP & Preprocessing Pipeline",
        [
            "Sanitization: Stripping URLs, HTML tags, and non-semantic noise.",
            "Contraction Expansion: 100+ mappings ('wasn't' → 'was not', 'didn't' → 'did not') preventing polarity inversion.",
            "Affective Emoji Retention: Preserves emojis (❤️, 🤢, ⭐, 😋) carrying dense sentiment signals.",
            "Stratified Partitioning: 80% Train (10,515), 10% Val (1,314), 10% Test (1,315) stratified by sentiment label."
        ]
    )
    
    add_card(
        slide5, Inches(4.8), Inches(1.8), Inches(3.7), Inches(4.8),
        "2. Sentiment & ABSA Modeling",
        [
            "Feature Engineering: Sub-linear TF-IDF (1–3 n-grams, 10,000 features).",
            "Class Imbalance Handling: Balanced inverse-frequency class weighting (heuristic penalty for rare negatives).",
            "Probability Calibration: Multinomial logistic sigmoid calibration yielding calibrated confidence %.",
            "Clause-Level ABSA: Discourse segmentation + keyword attribution across 5 aspects (Food, Service, Hygiene, Ambience, Price)."
        ]
    )
    
    add_card(
        slide5, Inches(8.8), Inches(1.8), Inches(3.7), Inches(4.8),
        "3. Safety Engine & Storage",
        [
            "Audit Scoring Algorithm: 40% Outcome + 30% Licence + 20% Violation Deductions + 10% Recency.",
            "Integrity Rule: Output 'Safety data unavailable' when no municipal audit exists. Never fabricate scores.",
            "Full-Stack Web UI: 9-Tab Streamlit master application.",
            "SQLite Persistence: Stores live diner submissions and triggers real-time dynamic re-scoring."
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 6: Experimental Setup & Datasets
    # -------------------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Experimental Setup & Dataset Provenance")
    
    add_card(
        slide6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
        "Dataset Provenance & Class Imbalance",
        [
            "100 Real Kolkata Restaurants: Authentic listings scraped from Zomato Kolkata across major food hubs (Park Street, Salt Lake, Esplanade, New Town, etc.).",
            "13,144 Real Yelp Training Reviews: Open academic benchmark corpus used for rigorous sentiment classifier training.",
            "Real-World Class Imbalance in Training Corpus:\n  • Positive: 9,848 (74.9%)\n  • Neutral: 2,553 (19.4%)\n  • Negative: 743 (5.7% minority class)",
            "5,000 Synthetic Kolkata Reviews: Calibrated synthetic corpus annotated with 5 fine-grained aspect labels.",
            "107 Municipal Audit Logs: Simulated inspection records (84 audited establishments, 16 un-audited)."
        ]
    )
    
    add_card(
        slide6, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
        "Computational Setup & Implementation Stack",
        [
            "Programming Language & Runtime: Python 3.12 64-bit on Apple Silicon.",
            "Machine Learning Frameworks: Scikit-learn 1.9.1, NumPy 2.5.4, Pandas 2.3.3, Joblib 1.6.0.",
            "Web Framework & Visualization: Streamlit 1.66.1, Plotly 6.9.0.",
            "Database: SQLite 3 embedded relational storage with foreign key indexing.",
            "Reproducibility Protocol: Seed fixed at 42 across all data splitting, model initialization, and evaluation passes.",
            "Cloud Deployment: Deployed to Streamlit Community Cloud with automated GitHub webhook synchronization."
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 7: Benchmark Results & Discussion
    # -------------------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Benchmark Results & Model Evaluation")
    
    # Embed Table
    rows = 5
    cols = 7
    left = Inches(0.8)
    top = Inches(1.8)
    width = Inches(11.7)
    height = Inches(2.2)
    
    table_shape = slide7.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    table.columns[0].width = Inches(2.9)
    table.columns[1].width = Inches(1.4)
    table.columns[2].width = Inches(1.4)
    table.columns[3].width = Inches(1.5)
    table.columns[4].width = Inches(1.5)
    table.columns[5].width = Inches(1.5)
    table.columns[6].width = Inches(1.5)
    
    headers = ["Model Architecture", "Accuracy", "Macro-F1", "Negative F1", "Neutral F1", "Positive F1", "Status"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = COLOR_WHITE
            p.alignment = PP_ALIGN.CENTER
            
    data = [
        ["TF-IDF + Logistic Regression (Balanced)", "71.18%", "0.6537", "0.5079", "0.7333", "0.7200", "★ WINNER"],
        ["TF-IDF + Linear SVM (Calibrated, Balanced)", "74.07%", "0.6376", "0.4272", "0.7853", "0.7004", "Baseline"],
        ["TF-IDF + Multi-Layer Perceptron (MLP)", "75.06%", "0.5341", "0.0779", "0.7958", "0.7286", "Imbalance Collapse"],
        ["TF-IDF + Complement Naive Bayes", "71.86%", "0.4901", "0.0000", "0.7582", "0.7122", "Failed Negatives"],
    ]
    
    for i, row in enumerate(data, 1):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = val
            cell.fill.solid()
            if i == 1:
                cell.fill.fore_color.rgb = RGBColor(240, 253, 250)
            else:
                cell.fill.fore_color.rgb = COLOR_WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(9.5)
                p.font.color.rgb = COLOR_TEAL if (i == 1 and j == 6) else COLOR_NAVY
                p.font.bold = (i == 1)
                p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT

    add_card(
        slide7, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.6),
        "Key Evaluation Insights & Winner Rationale",
        [
            "Why Logistic Regression Won: Achieved the highest Macro-F1 (0.6537) and crucial Negative F1 (0.5079) across 1,315 held-out test reviews.",
            "MLP & Naive Bayes Failure: While MLP achieved 75.06% raw accuracy, it scored 0.0779 on negative reviews, ignoring complaints.",
            "Probability Calibration: Logistic Regression outputs calibrated posterior probabilities powering user confidence gauges."
        ]
    )
    
    add_card(
        slide7, Inches(6.8), Inches(4.3), Inches(5.6), Inches(2.6),
        "Aspect-Based Validation (SemEval Benchmark)",
        [
            "Evaluated on 86 SemEval aspect benchmark samples with clause discourse splitting.",
            "Overall Aspect Macro-F1: 0.865 across Food, Service, Hygiene, Ambience, Price.",
            "Sanity Check: 'Biryani was excellent, but tables were dirty and service was slow' → Food: Positive, Hygiene: Negative, Service: Negative."
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 8: Context Recommendations & Full-Stack Application
    # -------------------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Context Recommendations & Interactive Web App")
    
    add_card(
        slide8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
        "Multi-Criteria Dining Recommendation Blend",
        [
            "Context-Driven: Non-stereotypical matching across dining contexts (Family, Students, Date Night, Groups, Solo).",
            "Multi-Criteria Formula:\n  Rank = 50% Sentiment + 25% Zomato + 15% Safety + 10% Suitability",
            "Missing Safety Re-Weighting:\n  When audit logs are unavailable, the 15% safety weight is proportionally reallocated: 60% Sentiment, 30% Zomato, 10% Tags.",
            "No Artificial Penalties: Un-audited restaurants are neither penalized nor gifted unearned compliance scores."
        ]
    )
    
    add_card(
        slide8, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
        "Interactive 9-Tab Streamlit Master Dashboard",
        [
            "Tab 1: 🔍 Kolkata Restaurant Directory (100 listings, 3-score triads)",
            "Tab 2: 🏛️ Restaurant Deep Dive & Submit Review (Aspect radar, live SQLite update)",
            "Tab 3: 🎯 Contextual Dining Recommendations (Multi-criteria ranking)",
            "Tab 4: ⚖️ Side-by-Side Restaurant Compare (Radar overlay & KPI table)",
            "Tab 5: 🛡️ Food Safety & Hygiene Surveillance (Early warning inspection triggers)",
            "Tab 6: ✳️ Sentiment & Aspect Studio (Real-time single review inference)",
            "Tab 7: ▦ Batch Intelligence Center (Bulk CSV processing & safety flagging)",
            "Tab 8: 📊 Model Benchmark & Evaluation Lab (Confusion matrices & charts)",
            "Tab 9: 📖 Methodology & Academic Model Card (Formulas & Provenance)"
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 9: Future Direction Towards Major Project
    # -------------------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Future Directions Towards Major Project")
    
    add_card(
        slide9, Inches(0.8), Inches(1.8), Inches(3.7), Inches(4.8),
        "Phase 1: Multilingual & Code-Mixed NLP",
        [
            "Kolkata Linguistic Landscape: Diners frequently review in colloquial Bengali or Banglish (e.g. 'Khawata khub bhalo kintu washroom nongra').",
            "Model Upgrade: Fine-tune BanglaBERT or IndicBERT on code-mixed social media & food review corpora.",
            "Cross-Lingual Transfer: Zero-shot aspect extraction across Bengali and English."
        ]
    )
    
    add_card(
        slide9, Inches(4.8), Inches(1.8), Inches(3.7), Inches(4.8),
        "Phase 2: Live Regulatory Integration",
        [
            "Automated Web Scrapers: Daily crawler querying the West Bengal Food Safety Portal (FSSAI compliance database).",
            "License Verification: Real-time OCR validation of FSSAI display certificates from kitchen photos.",
            "Official Inspection Integration: Real-time municipal API integration dispatching priority inspection notices."
        ]
    )
    
    add_card(
        slide9, Inches(8.8), Inches(1.8), Inches(3.7), Inches(4.8),
        "Phase 3: Deep ABSA & Mobile PWA",
        [
            "Transformer Architecture: Multi-task DeBERTa-v3 model with shared representations for aspect term extraction and polarity.",
            "Mobile PWA: Progressive Web Application with device GPS geolocation proximity ranking.",
            "Crowdsourced Photo Audits: Computer vision hygiene scoring of customer-uploaded kitchen and dining photos."
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 10: Conclusion & References
    # -------------------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Conclusion & Academic References")
    
    add_card(
        slide10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
        "Project Conclusions",
        [
            "Successfully built and deployed Kolkata FoodLens, combining 100 real Kolkata restaurant profiles with NLP sentiment and municipal food safety surveillance.",
            "Proved that TF-IDF with balanced class weights significantly outperforms unweighted neural networks when minority negative reviews represent critical health warnings.",
            "Decoupled popularity from safety: Solved the fundamental aggregator flaw where popular taste scores mask sanitary lapses.",
            "Established an early-warning public health inspection pipeline inspired by CDC and Harvard methodologies tailored for West Bengal municipal governance."
        ]
    )
    
    add_card(
        slide10, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
        "Selected Academic References",
        [
            "1. Pontiki, M., et al. (2014-2016). 'SemEval: Aspect Based Sentiment Analysis.' Proceedings of International Workshop on Semantic Evaluation.",
            "2. Harrison, C., et al. (2014). 'Using Online Reviews by Restaurant Patrons to Identify Unreported Cases of Foodborne Illness.' CDC MMWR, 63(20), 441-445.",
            "3. Glaeser, E. L., et al. (2016). 'Nowcasting the Local Economy: Using Yelp Data to Measure Economic Activity.' Harvard Business School Working Paper.",
            "4. Food Safety and Standards Authority of India (FSSAI). 'Food Safety and Standards (Licensing and Registration of Food Businesses) Regulations.'",
            "5. Pedregosa, F., et al. (2011). 'Scikit-learn: Machine Learning in Python.' JMLR, 12, 2825-2830."
        ]
    )
    
    prs.save(str(OUTPUT_PPTX))
    prs.save(str(TEMPLATE_PPTX))
    print(f"Successfully generated PowerPoint presentations:\n - {OUTPUT_PPTX}\n - {TEMPLATE_PPTX}")

if __name__ == "__main__":
    build_presentation()
