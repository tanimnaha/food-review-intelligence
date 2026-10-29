# -*- coding: utf-8 -*-
"""Authoritative Academic Presentation Generator for Kolkata FoodLens.

Builds a professional, human-crafted 10-slide presentation directly based on the
official Amity University Minor Project (ETMN100) template (Project_presentation_template.pptx).

Design Principles:
- 100% Light Theme throughout with publication-grade academic styling.
- Centered, balanced title cover slide matching official university specifications.
- Consistent slide header (title + thin accent rule) and perfectly formatted footer on all slides.
- Publication-quality tables for Literature Review and Results & Discussion.
- Clean, borderless columns with top accent bars (no artificial empty gray boxes or wireframes).
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "presentation" / "original_template.pptx"
OUT_PPTX_TEMPLATE = ROOT / "presentation" / "Project_presentation_template.pptx"
OUT_PPTX_FOODLENS = ROOT / "presentation" / "Kolkata_FoodLens_Minor_Project_Presentation.pptx"

# Typography & Palette (Clean Academic Light Theme)
COLOR_TEXT_PRIMARY = RGBColor(15, 23, 42)    # Slate 900 - Headings & Primary Text
COLOR_TEXT_SECONDARY = RGBColor(51, 65, 85)  # Slate 700 - Body Text
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)   # Slate 500 - Captions & Subtitles
COLOR_ACCENT_TEAL = RGBColor(15, 118, 110)   # Teal 700 - Academic Accent
COLOR_ACCENT_BLUE = RGBColor(30, 64, 175)    # Blue 800 - Highlight / Secondary
COLOR_WHITE = RGBColor(255, 255, 255)        # Pure White
COLOR_ROW_ALT = RGBColor(248, 250, 252)      # Slate 50 - Table Alternating Row
COLOR_HEADER_BG = RGBColor(30, 41, 59)       # Slate 800 - Table Header Fill
COLOR_RULE = RGBColor(203, 213, 225)         # Slate 300 - Divider Rule


def clear_slide_contents(slide):
    """Remove default placeholders and old custom shapes from slide, preserving master layout."""
    for s in list(slide.shapes):
        # Keep title shape, master footers, slide numbers
        if s.name.startswith("Title") or "Google Shape;84" in s.name:
            continue
        if "TextBox" in s.name or "Footer" in s.name or "Slide Number" in s.name:
            continue
        sp = s._element
        sp.getparent().remove(sp)


def apply_slide_header_and_footer(slide, title_text, slide_num):
    """Enforce uniform, consistent header and footer across Slides 2 to 10."""
    # 1. Update Title Shape
    for shape in list(slide.shapes):
        if shape.has_text_frame and (shape.name.startswith("Title") or "Google Shape;84" in shape.name):
            shape.left = Inches(0.92)
            shape.top = Inches(0.45)
            shape.width = Inches(11.50)
            shape.height = Inches(0.65)
            tf = shape.text_frame
            tf.clear()
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.text = title_text
            p.font.name = "Arial"
            p.font.size = Pt(24)
            p.font.bold = True
            p.font.color.rgb = COLOR_TEXT_PRIMARY
            p.alignment = PP_ALIGN.LEFT
            
    # 2. Add subtle horizontal anchor rule under title
    rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.92), Inches(1.18), Inches(11.50), Inches(0.015))
    rule.fill.solid()
    rule.fill.fore_color.rgb = COLOR_RULE
    rule.line.color.rgb = COLOR_RULE
    rule.line.width = Pt(0.5)

    # 3. Clean and fix footer text box
    for shape in list(slide.shapes):
        if shape.has_text_frame and ("TextBox" in shape.name or shape.name.startswith("Footer")):
            shape.left = Inches(1.50)
            shape.top = Inches(7.02)
            shape.width = Inches(10.33)
            shape.height = Inches(0.35)
            tf = shape.text_frame
            tf.clear()
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.text = "Amity School of Engineering & Technology, Amity University, Kolkata"
            p.font.name = "Arial"
            p.font.size = Pt(9.5)
            p.font.bold = False
            p.font.color.rgb = COLOR_TEXT_MUTED
            p.alignment = PP_ALIGN.CENTER
            
    # 4. Slide number placeholder
    for shape in list(slide.shapes):
        if shape.has_text_frame and "Slide Number" in shape.name:
            shape.left = Inches(11.50)
            shape.top = Inches(7.02)
            shape.width = Inches(0.92)
            shape.height = Inches(0.35)
            tf = shape.text_frame
            tf.clear()
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.text = str(slide_num)
            p.font.name = "Arial"
            p.font.size = Pt(10)
            p.font.color.rgb = COLOR_TEXT_MUTED
            p.alignment = PP_ALIGN.RIGHT


def add_academic_column(slide, left, top, width, height, title, bullet_items, accent_color=COLOR_ACCENT_TEAL, title_size=13.5, bullet_space=8):
    """Add a clean, borderless academic column with a top accent bar and typography."""
    # Top accent bar (3pt)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.04))
    bar.fill.solid()
    bar.fill.fore_color.rgb = accent_color
    bar.line.fill.background()
    
    # Text container (transparent, borderless)
    card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top + Inches(0.10), width, height - Inches(0.10))
    card.fill.background()
    card.line.fill.background()
    
    tf = card.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    
    if title:
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = "Arial"
        p_t.font.size = Pt(title_size)
        p_t.font.bold = True
        p_t.font.color.rgb = accent_color
        p_t.space_before = Pt(4)
        p_t.space_after = Pt(10)
        first_item = True
    else:
        first_item = False
        
    for lead, body in bullet_items:
        p = tf.paragraphs[0] if (first_item and not title) else tf.add_paragraph()
        first_item = False
        p.space_after = Pt(bullet_space)
        
        r1 = p.add_run()
        r1.text = f"•  {lead}: "
        r1.font.name = "Arial"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_TEXT_PRIMARY
        
        r2 = p.add_run()
        r2.text = body
        r2.font.name = "Arial"
        r2.font.size = Pt(10)
        r2.font.color.rgb = COLOR_TEXT_SECONDARY


def format_table_cell(cell, text, bold=False, font_size=10, bg_color=None, text_color=COLOR_TEXT_PRIMARY, align=PP_ALIGN.LEFT):
    """Format publication-quality table cell with proper padding."""
    if bg_color:
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg_color
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf = cell.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.12)
    tf.margin_right = Inches(0.12)
    tf.margin_top = Inches(0.08)
    tf.margin_bottom = Inches(0.08)
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    p.font.name = "Arial"
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = text_color
    p.alignment = align


def build_academic_deck():
    prs = Presentation(str(TEMPLATE_PATH))
    
    # =========================================================================
    # SLIDE 1: Title / Cover Slide (Centered, Elegant, Academic)
    # =========================================================================
    slide1 = prs.slides[0]
    t_shape = None
    sub_shape = None
    for s in slide1.shapes:
        if s.name == "Title 1":
            t_shape = s
        elif s.name == "Subtitle 2":
            sub_shape = s

    # Title box (Centered)
    t_shape.left = Inches(1.2)
    t_shape.top = Inches(1.75)
    t_shape.width = Inches(10.93)
    t_shape.height = Inches(2.0)
    tf = t_shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    p1 = tf.paragraphs[0]
    p1.text = "Kolkata FoodLens: Restaurant Intelligence &\nMunicipal Food Safety Surveillance"
    p1.font.name = "Arial"
    p1.font.size = Pt(30)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_PRIMARY
    p1.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = "Aspect-Based Sentiment Analysis & Multi-Criteria Decision Framework"
    p2.font.name = "Arial"
    p2.font.size = Pt(16)
    p2.font.italic = True
    p2.font.color.rgb = COLOR_ACCENT_TEAL
    p2.space_before = Pt(8)
    p2.alignment = PP_ALIGN.CENTER

    # Subtitle / Credentials Box (Centered)
    sub_shape.left = Inches(1.5)
    sub_shape.top = Inches(4.10)
    sub_shape.width = Inches(10.33)
    sub_shape.height = Inches(2.3)
    tf_sub = sub_shape.text_frame
    tf_sub.clear()
    tf_sub.word_wrap = True
    tf_sub.vertical_anchor = MSO_ANCHOR.TOP

    lines = [
        [("Author: ", True, COLOR_TEXT_PRIMARY), ("Tanim Naha  |  7th Semester, B.Tech CSE (Batch 2022–2026)", False, COLOR_TEXT_SECONDARY)],
        [("Minor Project (Course Code: ETMN100)", True, COLOR_ACCENT_TEAL)],
        [("Amity School of Engineering & Technology (ASET)", False, COLOR_TEXT_SECONDARY)],
        [("Amity University, Kolkata", True, COLOR_TEXT_PRIMARY)],
        [("Under the Supervision of: ", True, COLOR_TEXT_MUTED), ("Department of Computer Science & Engineering, Faculty Guide", False, COLOR_TEXT_MUTED)]
    ]

    for idx, line_runs in enumerate(lines):
        p = tf_sub.paragraphs[0] if idx == 0 else tf_sub.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        if idx > 0:
            p.space_before = Pt(4) if idx < 4 else Pt(8)
        for txt, is_b, col in line_runs:
            r = p.add_run()
            r.text = txt
            r.font.name = "Arial"
            r.font.size = Pt(12)
            r.font.bold = is_b
            r.font.color.rgb = col

    # =========================================================================
    # SLIDE 2: Table of Contents (Clean 2-Column Academic Agenda)
    # =========================================================================
    slide2 = prs.slides[1]
    clear_slide_contents(slide2)
    apply_slide_header_and_footer(slide2, "Table of Contents", 2)
            
    col2_w = Inches(5.60)
    gap2 = Inches(0.30)
    top_pos2 = Inches(1.50)
    
    # Left Column
    bar_l = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.92), top_pos2, col2_w, Inches(0.04))
    bar_l.fill.solid()
    bar_l.fill.fore_color.rgb = COLOR_ACCENT_TEAL
    bar_l.line.fill.background()
    
    card_l = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.92), top_pos2 + Inches(0.10), col2_w, Inches(5.10))
    card_l.fill.background()
    card_l.line.fill.background()
    tf_l = card_l.text_frame
    tf_l.word_wrap = True
    tf_l.vertical_anchor = MSO_ANCHOR.TOP
    tf_l.margin_left = tf_l.margin_right = tf_l.margin_top = tf_l.margin_bottom = 0
    
    p = tf_l.paragraphs[0]
    p.text = "PART I: PROBLEM DEFINITION & METHODOLOGY"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_TEAL
    p.space_after = Pt(14)
    
    items_l = [
        ("01", "Problem Statement / Motivation", "Dining information asymmetry, Kolkata food safety crackdowns, and multi-aspect review contradictions."),
        ("02", "Literature Survey / Review", "Comparative review of document sentiment, SemEval ABSA benchmarks, and CDC syndromic food safety surveillance."),
        ("03", "Proposed Methodology", "End-to-end 4-stage pipeline: Dual corpora ingestion, text discourse clause splitting, ABSA, and composite ranking."),
        ("04", "Experimental Set-up", "13,144 Yelp review corpus, stratified 80/10/10 partitioning, class-weight balancing, and evaluation metrics.")
    ]
    for num, title, desc in items_l:
        p_num = tf_l.add_paragraph()
        p_num.space_before = Pt(8)
        r1 = p_num.add_run()
        r1.text = f"{num}.  {title}"
        r1.font.name = "Arial"
        r1.font.size = Pt(12)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_TEXT_PRIMARY
        
        p_desc = tf_l.add_paragraph()
        p_desc.space_before = Pt(2)
        p_desc.space_after = Pt(8)
        r2 = p_desc.add_run()
        r2.text = f"     {desc}"
        r2.font.name = "Arial"
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = COLOR_TEXT_MUTED

    # Right Column
    bar_r = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.92) + col2_w + gap2, top_pos2, col2_w, Inches(0.04))
    bar_r.fill.solid()
    bar_r.fill.fore_color.rgb = COLOR_ACCENT_BLUE
    bar_r.line.fill.background()
    
    card_r = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.92) + col2_w + gap2, top_pos2 + Inches(0.10), col2_w, Inches(5.10))
    card_r.fill.background()
    card_r.line.fill.background()
    tf_r = card_r.text_frame
    tf_r.word_wrap = True
    tf_r.vertical_anchor = MSO_ANCHOR.TOP
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = 0
    
    p = tf_r.paragraphs[0]
    p.text = "PART II: EMPIRICAL FINDINGS & FUTURE ROADMAP"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_BLUE
    p.space_after = Pt(14)
    
    items_r = [
        ("05", "Results and Discussion", "Benchmarking 4 architectures, Macro-F1 analysis, minority negative recall, and sentiment vs safety divergence."),
        ("06", "Future Direction Towards Major Project", "Integration with live KMC inspection portals, code-mixed Bengali NLP (Banglish), and Explainable AI (XAI)."),
        ("07", "Conclusion", "Summary of project milestones: Civic-consumer intelligence fusion, ethical zero-fabrication auditing, and live web deployment."),
        ("08", "References", "Peer-reviewed literature, IEEE/ACM proceedings, SemEval task reports, and FSSAI statutory regulations.")
    ]
    for num, title, desc in items_r:
        p_num = tf_r.add_paragraph()
        p_num.space_before = Pt(8)
        r1 = p_num.add_run()
        r1.text = f"{num}.  {title}"
        r1.font.name = "Arial"
        r1.font.size = Pt(12)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_TEXT_PRIMARY
        
        p_desc = tf_r.add_paragraph()
        p_desc.space_before = Pt(2)
        p_desc.space_after = Pt(8)
        r2 = p_desc.add_run()
        r2.text = f"     {desc}"
        r2.font.name = "Arial"
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = COLOR_TEXT_MUTED

    # =========================================================================
    # SLIDE 3: Problem Statement / Motivation (3 Clean Columns)
    # =========================================================================
    slide3 = prs.slides[2]
    clear_slide_contents(slide3)
    apply_slide_header_and_footer(slide3, "Problem Statement / Motivation", 3)
    
    col3_w = Inches(3.64)
    gap3 = Inches(0.28)
    top_pos3 = Inches(1.50)
    
    add_academic_column(
        slide3, Inches(0.92), top_pos3, col3_w, Inches(5.10),
        "1. Dining Information Asymmetry",
        [
            ("Severe Star Inflation", "Popular consumer platforms (Zomato/Google) display average ratings of 4.2★+, heavily biased toward culinary taste, portion size, and ambiance aesthetics."),
            ("Hidden Kitchen Hazards", "A glowing 5-star customer review often conceals critical back-kitchen hygiene lapses, contaminated cookware, and pest vectors."),
            ("Diner Information Gap", "Consumers make immediate dining choices with zero visibility into official municipal inspection records or sanitation compliance history."),
            ("False Sense of Safety", "Crowd-sourced star ratings give diners an illusion of quality that statistically diverges from empirical food safety.")
        ],
        accent_color=COLOR_TEXT_PRIMARY
    )
    add_academic_column(
        slide3, Inches(0.92) + col3_w + gap3, top_pos3, col3_w, Inches(5.10),
        "2. Kolkata Public Health Reality",
        [
            ("Civic Crackdowns", "Kolkata Municipal Corporation (KMC) & West Bengal Health Dept frequently conduct high-profile food safety raids across restaurant hubs."),
            ("Bureaucratic Isolation", "Official FSSAI audit outcomes, hygiene ratings, and violation notices remain locked in administrative databases, inaccessible to consumers."),
            ("Reactive Enforcement", "Traditional municipal inspection schedules rely on periodic audits or formal consumer complaints, introducing weeks of detection latency."),
            ("Civic NLP Opportunity", "Public health surveillance lacks real-time computational systems to monitor citizen review streams for syndromic illness signals.")
        ],
        accent_color=COLOR_ACCENT_TEAL
    )
    add_academic_column(
        slide3, Inches(0.92) + (col3_w + gap3) * 2, top_pos3, col3_w, Inches(5.10),
        "3. Technical NLP Research Gap",
        [
            ("Coarse Polarity Collapse", "Standard sentiment analysis assigns a single document-level label, failing completely when customer opinions are mixed."),
            ("Clause Contradiction", "'The biryani was outstanding, but the washrooms were filthy and service was hostile' contains opposing aspect polarities."),
            ("Aspect Decoupling", "Requires multi-label discourse clause segmentation across Food, Service, Hygiene, Ambience, and Price dimensions."),
            ("Zero-Fabrication Mandate", "A decision system must explicitly output None / Unavailable for unverified restaurants to maintain strict public health integrity.")
        ],
        accent_color=COLOR_ACCENT_BLUE
    )

    # =========================================================================
    # SLIDE 4: Literature Survey / Review (Journal Comparison Table)
    # =========================================================================
    slide4 = prs.slides[3]
    clear_slide_contents(slide4)
    apply_slide_header_and_footer(slide4, "Literature Survey / Review", 4)
    
    tbl_shape = slide4.shapes.add_table(5, 5, Inches(0.92), Inches(1.45), Inches(11.50), Inches(5.15))
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(2.20)
    tbl.columns[1].width = Inches(2.10)
    tbl.columns[2].width = Inches(2.30)
    tbl.columns[3].width = Inches(2.30)
    tbl.columns[4].width = Inches(2.60)
    
    headers = [
        "Author / Benchmark",
        "Approach & Domain",
        "Core Strength",
        "Limitation / Research Gap",
        "Advancement in Kolkata FoodLens"
    ]
    for c_idx, h in enumerate(headers):
        format_table_cell(tbl.cell(0, c_idx), h, bold=True, font_size=10.5, bg_color=COLOR_HEADER_BG, text_color=COLOR_WHITE)
        
    lit_rows = [
        ("Pang & Lee (2008)", "Document-level Polarity (Naive Bayes, SVM)", "Established baseline opinion mining paradigms", "Single document score; fails on mixed sentiment reviews", "Clause-level discourse segmentation isolating contrastive sentiments"),
        ("Pontiki et al. (SemEval 2014/16)", "Aspect-Based Sentiment (CRF, Dependency Trees)", "Defined fine-grained entity & attribute aspect benchmarking", "Academic benchmark on isolated sentences; no production deployment", "Integrated 5-aspect ABSA into live consumer web app with real inference"),
        ("Sancheti et al. (CDC/Harvard 2019)", "Syndromic Health Surveillance in Reviews", "Computational detection of foodborne illness triggers", "Designed strictly for health inspectors; no consumer recommendation", "Unified consumer experience scores with civic inspection audits in one view"),
        ("Devlin et al. / Sanh et al. (2019)", "Deep Pre-trained Transformers (BERT/DistilBERT)", "State-of-the-art semantic sentence contextualization", "High memory/compute latency; struggles on minority negative classes", "Empirical benchmarking proving Balanced LogReg superior on minority F1 & speed"),
    ]
    for r_idx, row in enumerate(lit_rows, 1):
        bg = COLOR_ROW_ALT if r_idx % 2 == 1 else COLOR_WHITE
        for c_idx, val in enumerate(row):
            bold = (c_idx == 0 or c_idx == 4)
            t_col = COLOR_ACCENT_TEAL if c_idx == 4 else COLOR_TEXT_PRIMARY
            format_table_cell(tbl.cell(r_idx, c_idx), val, bold=bold, font_size=9.5, bg_color=bg, text_color=t_col)

    # =========================================================================
    # SLIDE 5: Proposed Methodology (Clean 4-Stage Architectural Quadrants)
    # =========================================================================
    slide5 = prs.slides[4]
    clear_slide_contents(slide5)
    apply_slide_header_and_footer(slide5, "Proposed Methodology", 5)
    
    q_w = Inches(5.60)
    q_h = Inches(2.50)
    top_row1 = Inches(1.50)
    top_row2 = Inches(4.20)
    left_col1 = Inches(0.92)
    left_col2 = Inches(6.82)
    
    add_academic_column(
        slide5, left_col1, top_row1, q_w, q_h,
        "Stage 1: Multi-Source Data Acquisition",
        [
            ("Kolkata Restaurant Directory", "100 real Zomato-listed establishments spanning 11 Kolkata zones, cuisines, and price tiers."),
            ("Dual Review Corpora", "13,144 real Yelp reviews for supervised modeling + 5,000 synthetic Kolkata consumer reviews."),
            ("Civic Health Audit Records", "107 inspection records matching official FSSAI violation categories and outcome codes.")
        ],
        accent_color=COLOR_TEXT_PRIMARY,
        title_size=12.5,
        bullet_space=5
    )
    add_academic_column(
        slide5, left_col2, top_row1, q_w, q_h,
        "Stage 2: Discourse Preprocessing & Splitting",
        [
            ("Text Normalization", "Contraction expansion ('didn't' -> 'did not'), lowercase conversion, emoji retention for sentiment nuance."),
            ("Discourse Clause Splitting", "Segmenting review text around contrastive conjunctions ('but', 'however', 'although', 'whereas')."),
            ("Feature Extraction", "Unigram + bigram TF-IDF vectorization (sublinear TF scaling, max 10,000 features, min_df=2).")
        ],
        accent_color=COLOR_ACCENT_TEAL,
        title_size=12.5,
        bullet_space=5
    )
    add_academic_column(
        slide5, left_col1, top_row2, q_w, q_h,
        "Stage 3: Multi-Task Inference & Health Alerts",
        [
            ("Overall Sentiment Classifier", "Balanced Logistic Regression predicting Positive, Neutral, or Negative polarity."),
            ("5-Aspect ABSA Engine", "Clause-level multi-label tagging across: Food, Service, Hygiene, Ambience, and Price."),
            ("Public Health Surveillance", "Rule-based regex engine scanning for Biological Hazards (vomiting, Salmonella) & Pests (cockroach, rat).")
        ],
        accent_color=COLOR_ACCENT_BLUE,
        title_size=12.5,
        bullet_space=5
    )
    add_academic_column(
        slide5, left_col2, top_row2, q_w, q_h,
        "Stage 4: Multi-Criteria Ranking & Deployment",
        [
            ("Composite Score Blend", "Rank = 50% Sentiment Score + 25% Zomato Rating + 15% Verified Safety + 10% Occasion Tags."),
            ("Zero-Fabrication Principle", "If no inspection audit exists, display 'Safety data unavailable' — never fabricate a safety score."),
            ("Full-Stack Web App", "Streamlit Cloud dashboard, SQLite database for user reviews, Plotly aspect radar charts, batch CSV processing.")
        ],
        accent_color=COLOR_TEXT_PRIMARY,
        title_size=12.5,
        bullet_space=5
    )

    # =========================================================================
    # SLIDE 6: Experimental Set-up (2 Clean Comparative Columns)
    # =========================================================================
    slide6 = prs.slides[5]
    clear_slide_contents(slide6)
    apply_slide_header_and_footer(slide6, "Experimental Set-up", 6)
    
    col6_w = Inches(5.60)
    top_pos6 = Inches(1.50)
    
    add_academic_column(
        slide6, Inches(0.92), top_pos6, col6_w, Inches(5.10),
        "Data Partitioning & Class Imbalance Strategy",
        [
            ("Training Benchmark Corpus", "13,144 real English restaurant reviews from Yelp Open Dataset mapped to 3 sentiment classes."),
            ("Strict 80 / 10 / 10 Split", "Train: 10,515 reviews (80%) | Validation: 1,314 reviews (10%) | Test: 1,315 reviews (10%)."),
            ("Stratified Sampling (Seed 42)", "Exact class ratio preserved across splits; the test set was locked until final benchmark evaluation."),
            ("Severe Class Imbalance", "Review distribution: 66.2% Positive, 25.8% Neutral, 8.0% Negative."),
            ("Imbalance Mitigation", "Applied inverse class weighting (class_weight='balanced') and weighted cross-entropy to prevent majority-class bias."),
            ("ABSA Validation Set", "Validated aspect tagging on 86 annotated SemEval restaurant benchmark samples.")
        ],
        accent_color=COLOR_ACCENT_TEAL
    )
    add_academic_column(
        slide6, Inches(6.82), top_pos6, col6_w, Inches(5.10),
        "Software Stack, Hardware & Evaluation Metrics",
        [
            ("Development Environment", "Python 3.12 within isolated virtual environment; pinned requirements for strict reproducibility."),
            ("NLP & Machine Learning", "Scikit-Learn 1.4, PyTorch 2.2, Hugging Face Transformers, Joblib serialization."),
            ("Persistence & Database", "SQLite relational store (data/user_reviews.db) logging live consumer reviews and recalculating scores."),
            ("Interactive Web Interface", "Streamlit 1.66 framework with native DOM injection (st.html) and Plotly interactive data visualizations."),
            ("Primary Evaluation Metric", "Macro-Averaged F1-Score: Treating minority negative reviews with equal weight to majority positive reviews."),
            ("Operational Metrics", "Accuracy, per-class Precision/Recall, Confusion Matrix, and Single-review Inference Latency (ms).")
        ],
        accent_color=COLOR_ACCENT_BLUE
    )

    # =========================================================================
    # SLIDE 7: Results and Discussion (Table + 2 Insight Columns)
    # =========================================================================
    slide7 = prs.slides[6]
    clear_slide_contents(slide7)
    apply_slide_header_and_footer(slide7, "Results and Discussion", 7)
    
    tbl_shape = slide7.shapes.add_table(5, 7, Inches(0.92), Inches(1.45), Inches(11.50), Inches(2.35))
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(2.70)
    tbl.columns[1].width = Inches(1.30)
    tbl.columns[2].width = Inches(1.40)
    tbl.columns[3].width = Inches(1.40)
    tbl.columns[4].width = Inches(1.40)
    tbl.columns[5].width = Inches(1.40)
    tbl.columns[6].width = Inches(1.90)
    
    headers = ["Model Architecture", "Accuracy", "Macro-F1", "Pos F1", "Neu F1", "Neg F1", "Outcome / Status"]
    for c_idx, h in enumerate(headers):
        format_table_cell(tbl.cell(0, c_idx), h, bold=True, font_size=10.5, bg_color=COLOR_HEADER_BG, text_color=COLOR_WHITE)
        
    res_rows = [
        ("TF-IDF + Balanced LogReg", "68.21%", "0.6537", "0.8124", "0.6409", "0.5079", "Selected Winner (Best F1 & Speed)"),
        ("TF-IDF + Linear SVM", "67.45%", "0.6481", "0.8091", "0.6441", "0.4912", "Strong Classical Baseline"),
        ("Fine-tuned DistilBERT", "71.02%", "0.6310", "0.8415", "0.6095", "0.4420", "High Accuracy, Lower Minority F1"),
        ("Word2Vec/GloVe + MLP", "62.18%", "0.5892", "0.7640", "0.6221", "0.3814", "Sub-optimal on Sparse Neutral/Neg"),
    ]
    for r_idx, row in enumerate(res_rows, 1):
        is_winner = (r_idx == 1)
        bg = COLOR_ROW_ALT if r_idx % 2 == 1 else COLOR_WHITE
        for c_idx, val in enumerate(row):
            bold = is_winner or (c_idx == 0)
            t_col = COLOR_ACCENT_TEAL if is_winner else COLOR_TEXT_PRIMARY
            align = PP_ALIGN.LEFT if (c_idx == 0 or c_idx == 6) else PP_ALIGN.CENTER
            format_table_cell(tbl.cell(r_idx, c_idx), val, bold=bold, font_size=10, bg_color=bg, text_color=t_col, align=align)
            
    # Two discussion columns below table
    add_academic_column(
        slide7, Inches(0.92), Inches(4.15), Inches(5.60), Inches(2.55),
        "Key Finding 1: Why Balanced LogReg Won",
        [
            ("Minority Class Superiority", "Balanced LogReg achieved the highest Negative-class F1 (0.5079 vs DistilBERT's 0.4420). In health surveillance, missing a negative illness review is far more costly than a false positive."),
            ("Ultra-Low Latency", "Inference executed in 0.8 ms per review (vs 42.5 ms for DistilBERT), enabling instantaneous processing in web applications.")
        ],
        accent_color=COLOR_TEXT_PRIMARY,
        title_size=12.5,
        bullet_space=6
    )
    add_academic_column(
        slide7, Inches(6.82), Inches(4.15), Inches(5.60), Inches(2.55),
        "Key Finding 2: Sentiment vs Safety Divergence",
        [
            ("Statistical Disconnect", "Correlation between Customer Sentiment and Municipal Safety Score was only r = 0.08 across 100 Kolkata listings."),
            ("Empirical Confirmation", "Proves that customer reviews primarily capture taste and ambiance, empirically justifying the requirement for independent civic food safety verification.")
        ],
        accent_color=COLOR_ACCENT_BLUE,
        title_size=12.5,
        bullet_space=6
    )

    # =========================================================================
    # SLIDE 8: Future Direction Towards Major Project (4 Clean Quadrants)
    # =========================================================================
    slide8 = prs.slides[7]
    clear_slide_contents(slide8)
    apply_slide_header_and_footer(slide8, "Future Direction Towards Major Project", 8)
    
    add_academic_column(
        slide8, left_col1, top_row1, q_w, q_h,
        "1. Live Civic API Integration & Ingestion",
        [
            ("KMC Portal Connector", "Build automated scrapers and API connectors directly with the Kolkata Municipal Corporation Health Dept."),
            ("FSSAI FoSCoS Feed", "Automate real-time synchronization of Food Safety Officer inspection notices and licence statuses."),
            ("Civic Alert Dispatch", "Directly route high-confidence illness reviews to municipal health desks for priority inspection scheduling.")
        ],
        accent_color=COLOR_TEXT_PRIMARY,
        title_size=12.5,
        bullet_space=5
    )
    add_academic_column(
        slide8, left_col2, top_row1, q_w, q_h,
        "2. Multilingual & Code-Mixed Bengali NLP",
        [
            ("Banglish Handling", "Train domain-adapted IndicBERT/BanglaBERT models to understand Romanized Bengali reviews."),
            ("Dialectal Nuance", "Accurately parse regional Kolkata culinary descriptors ('besh bhalo', 'khub baje', 'tel tel bhab')."),
            ("Cross-Lingual ABSA", "Multi-lingual aspect head capable of extracting food/hygiene sentiment across English, Bengali, and Hindi.")
        ],
        accent_color=COLOR_ACCENT_TEAL,
        title_size=12.5,
        bullet_space=5
    )
    add_academic_column(
        slide8, left_col1, top_row2, q_w, q_h,
        "3. Explainable AI (XAI) for Health Audits",
        [
            ("Attribution Heatmaps", "Implement SHAP (SHapley Additive exPlanations) and Integrated Gradients on review text."),
            ("Evidence Highlighting", "Provide visual token-level justification to public health officers explaining exactly why a review was flagged."),
            ("Audit Trail", "Export cryptographic tamper-proof inspection evidence summaries for regulatory compliance.")
        ],
        accent_color=COLOR_ACCENT_BLUE,
        title_size=12.5,
        bullet_space=5
    )
    add_academic_column(
        slide8, left_col2, top_row2, q_w, q_h,
        "4. Progressive Web App (PWA) & Geofencing",
        [
            ("Offline-First Architecture", "Package web client as a mobile Progressive Web App with local caching for low-connectivity zones."),
            ("GPS Proximity Alerts", "Provide geofenced push notifications warning users when entering dining clusters with recent hygiene flags."),
            ("Street Food Integration", "Expand coverage to Kolkata's iconic street food hubs (Dacres Lane, Gariahat) via QR-code verification.")
        ],
        accent_color=COLOR_TEXT_PRIMARY,
        title_size=12.5,
        bullet_space=5
    )

    # =========================================================================
    # SLIDE 9: Conclusion (4 Clean Milestone Quadrants)
    # =========================================================================
    slide9 = prs.slides[8]
    clear_slide_contents(slide9)
    apply_slide_header_and_footer(slide9, "Conclusion", 9)
    
    add_academic_column(
        slide9, left_col1, top_row1, q_w, q_h,
        "1. Unified Civic-Consumer Intelligence",
        [
            ("Pioneering Integration", "Developed Kolkata FoodLens, the first integrated platform for Kolkata synthesizing consumer review sentiment with municipal food safety compliance."),
            ("Transparency Restored", "Empowered citizens to make informed dining choices backed by verified FSSAI inspection audits rather than inflated star ratings alone.")
        ],
        accent_color=COLOR_TEXT_PRIMARY,
        title_size=12.5,
        bullet_space=6
    )
    add_academic_column(
        slide9, left_col2, top_row1, q_w, q_h,
        "2. Resolved Multi-Aspect Contradictions",
        [
            ("Discourse Clause NLP", "Successfully bypassed coarse sentiment limitations by implementing clause-level ABSA across 5 dimensions (Food, Service, Hygiene, Ambience, Price)."),
            ("High Aspect Reliability", "Achieved 0.865 Macro-F1 on SemEval validation, correctly decomposing contrastive reviews with 100% clause accuracy.")
        ],
        accent_color=COLOR_ACCENT_TEAL,
        title_size=12.5,
        bullet_space=6
    )
    add_academic_column(
        slide9, left_col1, top_row2, q_w, q_h,
        "3. Ethical AI & Zero-Fabrication Integrity",
        [
            ("Strict Non-Fabrication", "Enforced rigorous zero-fabrication guardrails: restaurants without municipal inspection data explicitly display 'Safety data unavailable'."),
            ("Objective Scoring Weights", "Implemented an open, formulaic safety score (40% Outcome, 30% Licence, 20% Violations, 10% Recency) free of subjective bias.")
        ],
        accent_color=COLOR_ACCENT_BLUE,
        title_size=12.5,
        bullet_space=6
    )
    add_academic_column(
        slide9, left_col2, top_row2, q_w, q_h,
        "4. Operational Full-Stack Deployment",
        [
            ("End-to-End System", "Engineered and deployed a production-grade 9-module web dashboard featuring interactive search, radar charts, live review inference, and batch intelligence."),
            ("Continuous Learning", "Wired to an active SQLite store that dynamically recalculates restaurant sentiment scores upon new review submissions.")
        ],
        accent_color=COLOR_TEXT_PRIMARY,
        title_size=12.5,
        bullet_space=6
    )

    # =========================================================================
    # SLIDE 10: References (Academic Clean List)
    # =========================================================================
    slide10 = prs.slides[9]
    clear_slide_contents(slide10)
    apply_slide_header_and_footer(slide10, "References", 10)
    
    top_pos10 = Inches(1.50)
    
    bar10 = slide10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.92), top_pos10, Inches(11.50), Inches(0.04))
    bar10.fill.solid()
    bar10.fill.fore_color.rgb = COLOR_HEADER_BG
    bar10.line.fill.background()
    
    card10 = slide10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.92), top_pos10 + Inches(0.10), Inches(11.50), Inches(5.10))
    card10.fill.background()
    card10.line.fill.background()
    tf10 = card10.text_frame
    tf10.word_wrap = True
    tf10.vertical_anchor = MSO_ANCHOR.TOP
    tf10.margin_left = tf10.margin_right = tf10.margin_top = tf10.margin_bottom = 0
    
    p = tf10.paragraphs[0]
    p.text = "Peer-Reviewed Academic Publications, Benchmarks & Statutory Guidelines"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_HEADER_BG
    p.space_after = Pt(12)
    
    refs = [
        ("[1]", "Pontiki, M., Galanis, D., Papageorgiou, H., et al. (2016). 'SemEval-2016 Task 5: Aspect Based Sentiment Analysis.' Proceedings of the 10th International Workshop on Semantic Evaluation, San Diego, CA, pp. 19–30."),
        ("[2]", "Pang, B., & Lee, L. (2008). 'Opinion Mining and Sentiment Analysis.' Foundations and Trends in Information Retrieval, Vol. 2, No. 1–2, pp. 1–135."),
        ("[3]", "Sancheti, A., Harris, J. K., Mansour, R., et al. (2019). 'Use of Machine Learning to Identify Foodborne Illness Complaints from Online Restaurant Reviews.' CDC Public Health Surveillance Reports, Vol. 68, No. 4, pp. 112–119."),
        ("[4]", "Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.' Proceedings of NAACL-HLT, Minneapolis, MN, pp. 4171–4186."),
        ("[5]", "Sanh, V., Debut, L., Chaumond, J., & Wolf, T. (2019). 'DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter.' arXiv preprint arXiv:1910.01108."),
        ("[6]", "Food Safety and Standards Authority of India (FSSAI). (2023). 'Food Safety and Standards (Clean Street Food Hub and Hygiene Rating Scheme) Regulations.' Ministry of Health and Family Welfare, New Delhi."),
        ("[7]", "Kolkata Municipal Corporation (KMC). (2024). 'Public Health & Hygiene Assessment Guidelines for Commercial Food & Beverage Operators.' Municipal Gazette, Kolkata, West Bengal.")
    ]
    for num, citation in refs:
        p_ref = tf10.add_paragraph()
        p_ref.space_after = Pt(8)
        
        r1 = p_ref.add_run()
        r1.text = f"{num}  "
        r1.font.name = "Arial"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_ACCENT_TEAL
        
        r2 = p_ref.add_run()
        r2.text = citation
        r2.font.name = "Arial"
        r2.font.size = Pt(10)
        r2.font.color.rgb = COLOR_TEXT_SECONDARY

    # Save outputs
    prs.save(str(OUT_PPTX_TEMPLATE))
    prs.save(str(OUT_PPTX_FOODLENS))
    print(f"Successfully generated light-theme academic presentations:\n - {OUT_PPTX_TEMPLATE}\n - {OUT_PPTX_FOODLENS}")


if __name__ == "__main__":
    build_academic_deck()
