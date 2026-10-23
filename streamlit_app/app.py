from __future__ import annotations

import html
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

try:
    import joblib
except Exception:  # show a friendly in-app diagnostic if the environment is incomplete
    joblib = None  # type: ignore[assignment]

try:
    import pandas as pd
except Exception:
    pd = None  # type: ignore[assignment]

# Supports both layouts:
# 1) repo root: app.py + results/best_model.joblib
# 2) local student project: streamlit_app/app.py + results/best_model.joblib
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = next(
    (p for p in [HERE, *HERE.parents] if (p / "results").is_dir()),
    HERE,
)
RESULTS_DIR = PROJECT_ROOT / "results"
MODEL_PATH = RESULTS_DIR / "best_model.joblib"
MODEL_NAME_PATH = RESULTS_DIR / "best_model_name.txt"
METRICS_PATH = RESULTS_DIR / "model_comparison.csv"

st.set_page_config(
    page_title="Food Review Intelligence | Sentiment Lab",
    page_icon="✳️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Polished, restrained interface; the Streamlit config also sets the base theme.
st.markdown(
    """
    <style>
    :root {
      --ink: #18283B; --muted: #617083; --paper: #F4F6F5; --line: #E1E7E5;
      --teal: #137C72; --teal-soft: #E7F4F1; --white: #FFFFFF;
    }
    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(244,246,245,.92); }
    .block-container { max-width: 1260px; padding-top: 1.2rem; padding-bottom: 3rem; }
    [data-testid="stToolbar"] { right: 1rem; }
    h1, h2, h3 { letter-spacing: -0.035em; color: var(--ink); }
    p, li, label { color: var(--ink); }
    .brand-row { display:flex; align-items:center; gap:.7rem; margin-bottom:1.05rem; }
    .brand-mark { width:38px; height:38px; border-radius:13px; display:flex; align-items:center;
      justify-content:center; background:#173A4A; color:#DDF6EF; font-size:1.2rem; font-weight:800; }
    .brand-name { font-size:.92rem; font-weight:800; letter-spacing:.06em; text-transform:uppercase; color:#20384A; }
    .brand-sub { font-size:.73rem; color:#6C7B86; margin-top:.08rem; }
    .hero { background:linear-gradient(118deg,#162D3B 0%,#234758 68%,#1B645D 100%);
      border-radius:24px; padding:2rem 2.1rem; color:white; margin:.2rem 0 1.15rem 0;
      box-shadow:0 14px 35px rgba(25,54,67,.10); position:relative; overflow:hidden; }
    .hero:after { content:""; width:250px; height:250px; border:1px solid rgba(255,255,255,.12);
      border-radius:50%; position:absolute; right:-60px; top:-115px; box-shadow:0 0 0 26px rgba(255,255,255,.025),0 0 0 54px rgba(255,255,255,.02); }
    .hero-kicker { color:#B8E7DC; font-size:.73rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; margin-bottom:.75rem; }
    .hero h1 { color:#FFFFFF; font-size:clamp(2rem,3vw,3rem); line-height:1.05; margin:0 0 .7rem 0; font-weight:750; }
    .hero p { color:#D7E4E8; max-width:750px; font-size:1.02rem; margin:0; line-height:1.65; }
    .hero-note { margin-top:1.25rem; display:flex; flex-wrap:wrap; gap:.5rem; }
    .hero-chip { border:1px solid rgba(226,247,241,.25); background:rgba(255,255,255,.07); color:#E2F4EF;
      border-radius:999px; padding:.35rem .7rem; font-size:.74rem; }
    .section-eyebrow { text-transform:uppercase; letter-spacing:.13em; color:#70818A; font-size:.72rem; font-weight:800; margin-bottom:.3rem; }
    .section-title { font-size:1.45rem; font-weight:760; letter-spacing:-.035em; margin:0 0 .35rem 0; color:#1B2F40; }
    .section-copy { color:#647586; margin-bottom:1rem; line-height:1.6; }
    .surface { background:#FFFFFF; border:1px solid var(--line); border-radius:18px; padding:1.1rem 1.2rem; }
    .metric-card { background:#FFFFFF; border:1px solid var(--line); border-radius:16px; padding:1rem 1.05rem; min-height:105px; }
    .metric-label { font-size:.74rem; color:#71808B; font-weight:750; text-transform:uppercase; letter-spacing:.08em; }
    .metric-value { font-size:1.65rem; font-weight:800; letter-spacing:-.045em; color:#1A3341; margin:.28rem 0 .12rem 0; }
    .metric-note { color:#687D87; font-size:.79rem; }
    .result-card { border:1px solid #DDE6E4; border-radius:20px; background:#fff; padding:1.2rem 1.35rem; }
    .result-top { display:flex; align-items:center; gap:.9rem; }
    .result-icon { width:53px; height:53px; border-radius:16px; display:flex; align-items:center; justify-content:center; font-size:1.6rem; }
    .result-label { color:#7A8791; font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; font-weight:800; }
    .result-value { font-size:2rem; font-weight:820; letter-spacing:-.04em; margin-top:.08rem; }
    .result-positive { border-color:#B5DDD0; background:linear-gradient(135deg,#FFFFFF,#F2FAF6); }
    .result-positive .result-icon { background:#DDF3E9; }
    .result-positive .result-value { color:#13744F; }
    .result-negative { border-color:#EBCBC5; background:linear-gradient(135deg,#FFFFFF,#FFF6F4); }
    .result-negative .result-icon { background:#FBE5E0; }
    .result-negative .result-value { color:#B3473D; }
    .result-neutral { border-color:#E9DBB6; background:linear-gradient(135deg,#FFFFFF,#FFFBF0); }
    .result-neutral .result-icon { background:#F8EDC9; }
    .result-neutral .result-value { color:#98701D; }
    .pill { display:inline-block; border-radius:999px; padding:.27rem .6rem; font-size:.72rem; font-weight:800; background:#E8F4F1; color:#126B63; }
    .score-row { display:grid; grid-template-columns:95px 1fr 48px; align-items:center; gap:.55rem; margin:.7rem 0; font-size:.83rem; }
    .score-track { height:8px; border-radius:20px; background:#EAF0EE; overflow:hidden; }
    .score-fill { height:100%; border-radius:20px; }
    .callout { border-radius:14px; padding:.85rem 1rem; background:#EAF4F2; border:1px solid #D2E8E3; color:#315B5A; line-height:1.5; }
    .warning-box { border-radius:14px; padding:.95rem 1rem; background:#FFF7E8; border:1px solid #F0DDB7; color:#725C32; line-height:1.55; }
    .step { border:1px solid #E0E7E5; background:#fff; border-radius:15px; padding:1rem; height:100%; }
    .step-no { color:#137C72; font-size:.72rem; font-weight:850; letter-spacing:.12em; }
    .step-title { color:#1A3442; font-weight:800; margin:.35rem 0; }
    .step-copy { color:#667987; font-size:.87rem; line-height:1.55; }
    div[data-testid="stMetric"] { background:#fff; border:1px solid #E0E7E5; border-radius:15px; padding:1rem; }
    div[data-testid="stMetricLabel"] { color:#74818A; }
    div.stButton > button { border-radius:11px; font-weight:720; min-height:2.7rem; border-color:#DCE5E2; }
    div.stButton > button[kind="primary"] { background:#147C72; color:#fff; border-color:#147C72; }
    div.stButton > button[kind="primary"]:hover { background:#0D655D; border-color:#0D655D; }
    .stTextArea textarea { border-radius:13px; border-color:#DCE5E2; background:#FFFFFF; line-height:1.55; }
    div[data-baseweb="select"] > div { border-radius:11px; }
    button[data-baseweb="tab"] { font-weight:700; }
    div[data-testid="stTabs"] [data-baseweb="tab-list"] { gap:.4rem; border-bottom:1px solid #DFE6E4; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color:#137C72; }
    .footer { border-top:1px solid #DFE6E4; margin-top:2.4rem; padding-top:1rem; color:#77858E; font-size:.76rem; display:flex; gap:1rem; justify-content:space-between; flex-wrap:wrap; }
    footer { visibility:hidden; }
    @media (max-width: 700px) { .hero { padding:1.4rem; border-radius:18px; } .hero h1 { font-size:2rem; } .block-container { padding-left:1rem; padding-right:1rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)

# Verified project results from the student's training run.
MODEL_METRICS = pd.DataFrame(
    [
        {"Model": "Logistic Regression", "Accuracy": 0.8244, "Macro Precision": 0.7104, "Macro Recall": 0.7375, "Macro F1": 0.7217, "Weighted F1": 0.8318},
        {"Model": "Linear SVM", "Accuracy": 0.8397, "Macro Precision": 0.7137, "Macro Recall": 0.6919, "Macro F1": 0.6991, "Weighted F1": 0.8301},
        {"Model": "Multinomial Naive Bayes", "Accuracy": 0.7540, "Macro Precision": 0.5577, "Macro Recall": 0.4538, "Macro F1": 0.4575, "Weighted F1": 0.6820},
    ]
) if pd is not None else None

SENTIMENT_COUNTS = {"Positive": 9857, "Negative": 2699, "Neutral": 1795}
SENTIMENT_COLORS = {"Positive": "#208765", "Negative": "#C65E52", "Neutral": "#C79A39"}
SENTIMENT_ICONS = {"Positive": "✦", "Negative": "↘", "Neutral": "—"}
SAMPLE_REVIEWS = {
    "Positive example": "The food was delicious and the service was excellent.",
    "Negative example": "The food was cold and the delivery was extremely late.",
    "Neutral example": "The food was average and nothing was particularly special.",
}


def get_model_name() -> str:
    try:
        if MODEL_NAME_PATH.exists():
            name = MODEL_NAME_PATH.read_text(encoding="utf-8").strip()
            if name:
                return name.replace("LogisticRegression", "Logistic Regression")
    except OSError:
        pass
    return "Logistic Regression"


def clean_label(value: Any) -> str:
    label = str(value).strip()
    aliases = {
        "positive": "Positive", "pos": "Positive",
        "negative": "Negative", "neg": "Negative",
        "neutral": "Neutral", "neu": "Neutral",
    }
    return aliases.get(label.lower(), label[:1].upper() + label[1:] if label else "Unknown")


@st.cache_resource(show_spinner="Loading the trained sentiment model…")
def load_model() -> Any:
    if joblib is None:
        raise ModuleNotFoundError("joblib is missing from the Python environment running this app.")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {MODEL_PATH}. Copy your trained results/best_model.joblib into this app's results folder."
        )
    return joblib.load(MODEL_PATH)


def load_vectorizer_if_available() -> Any | None:
    if joblib is None:
        return None
    candidates = [
        RESULTS_DIR / "tfidf_vectorizer.joblib",
        RESULTS_DIR / "vectorizer.joblib",
        RESULTS_DIR / "best_vectorizer.joblib",
        RESULTS_DIR / "tfidf.joblib",
    ]
    for path in candidates:
        if path.exists():
            return joblib.load(path)
    return None


def model_features_and_predict(model: Any, review: str) -> tuple[Any, Any, Any]:
    """Return prediction, optional scores and score classes.

    First expects a full sklearn pipeline that accepts raw text. If the saved artifact
    is a bare classifier, optionally uses a separately saved vectorizer if provided.
    """
    vectorizer = None
    classifier = model
    if isinstance(model, dict):
        classifier = model.get("pipeline") or model.get("model") or model.get("classifier") or model
        vectorizer = model.get("vectorizer") or model.get("tfidf_vectorizer")

    try:
        X = [review]
        prediction = classifier.predict(X)[0]
        scoring_input = X
    except Exception as direct_exc:
        if vectorizer is None:
            vectorizer = load_vectorizer_if_available()
        if vectorizer is None:
            raise RuntimeError(
                "The saved model does not accept raw review text. It may be a classifier without its fitted text vectorizer. "
                "If your training script saved a separate vectorizer, place it in results/tfidf_vectorizer.joblib or results/vectorizer.joblib. "
                f"Original detail: {type(direct_exc).__name__}: {direct_exc}"
            ) from direct_exc
        X = vectorizer.transform([review])
        prediction = classifier.predict(X)[0]
        scoring_input = X

    scores = None
    classes = None
    if hasattr(classifier, "predict_proba"):
        try:
            scores = classifier.predict_proba(scoring_input)[0]
            classes = getattr(classifier, "classes_", None)
            if classes is None and hasattr(classifier, "named_steps"):
                classes = getattr(list(classifier.named_steps.values())[-1], "classes_", None)
        except Exception:
            scores, classes = None, None
    return prediction, scores, classes


def sentiment_from_review(review: str) -> tuple[str, list[dict[str, Any]] | None]:
    model = load_model()
    raw_prediction, scores, classes = model_features_and_predict(model, review)
    label = clean_label(raw_prediction)
    breakdown = None
    if scores is not None and classes is not None and len(scores) == len(classes):
        breakdown = []
        for item, score in zip(classes, scores):
            breakdown.append({"sentiment": clean_label(item), "score": max(0.0, float(score))})
        total = sum(item["score"] for item in breakdown)
        if total > 0:
            for item in breakdown:
                item["score"] = item["score"] / total
        breakdown.sort(key=lambda item: item["score"], reverse=True)
    return label, breakdown


def metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(value)}</div><div class="metric-note">{html.escape(note)}</div></div>',
        unsafe_allow_html=True,
    )


def show_prediction_result(review: str, prediction: str, breakdown: list[dict[str, Any]] | None) -> None:
    key = prediction.lower() if prediction.lower() in {"positive", "negative", "neutral"} else "neutral"
    icon = {"positive": "✦", "negative": "↘", "neutral": "—"}[key]
    st.markdown(
        f'<div class="result-card result-{key}"><div class="result-top">'
        f'<div class="result-icon">{icon}</div><div><div class="result-label">Model prediction</div>'
        f'<div class="result-value">{html.escape(prediction)}</div></div></div></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown("**Review analysed**")
    st.markdown(f'<div class="surface">{html.escape(review)}</div>', unsafe_allow_html=True)
    if breakdown:
        st.markdown("#### Model score by class")
        st.caption("Scores are the model's class outputs, not a guarantee that the prediction is correct.")
        for item in breakdown:
            cls = item["sentiment"]
            score = float(item["score"])
            color = SENTIMENT_COLORS.get(cls, "#66828A")
            st.markdown(
                f'<div class="score-row"><div>{html.escape(cls)}</div><div class="score-track">'
                f'<div class="score-fill" style="width:{min(100, max(0, score*100)):.2f}%;background:{color};"></div>'
                f'</div><div style="text-align:right;font-weight:750;">{score:.1%}</div></div>',
                unsafe_allow_html=True,
            )


def add_history(review: str, prediction: str) -> None:
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    st.session_state.analysis_history.insert(
        0,
        {"Time": datetime.now().strftime("%H:%M:%S"), "Sentiment": prediction, "Review": review},
    )
    st.session_state.analysis_history = st.session_state.analysis_history[:20]


# Brand and hero
st.markdown(
    '<div class="brand-row"><div class="brand-mark">✳</div><div><div class="brand-name">Sentiment Lab</div>'
    '<div class="brand-sub">Machine learning · Customer experience analytics</div></div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero"><div class="hero-kicker">NLP / FOOD REVIEW INTELLIGENCE</div>'
    '<h1>Understand the feeling<br>behind every review.</h1>'
    '<p>Explore a machine-learning model that classifies online food reviews as positive, negative, or neutral. '
    'Test a review, inspect model performance, and explore the dataset behind the project.</p>'
    '<div class="hero-note"><span class="hero-chip">3 sentiment classes</span>'
    '<span class="hero-chip">14,351 labelled reviews</span><span class="hero-chip">3 models compared</span></div></div>',
    unsafe_allow_html=True,
)

# Compact glance cards
c1, c2, c3, c4 = st.columns(4, gap="medium")
with c1:
    metric_card("Reviews in dataset", "14,351", "Yelp restaurant review dataset")
with c2:
    metric_card("Sentiment classes", "03", "Positive · Neutral · Negative")
with c3:
    metric_card("Top accuracy", "83.97%", "Linear SVM in the test results")
with c4:
    metric_card("Selected model", "Logistic Reg.", "Highest macro F1: 0.7217")

st.write("")
tabs = st.tabs(["✳  Review analyzer", "▥  Model performance", "◫  Dataset insights", "⌘  Methodology"])

with tabs[0]:
    st.markdown('<div class="section-eyebrow">INTERACTIVE WORKSPACE</div><div class="section-title">Analyze a customer review</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Write or paste a review, choose a sample, and run your trained classifier.</div>', unsafe_allow_html=True)

    left, right = st.columns([1.12, .88], gap="large")
    with left:
        sample_cols = st.columns(3)
        sample_order = list(SAMPLE_REVIEWS.keys())
        for idx, col in enumerate(sample_cols):
            with col:
                short_label = ["Positive sample", "Negative sample", "Neutral sample"][idx]
                if st.button(short_label, key=f"sample_{idx}", use_container_width=True):
                    st.session_state.review_input = SAMPLE_REVIEWS[sample_order[idx]]
                    st.session_state.pop("latest_result", None)
                    st.rerun()
        review_text = st.text_area(
            "Review text",
            key="review_input",
            height=180,
            placeholder="Example: The ramen arrived hot, tasted fresh, and the staff were welcoming.",
            help="Enter one English-language review. The model returns one of the sentiment labels.",
        )
        word_count = len(review_text.split()) if review_text.strip() else 0
        st.caption(f"{word_count} words · {len(review_text)} characters")
        run_col, clear_col = st.columns([1.35, .65])
        with run_col:
            analyze_clicked = st.button("Analyze sentiment  →", key="analyze_single", type="primary", use_container_width=True)
        with clear_col:
            clear_clicked = st.button("Clear", key="clear_review", use_container_width=True)
        if clear_clicked:
            st.session_state.review_input = ""
            st.session_state.pop("latest_result", None)
            st.rerun()
        if analyze_clicked:
            st.session_state.pop("latest_error", None)
            if not review_text.strip():
                st.warning("Enter a review before running the analysis.")
            elif len(review_text.strip()) < 3:
                st.warning("Please enter a little more review text.")
            else:
                with st.spinner("Analysing review with the trained model…"):
                    try:
                        prediction, scores = sentiment_from_review(review_text.strip())
                        st.session_state.latest_result = {"review": review_text.strip(), "prediction": prediction, "scores": scores}
                        add_history(review_text.strip(), prediction)
                    except FileNotFoundError as exc:
                        st.session_state.latest_error = str(exc)
                    except ModuleNotFoundError as exc:
                        st.session_state.latest_error = f"Required package is missing: {exc}. Install packages from requirements.txt and restart the app."
                    except Exception as exc:
                        st.session_state.latest_error = f"The app couldn't generate a prediction: {type(exc).__name__}: {exc}"
        with st.expander("Try several reviews at once", expanded=False):
            st.write("Paste one review per line. Blank lines will be ignored.")
            batch_input = st.text_area("Batch reviews", key="batch_input", height=125, placeholder="The pizza was amazing.\nThe order arrived cold.\nThe meal was okay.")
            if st.button("Analyze batch", key="analyze_batch", use_container_width=True):
                lines = [line.strip() for line in batch_input.splitlines() if line.strip()]
                if not lines:
                    st.warning("Paste at least one review, with one review per line.")
                else:
                    results = []
                    try:
                        model = load_model()
                        for text_line in lines[:100]:
                            raw, _, _ = model_features_and_predict(model, text_line)
                            results.append({"Review": text_line, "Predicted sentiment": clean_label(raw)})
                        st.session_state.batch_results = results
                        if len(lines) > 100:
                            st.info("Only the first 100 reviews were processed in this batch.")
                    except Exception as exc:
                        st.error(f"Batch analysis failed: {type(exc).__name__}: {exc}")
            if st.session_state.get("batch_results"):
                batch_frame = pd.DataFrame(st.session_state.batch_results) if pd is not None else None
                if batch_frame is not None:
                    st.dataframe(batch_frame, use_container_width=True, hide_index=True)
                    st.download_button("Download batch results (CSV)", batch_frame.to_csv(index=False).encode("utf-8"), file_name="food_review_sentiment_results.csv", mime="text/csv")

    with right:
        st.markdown('<div class="surface"><div class="section-eyebrow">WHAT HAPPENS NEXT</div><div class="section-title" style="font-size:1.2rem">From text to sentiment</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="step"><div class="step-no">01 / INPUT</div><div class="step-title">Customer review</div><div class="step-copy">The app accepts review text written in natural language.</div></div>'
            '<div style="height:8px"></div><div class="step"><div class="step-no">02 / PROCESS</div><div class="step-title">Text representation</div><div class="step-copy">The saved model pipeline transforms the text into features it learned during training.</div></div>'
            '<div style="height:8px"></div><div class="step"><div class="step-no">03 / PREDICT</div><div class="step-title">Three-way classification</div><div class="step-copy">The trained classifier returns Positive, Negative, or Neutral.</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")
        if MODEL_PATH.exists():
            st.markdown('<div class="callout"><b>Model artifact detected.</b><br>The app has found the saved model file in the results folder.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box"><b>Model file not found yet.</b><br>Place <code>results/best_model.joblib</code> beside the app so live predictions can run. Performance and dataset information remain available.</div>', unsafe_allow_html=True)

    if st.session_state.get("latest_error"):
        st.error(st.session_state.latest_error)
        st.caption(f"App file: {Path(__file__).resolve()} · Python: {sys.executable}")
        with st.expander("Technical details"):
            st.code(st.session_state.latest_error)
        if st.button("Dismiss error", key="dismiss_error"):
            st.session_state.pop("latest_error", None)
            st.rerun()

    if st.session_state.get("latest_result"):
        st.write("")
        st.markdown('<div class="section-eyebrow">ANALYSIS OUTPUT</div><div class="section-title">Prediction result</div>', unsafe_allow_html=True)
        res = st.session_state.latest_result
        res_cols = st.columns([1, 1.05], gap="large")
        with res_cols[0]:
            show_prediction_result(res["review"], res["prediction"], res["scores"])
        with res_cols[1]:
            st.markdown('<div class="surface"><div class="section-eyebrow">INTERPRETATION</div><div class="section-title" style="font-size:1.2rem">How to read this result</div>', unsafe_allow_html=True)
            st.write(f"The model assigned the **{res['prediction'].lower()}** label to the review entered above.")
            if res.get("scores"):
                st.write("The score bars show the model's output across available classes. These are not a promise that the label is correct.")
            else:
                st.write("This saved estimator does not expose class probabilities, so the app shows the predicted class without inventing a confidence score.")
            st.caption("Sentiment models can miss sarcasm, mixed opinions, slang, spelling errors, and context outside the review text.")
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("analysis_history"):
        with st.expander("Recent predictions from this browser session"):
            history_df = pd.DataFrame(st.session_state.analysis_history) if pd is not None else None
            if history_df is not None:
                st.dataframe(history_df, use_container_width=True, hide_index=True)
                st.download_button("Download prediction history", history_df.to_csv(index=False).encode("utf-8"), file_name="prediction_history.csv", mime="text/csv")

with tabs[1]:
    st.markdown('<div class="section-eyebrow">EVALUATION SCORECARD</div><div class="section-title">Three models. One test set.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Compare accuracy with macro F1 to see why the model selected for the website is not automatically the one with the highest accuracy.</div>', unsafe_allow_html=True)
    if MODEL_METRICS is not None:
        top1, top2, top3 = st.columns(3)
        with top1:
            metric_card("Highest accuracy", "83.97%", "Linear SVM")
        with top2:
            metric_card("Highest macro F1", "0.7217", "Logistic Regression")
        with top3:
            metric_card("Lowest macro F1", "0.4575", "Multinomial Naive Bayes")
        st.write("")
        chart_col, insight_col = st.columns([1.2, .8], gap="large")
        with chart_col:
            st.markdown("#### Accuracy vs macro F1")
            chart_df = MODEL_METRICS.set_index("Model")[["Accuracy", "Macro F1"]]
            st.bar_chart(chart_df, y_label="Score (0–1)", height=310)
        with insight_col:
            st.markdown("#### What the results suggest")
            st.markdown('<div class="surface"><span class="pill">Selection rationale</span><h3 style="margin-top:.75rem">Balanced performance matters.</h3><p style="color:#657885;line-height:1.65">Linear SVM produces the highest overall accuracy, while Logistic Regression achieves the best macro F1 in this run. Macro F1 gives equal weight to each class, helping expose weaker performance on less common labels.</p><hr style="border-color:#E3E9E7"><p style="color:#657885;line-height:1.65">The neutral class is the main improvement opportunity; a strong overall accuracy can hide weaker results on minority classes.</p></div>', unsafe_allow_html=True)
        st.write("")
        st.markdown("#### Full evaluation metrics")
        display_df = MODEL_METRICS.copy()
        for col in ["Accuracy", "Macro Precision", "Macro Recall", "Macro F1", "Weighted F1"]:
            display_df[col] = display_df[col].map(lambda x: f"{x:.2%}" if col == "Accuracy" else f"{x:.4f}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.caption("Metrics are from the project's recorded evaluation run. Recalculate them if the dataset split or model training changes.")
    else:
        st.warning("Pandas is required to display the evaluation table. Install the packages from requirements.txt.")

with tabs[2]:
    st.markdown('<div class="section-eyebrow">DATASET OVERVIEW</div><div class="section-title">What the model learned from</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">A quick profile of the review dataset used for the project. No raw customer records are displayed on this page.</div>', unsafe_allow_html=True)
    n1, n2, n3, n4 = st.columns(4)
    with n1: metric_card("Records", "14,351", "Restaurant reviews")
    with n2: metric_card("Fields", "11", "Dataset columns")
    with n3: metric_card("Missing values", "0 reported", "In the prepared dataset")
    with n4: metric_card("Duplicate texts", "1", "Reported in cleaning checks")
    st.write("")
    dist_col, profile_col = st.columns([1, 1], gap="large")
    with dist_col:
        st.markdown("#### Sentiment distribution")
        if pd is not None:
            dist = pd.DataFrame({"Sentiment": list(SENTIMENT_COUNTS.keys()), "Reviews": list(SENTIMENT_COUNTS.values())})
            dist["Share"] = dist["Reviews"] / sum(SENTIMENT_COUNTS.values())
            st.bar_chart(dist.set_index("Sentiment")["Reviews"], y_label="Number of reviews", height=270)
            for name, count in SENTIMENT_COUNTS.items():
                pct = count / sum(SENTIMENT_COUNTS.values())
                st.markdown(f'<div class="score-row"><div>{name}</div><div class="score-track"><div class="score-fill" style="width:{pct*100:.2f}%;background:{SENTIMENT_COLORS[name]};"></div></div><div style="text-align:right;font-weight:750">{pct:.1%}</div></div>', unsafe_allow_html=True)
    with profile_col:
        st.markdown("#### Project data profile")
        st.markdown('<div class="surface"><p><b>Review text</b><br><span style="color:#657885">The main input field submitted to the classifier.</span></p><hr style="border-color:#E5EBE9"><p><b>Sentiment label</b><br><span style="color:#657885">The target category used for supervised learning.</span></p><hr style="border-color:#E5EBE9"><p><b>Class balance</b><br><span style="color:#657885">Positive reviews are the majority (about 68.7%), while neutral reviews are less common.</span></p><hr style="border-color:#E5EBE9"><p><b>Why it matters</b><br><span style="color:#657885">Class imbalance is one reason to review per-class results and macro F1—not accuracy alone.</span></p></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="callout"><b>Interpretation note:</b> the chart describes the labelled project dataset. It does not describe the sentiment of all food reviews on the internet.</div>', unsafe_allow_html=True)

with tabs[3]:
    st.markdown('<div class="section-eyebrow">PROJECT DOCUMENTATION</div><div class="section-title">The workflow behind the prediction</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">This interface demonstrates the trained classifier; model training is performed separately and is not repeated each time the page is used.</div>', unsafe_allow_html=True)
    steps = st.columns(4, gap="medium")
    workflow = [
        ("01", "Collect", "Use the labelled online food-review dataset for supervised learning."),
        ("02", "Prepare", "Inspect review text and labels, and apply the text preparation used in training."),
        ("03", "Train & compare", "Evaluate Logistic Regression, Linear SVM, and Multinomial Naive Bayes."),
        ("04", "Predict", "Load the saved model and classify newly entered reviews in the web app."),
    ]
    for col, (num, title, copy) in zip(steps, workflow):
        with col:
            st.markdown(f'<div class="step"><div class="step-no">STAGE {num}</div><div class="step-title">{title}</div><div class="step-copy">{copy}</div></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("#### Technical stack")
    st.markdown('<div class="surface"><span class="pill">Python</span> &nbsp; <span class="pill">scikit-learn</span> &nbsp; <span class="pill">Joblib</span> &nbsp; <span class="pill">pandas</span> &nbsp; <span class="pill">Streamlit</span><br><br><p style="color:#667987;line-height:1.65">The exact text vectorization and preprocessing must match the project training code. For deployment, the trained model artifact and compatible Python packages must be included in the GitHub repository.</p></div>', unsafe_allow_html=True)
    st.write("")
    with st.expander("Model use and limitations"):
        st.markdown(
            "- The model predicts sentiment from the review text provided; it does not verify whether a review is factually accurate.\n"
            "- Sarcasm, mixed sentiment, domain-specific slang, and short or ambiguous reviews can lead to errors.\n"
            "- Displayed evaluation metrics are from the project's recorded test run. New training runs may produce different values.\n"
            "- Do not treat prediction scores as calibrated probabilities unless the saved estimator was designed and evaluated for that purpose."
        )

st.markdown(
    '<div class="footer"><span>Sentiment Lab · Minor Project — Sentiment Analysis of Online Food Reviews</span>'
    '<span>Academic prototype · Predictions may be imperfect</span></div>',
    unsafe_allow_html=True,
)
