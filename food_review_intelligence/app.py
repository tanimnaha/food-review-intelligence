from __future__ import annotations

import html
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

try:
    import joblib
except Exception:
    joblib = None

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = next((p for p in [HERE, *HERE.parents] if (p / "results").is_dir()), HERE)
RESULTS_DIR = PROJECT_ROOT / "results"
MODEL_PATH = RESULTS_DIR / "best_model.joblib"
MODEL_NAME_PATH = RESULTS_DIR / "best_model_name.txt"
METRICS_PATH = RESULTS_DIR / "model_comparison.csv"

st.set_page_config(page_title="Food Review Intelligence", page_icon="✳", layout="wide", initial_sidebar_state="expanded")

# Premium restrained visual system: editorial navy + teal, ample whitespace.
st.markdown(r"""
<style>
:root{--ink:#192d3a;--muted:#647784;--paper:#f4f7f6;--line:#dfe8e5;--teal:#147d73;--teal2:#dff2ed;--navy:#173341;--white:#fff}
.stApp{background:var(--paper);color:var(--ink)}
[data-testid="stHeader"]{background:rgba(244,247,246,.94)}
.block-container{max-width:1380px;padding-top:1.1rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.035em;color:var(--ink)} p,li,label{color:var(--ink)}
.brand{display:flex;align-items:center;gap:.65rem;margin:.2rem 0 1rem}
.brandmark{width:38px;height:38px;border-radius:13px;background:var(--navy);color:#c8f0e5;display:flex;align-items:center;justify-content:center;font-size:1.25rem;font-weight:900}
.brandname{font-size:.9rem;font-weight:850;letter-spacing:.08em;text-transform:uppercase;color:var(--navy)}
.brandsub{font-size:.76rem;color:var(--muted);margin-top:.12rem}
.hero{position:relative;overflow:hidden;border-radius:26px;padding:2.2rem;background:linear-gradient(118deg,#142f3d,#214857 63%,#176c63);color:#fff;box-shadow:0 16px 40px #17334118;margin:.25rem 0 1.25rem}
.hero:after{content:"";position:absolute;width:280px;height:280px;right:-85px;top:-130px;border:1px solid #ffffff22;border-radius:50%;box-shadow:0 0 0 28px #ffffff08,0 0 0 58px #ffffff06}
.kicker{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;font-weight:850;color:#bce9df;margin-bottom:.8rem}
.hero h1{color:#fff;font-size:clamp(2.1rem,3.2vw,3.2rem);line-height:1.04;margin:0 0 .8rem;font-weight:850;max-width:780px}
.hero p{color:#d8e7e9;max-width:850px;line-height:1.65;font-size:1.02rem}
.chips{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:1.2rem}.chip{padding:.38rem .75rem;border-radius:99px;border:1px solid #ffffff35;background:#ffffff0d;color:#e3f5f0;font-size:.76rem}
.eyebrow{color:#748691;font-size:.71rem;font-weight:850;letter-spacing:.14em;text-transform:uppercase;margin-bottom:.35rem}
.section-title{font-size:1.45rem;font-weight:850;letter-spacing:-.04em;margin:0 0 .3rem;color:var(--ink)}
.subcopy{color:var(--muted);line-height:1.65;margin-bottom:1.1rem}
.card{background:#fff;border:1px solid var(--line);border-radius:18px;padding:1.1rem 1.2rem;height:100%}
.metric{background:#fff;border:1px solid var(--line);border-radius:17px;padding:1rem 1.05rem;min-height:114px}
.metriclabel{font-size:.7rem;font-weight:850;color:#71828d;letter-spacing:.11em;text-transform:uppercase}
.metricvalue{font-size:1.65rem;font-weight:900;letter-spacing:-.045em;color:#1c3645;margin:.28rem 0 .12rem;overflow-wrap:anywhere}
.metricnote{font-size:.8rem;color:#71838d;line-height:1.4}
.badge{display:inline-block;border-radius:99px;padding:.3rem .65rem;background:#e4f3ef;color:#12685f;font-size:.72rem;font-weight:850}
.insight{padding:.9rem 1rem;border:1px solid #cfe7df;border-radius:15px;background:#ebf6f2;color:#305b59;line-height:1.6}
.caution{padding:.9rem 1rem;border:1px solid #ecdcb7;border-radius:15px;background:#fff8e9;color:#745e33;line-height:1.6}
.sentimentbox{border-radius:18px;padding:1.25rem;border:1px solid var(--line);background:#fff}
.sentimentbox.positive{background:linear-gradient(130deg,#fff,#effaf5);border-color:#b6dfd1}.sentimentbox.negative{background:linear-gradient(130deg,#fff,#fff4f2);border-color:#edcbc5}.sentimentbox.neutral{background:linear-gradient(130deg,#fff,#fffaf0);border-color:#e9dbb6}
.stButton>button,.stDownloadButton>button{border-radius:12px;min-height:2.65rem;font-weight:750;border-color:#d7e3df}
.stButton>button[kind="primary"]{background:#147d73;color:white;border-color:#147d73}.stButton>button[kind="primary"]:hover{background:#10675f;color:white;border-color:#10675f}
.stTextArea textarea,.stTextInput input{border-radius:12px;background:#fff}
div[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:.3rem;border-bottom:1px solid #dce6e3}
div[data-testid="stTabs"] button{font-weight:750}
div[data-testid="stTabs"] button[aria-selected="true"]{color:#147d73}
div[data-testid="stMetric"]{background:#fff;border:1px solid #dfe8e5;border-radius:15px;padding:1rem}
[data-testid="stDataFrame"]{border:1px solid #e1e8e6;border-radius:12px;overflow:hidden}
hr{border-color:#dfe8e5}
.footer{border-top:1px solid #dfe8e5;margin-top:2.5rem;padding-top:1rem;display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;color:#7a8a92;font-size:.76rem}
@media(max-width:700px){.hero{padding:1.35rem;border-radius:19px}.hero h1{font-size:2.1rem}.block-container{padding-left:1rem;padding-right:1rem}}
</style>
""", unsafe_allow_html=True)

METRICS_FALLBACK = pd.DataFrame([
    {"Model": "Logistic Regression", "Accuracy": .8244, "Macro Precision": .7104, "Macro Recall": .7375, "Macro F1": .7217, "Weighted F1": .8318},
    {"Model": "Linear SVM", "Accuracy": .8397, "Macro Precision": .7137, "Macro Recall": .6919, "Macro F1": .6991, "Weighted F1": .8301},
    {"Model": "Multinomial Naive Bayes", "Accuracy": .7540, "Macro Precision": .5577, "Macro Recall": .4538, "Macro F1": .4575, "Weighted F1": .6820},
])
SENTIMENT_COUNTS = {"Positive": 9857, "Negative": 2699, "Neutral": 1795}
SENTIMENT_COLORS = {"Positive": "#228866", "Negative": "#c95f53", "Neutral": "#c49a38"}
SAMPLE_REVIEWS = {
    "Positive": "The food was delicious and the service was excellent.",
    "Negative": "The food was cold and the delivery was extremely late.",
    "Neutral": "The food was average and nothing was particularly special.",
}
ASPECT_TERMS = {
    "Food quality": ["food", "taste", "tasty", "flavor", "flavour", "delicious", "bland", "fresh", "cold", "hot", "overcooked", "undercooked", "portion", "menu", "meal", "dish", "pizza", "burger", "sushi", "dessert"],
    "Service": ["service", "staff", "waiter", "waitress", "server", "friendly", "rude", "polite", "attentive", "manager", "waited", "hospitality"],
    "Delivery & timing": ["delivery", "delivered", "driver", "arrived", "late", "waiting", "wait", "order", "takeout", "takeaway", "pickup", "pick-up"],
    "Price & value": ["price", "priced", "expensive", "cheap", "cost", "value", "bill", "money", "overpriced", "affordable", "portion"],
    "Cleanliness & ambience": ["clean", "dirty", "hygiene", "table", "bathroom", "toilet", "ambience", "atmosphere", "music", "noise", "decor", "comfortable"],
}
STOPWORDS = set("a an the and or but if then than to of in on for with at by from is are was were be been being it this that these those i we you they he she them my our your their very really just so too as have has had do did does not no nor can could would should about into over after before up down out there here food restaurant meal review place good bad".split())


def model_name() -> str:
    try:
        if MODEL_NAME_PATH.exists():
            name = MODEL_NAME_PATH.read_text(encoding="utf-8").strip()
            if name:
                return name.replace("LogisticRegression", "Logistic Regression")
    except OSError:
        pass
    return "Logistic Regression (selected by macro F1)"


def clean_label(value: Any) -> str:
    label = str(value).strip()
    aliases = {"positive": "Positive", "pos": "Positive", "negative": "Negative", "neg": "Negative", "neutral": "Neutral", "neu": "Neutral"}
    return aliases.get(label.lower(), label[:1].upper() + label[1:] if label else "Unknown")


@st.cache_resource(show_spinner="Loading the trained model…")
def load_model() -> Any:
    if joblib is None:
        raise ModuleNotFoundError("joblib is not installed in the app environment.")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Expected saved model at {MODEL_PATH}. Add results/best_model.joblib to this app's repository folder.")
    return joblib.load(MODEL_PATH)


def unwrap_model(obj: Any) -> tuple[Any, Any]:
    if isinstance(obj, dict):
        predictor = obj.get("pipeline") or obj.get("model") or obj.get("classifier") or obj
        vectorizer = obj.get("vectorizer") or obj.get("tfidf_vectorizer")
        return predictor, vectorizer
    return obj, None


def find_vectorizer(model: Any, vectorizer: Any = None) -> Any:
    if vectorizer is not None:
        return vectorizer
    for name in ["tfidf_vectorizer.joblib", "vectorizer.joblib", "best_vectorizer.joblib", "tfidf.joblib"]:
        path = RESULTS_DIR / name
        if path.exists() and joblib is not None:
            return joblib.load(path)
    return None


def predict_texts(texts: list[str], include_scores: bool = True) -> tuple[list[str], list[dict[str, float] | None], Any, Any, Any]:
    """Predict raw text using a full pipeline or classifier + saved vectorizer."""
    saved = load_model()
    predictor, vectorizer = unwrap_model(saved)
    try:
        predictions = predictor.predict(texts)
        scoring_input = texts
        scoring_model = predictor
    except Exception as direct_error:
        vectorizer = find_vectorizer(predictor, vectorizer)
        if vectorizer is None:
            raise RuntimeError("The saved model doesn't accept raw text and no fitted vectorizer was found. Save the fitted vectorizer with the classifier, or save the full sklearn Pipeline.") from direct_error
        X = vectorizer.transform(texts)
        predictions = predictor.predict(X)
        scoring_input = X
        scoring_model = predictor
    predictions = [clean_label(x) for x in predictions]
    all_scores: list[dict[str, float] | None] = [None] * len(texts)
    if include_scores and hasattr(scoring_model, "predict_proba"):
        try:
            score_matrix = scoring_model.predict_proba(scoring_input)
            classes = getattr(scoring_model, "classes_", None)
            if classes is None and hasattr(scoring_model, "steps"):
                classes = getattr(scoring_model.steps[-1][1], "classes_", None)
            if classes is not None and len(classes) == score_matrix.shape[1]:
                for i, row in enumerate(score_matrix):
                    all_scores[i] = {clean_label(c): float(v) for c, v in zip(classes, row)}
        except Exception:
            pass
    return predictions, all_scores, saved, predictor, vectorizer


def local_linear_explanation(saved_model: Any, review: str, predicted_label: str, vectorizer_override: Any = None) -> pd.DataFrame:
    """Return local token contributions if a compatible linear sklearn Pipeline is saved."""
    predictor, vectorizer = unwrap_model(saved_model)
    if vectorizer_override is not None:
        vectorizer = vectorizer_override
    if not hasattr(predictor, "steps") or len(predictor.steps) < 2:
        return pd.DataFrame(columns=["Token / n-gram", "Contribution"])
    estimator = predictor.steps[-1][1]
    if not hasattr(estimator, "coef_") or not hasattr(estimator, "classes_"):
        return pd.DataFrame(columns=["Token / n-gram", "Contribution"])
    try:
        transformer = predictor[:-1]
        X = transformer.transform([review])
        names = transformer.get_feature_names_out()
        classes = [clean_label(c) for c in estimator.classes_]
        if predicted_label not in classes:
            return pd.DataFrame(columns=["Token / n-gram", "Contribution"])
        class_idx = classes.index(predicted_label)
        coefficients = estimator.coef_
        if coefficients.shape[0] == len(classes):
            row_coef = coefficients[class_idx]
        elif coefficients.shape[0] == 1 and len(classes) == 2:
            row_coef = coefficients[0] if class_idx == 1 else -coefficients[0]
        else:
            return pd.DataFrame(columns=["Token / n-gram", "Contribution"])
        X = X.tocsr()
        indices = X.indices
        values = X.data
        rows = [{"Token / n-gram": str(names[idx]), "Contribution": float(val * row_coef[idx])} for idx, val in zip(indices, values)]
        return pd.DataFrame(rows).sort_values("Contribution", ascending=False) if rows else pd.DataFrame(columns=["Token / n-gram", "Contribution"])
    except Exception:
        return pd.DataFrame(columns=["Token / n-gram", "Contribution"])


def aspect_mentions(text: str) -> pd.DataFrame:
    tokens = set(re.findall(r"[a-zA-Z][a-zA-Z'-]*", text.lower()))
    rows = []
    for aspect, words in ASPECT_TERMS.items():
        matched = sorted(tokens.intersection(words))
        if matched:
            rows.append({"Aspect": aspect, "Matched terms": ", ".join(matched), "Terms found": len(matched)})
    return pd.DataFrame(rows, columns=["Aspect", "Matched terms", "Terms found"])


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(f'<div class="metric"><div class="metriclabel">{html.escape(label)}</div><div class="metricvalue">{html.escape(value)}</div><div class="metricnote">{html.escape(note)}</div></div>', unsafe_allow_html=True)


def read_metrics() -> pd.DataFrame:
    if METRICS_PATH.exists():
        try:
            df = pd.read_csv(METRICS_PATH)
            # Use the saved table only when the expected metrics columns can be identified.
            low = {c.lower().replace("_", " "): c for c in df.columns}
            model_col = next((low[k] for k in ["model", "classifier", "algorithm"] if k in low), None)
            accuracy_col = next((low[k] for k in ["accuracy", "test accuracy"] if k in low), None)
            f1_col = next((low[k] for k in ["macro f1", "macro f1 score", "f1 macro"] if k in low), None)
            if model_col and accuracy_col and f1_col:
                return df.rename(columns={model_col: "Model", accuracy_col: "Accuracy", f1_col: "Macro F1"})
        except Exception:
            pass
    return METRICS_FALLBACK.copy()


def render_prediction(review: str) -> None:
    preds, scores_list, saved, predictor, vectorizer = predict_texts([review], include_scores=True)
    predicted = preds[0]
    scores = scores_list[0]
    css = predicted.lower() if predicted.lower() in {"positive", "negative", "neutral"} else "neutral"
    st.markdown(f'<div class="sentimentbox {css}"><div class="eyebrow">PREDICTION GENERATED</div><h2 style="margin:.2rem 0 .35rem">{html.escape(predicted)} sentiment</h2><p style="color:#667784;margin:0">The saved model classified this review as <b>{html.escape(predicted.lower())}</b>.</p></div>', unsafe_allow_html=True)
    if scores:
        st.write("")
        st.markdown("#### Class probability outputs")
        st.caption("Shown only when the saved estimator provides predict_proba. These scores should not be treated as calibrated certainty unless calibration was evaluated.")
        ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        fig = go.Figure(go.Bar(x=[p[1] for p in ordered], y=[p[0] for p in ordered], orientation="h", marker_color=[SENTIMENT_COLORS.get(p[0], "#147d73") for p in ordered], text=[f"{p[1]:.1%}" for p in ordered], textposition="outside"))
        fig.update_layout(height=210, margin=dict(l=4,r=32,t=4,b=4), xaxis=dict(range=[0,1], tickformat=".0%", title=None, gridcolor="#e7eeeb"), yaxis=dict(title=None), plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.write("")
    aspect_df = aspect_mentions(review)
    explain_df = local_linear_explanation(saved, review, predicted, vectorizer)
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown("#### Review diagnostics")
        a, b, c = st.columns(3)
        a.metric("Words", len(review.split()))
        b.metric("Characters", len(review))
        c.metric("Sentences", max(1, len(re.findall(r"[.!?]+", review))))
        if not aspect_df.empty:
            st.markdown("**Mentioned aspects**")
            st.dataframe(aspect_df, hide_index=True, width="stretch")
            st.caption("Aspect detection here is a transparent keyword scan, not a separately trained aspect-sentiment model.")
        else:
            st.info("No common food/service/delivery/price/ambience keywords were detected. This does not mean the review lacks those topics.")
    with col_b:
        st.markdown("#### Model explanation")
        if not explain_df.empty:
            top = pd.concat([explain_df.head(6), explain_df.tail(6)]).drop_duplicates().sort_values("Contribution")
            fig = px.bar(top, x="Contribution", y="Token / n-gram", orientation="h", color="Contribution", color_continuous_scale=["#c95f53", "#e8efec", "#147d73"])
            fig.update_layout(height=340, margin=dict(l=0,r=0,t=10,b=10), coloraxis_showscale=False, xaxis_title="Contribution toward predicted-class score", yaxis_title=None, plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            st.caption("Token contributions are an approximate local explanation for a compatible linear model pipeline. They are not causal evidence.")
        else:
            st.info("Token-level explanation is available when the saved artifact includes a compatible linear scikit-learn Pipeline with feature names and coefficients. The current saved artifact does not expose that interface.")
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Prediction": predicted, "Review": review})
    st.session_state.history = st.session_state.history[:20]


# Brand + hero
st.markdown('<div class="brand"><div class="brandmark">✳</div><div><div class="brandname">Food Review Intelligence</div><div class="brandsub">Sentiment analytics · Model evaluation · Review intelligence</div></div></div>', unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="kicker">NLP / APPLIED MACHINE LEARNING</div><h1>Go beyond the rating.<br>Understand the review.</h1><p>Analyze individual reviews, process CSV batches, evaluate predictions against labelled data, and explore the signals behind customer feedback—all in one applied ML workspace.</p><div class="chips"><span class="chip">3 sentiment classes</span><span class="chip">14,351 labelled reviews</span><span class="chip">3 classifiers benchmarked</span><span class="chip">Batch + evaluation tools</span></div></div>', unsafe_allow_html=True)

mcols = st.columns(4, gap="medium")
with mcols[0]: metric_card("Dataset size", "14,351", "Labelled food reviews")
with mcols[1]: metric_card("Sentiment classes", "03", "Positive · Negative · Neutral")
with mcols[2]: metric_card("Highest accuracy", "83.97%", "Linear SVM · recorded test run")
with mcols[3]: metric_card("Selected model", "Logistic Regression", "Highest recorded macro F1: 0.7217")

st.write("")
tabs = st.tabs(["✳ Review studio", "▦ Batch intelligence", "◉ Evaluation lab", "⌁ Dataset explorer", "▤ Model benchmark", "ⓘ Model card"])

# TAB 1: Single review, explanation, session history.
with tabs[0]:
    st.markdown('<div class="eyebrow">01 / LIVE INFERENCE</div><div class="section-title">Analyze a customer review</div><div class="subcopy">Enter a review and inspect the model output, keyword-level aspect mentions, and—when the saved pipeline supports it—local token contributions.</div>', unsafe_allow_html=True)
    left, right = st.columns([1.1,.9], gap="large")
    with left:
        sample_cols = st.columns(3)
        for idx, (name, sample) in enumerate(SAMPLE_REVIEWS.items()):
            if sample_cols[idx].button(f"Load {name.lower()}", key=f"sample_v2_{idx}", width="stretch"):
                st.session_state.review_text_v2 = sample
        with st.form("review_form_v2", clear_on_submit=False):
            review = st.text_area("Review text", key="review_text_v2", height=190, placeholder="Example: The noodles arrived hot, the flavors were balanced, and the staff were welcoming.", help="One English-language review at a time.")
            submit = st.form_submit_button("Analyze review →", type="primary", width="stretch")
        if submit:
            if len(review.strip()) < 3:
                st.warning("Enter a longer review before analysis.")
            else:
                try:
                    with st.spinner("Running the saved classifier…"):
                        render_prediction(review.strip())
                except Exception as exc:
                    st.error(f"Prediction failed: {type(exc).__name__}: {exc}")
                    st.caption(f"Model file expected: {MODEL_PATH}")
    with right:
        st.markdown('<div class="card"><div class="eyebrow">INFERENCE PIPELINE</div><h3>From raw text to model output</h3><ol><li><b>Input validation</b> — review text is checked for usable content.</li><li><b>Text representation</b> — the saved vectorizer/pipeline prepares features consistent with training.</li><li><b>Classification</b> — the trained classifier predicts one of three sentiments.</li><li><b>Interpretation</b> — optional class scores and token signals are displayed when supported by the saved artifact.</li></ol></div>', unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="insight"><b>Research point:</b> a convincing interface is not proof of model correctness. Use the evaluation lab with a held-out labelled file to measure real generalization.</div>', unsafe_allow_html=True)
    if st.session_state.get("history"):
        st.markdown("#### Recent predictions (this browser session)")
        hist = pd.DataFrame(st.session_state.history)
        st.dataframe(hist, hide_index=True, width="stretch")
        st.download_button("Export session history", hist.to_csv(index=False).encode("utf-8"), file_name="review_prediction_history.csv", mime="text/csv", key="download_history_v2")

# TAB 2: Batch lab
with tabs[1]:
    st.markdown('<div class="eyebrow">02 / BULK PROCESSING</div><div class="section-title">Batch intelligence</div><div class="subcopy">Run many reviews in one operation, inspect the sentiment mix, and download row-level predictions for reporting or further analysis.</div>', unsafe_allow_html=True)
    mode = st.radio("Choose batch input", ["Upload CSV", "Paste reviews"], horizontal=True, key="batch_mode_v2")
    texts: list[str] = []
    input_name = "manual_batch"
    if mode == "Upload CSV":
        upload = st.file_uploader("Upload a CSV file containing review text", type=["csv"], key="batch_upload_v2")
        if upload is not None:
            try:
                batch_source = pd.read_csv(upload)
                if len(batch_source.columns) == 0:
                    st.error("The CSV has no columns.")
                else:
                    text_col = st.selectbox("Select the review-text column", batch_source.columns.tolist(), key="batch_text_col_v2")
                    st.caption(f"Loaded {len(batch_source):,} rows. A maximum of 5,000 rows can be processed in one run.")
                    texts = batch_source[text_col].dropna().astype(str).str.strip().tolist()
                    texts = [t for t in texts if t]
                    input_name = upload.name.rsplit(".", 1)[0]
            except Exception as exc:
                st.error(f"Could not read CSV: {exc}")
    else:
        paste = st.text_area("One review per line", height=180, placeholder="The pasta was fresh and tasty.\nThe delivery was 45 minutes late.\nThe meal was average.", key="paste_batch_v2")
        texts = [line.strip() for line in paste.splitlines() if line.strip()]
    if st.button("Run batch analysis →", type="primary", key="run_batch_v2", width="stretch"):
        if not texts:
            st.warning("Add at least one non-empty review.")
        else:
            if len(texts) > 5000:
                st.warning("For responsiveness, only the first 5,000 reviews will be processed.")
                texts = texts[:5000]
            try:
                with st.spinner(f"Classifying {len(texts):,} reviews…"):
                    pred_labels, score_rows, _, _, _ = predict_texts(texts, include_scores=True)
                out = pd.DataFrame({"Review": texts, "Predicted sentiment": pred_labels, "Word count": [len(t.split()) for t in texts]})
                if score_rows and any(s is not None for s in score_rows):
                    for cls in ["Positive", "Neutral", "Negative"]:
                        out[f"Score: {cls}"] = [s.get(cls) if s else None for s in score_rows]
                st.session_state.batch_output_v2 = out
                st.success(f"Completed {len(out):,} predictions.")
            except Exception as exc:
                st.error(f"Batch prediction failed: {type(exc).__name__}: {exc}")
    if st.session_state.get("batch_output_v2") is not None:
        out = st.session_state.batch_output_v2
        summary = out["Predicted sentiment"].value_counts().rename_axis("Sentiment").reset_index(name="Reviews")
        c1,c2 = st.columns([.85,1.15], gap="large")
        with c1:
            st.markdown("#### Batch sentiment profile")
            st.dataframe(summary, hide_index=True, width="stretch")
            fig = px.pie(summary, names="Sentiment", values="Reviews", hole=.62, color="Sentiment", color_discrete_map=SENTIMENT_COLORS)
            fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=5), legend_title=None)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        with c2:
            st.markdown("#### Row-level predictions")
            st.dataframe(out.head(1000), hide_index=True, width="stretch", height=390)
            st.caption("Preview limited to 1,000 rows. The download contains the full processed batch.")
            st.download_button("Download prediction results (.csv)", out.to_csv(index=False).encode("utf-8"), file_name="food_review_batch_predictions.csv", mime="text/csv", width="stretch", key="batch_download_v2")
        st.markdown("#### Example reviews by predicted class")
        excols = st.columns(3)
        for col, cls in zip(excols, ["Positive", "Negative", "Neutral"]):
            with col:
                st.markdown(f"**{cls} examples**")
                rows = out.loc[out["Predicted sentiment"] == cls, "Review"].head(3).tolist()
                if rows:
                    for t in rows:
                        st.caption("“" + (t[:180] + "…" if len(t) > 180 else t) + "”")
                else:
                    st.caption("No items in this class for the current batch.")

# TAB 3: Evaluation lab
with tabs[2]:
    st.markdown('<div class="eyebrow">03 / GENERALIZATION CHECK</div><div class="section-title">Evaluation lab</div><div class="subcopy">Upload an independently labelled CSV to calculate accuracy, macro/weighted F1, a per-class report, and a confusion matrix for the deployed model.</div>', unsafe_allow_html=True)
    st.markdown('<div class="caution"><b>Important evaluation rule:</b> use held-out test rows that were not used to train the saved model. Evaluating on the same training dataset gives an optimistic and potentially misleading result.</div>', unsafe_allow_html=True)
    eval_upload = st.file_uploader("Upload labelled review CSV", type=["csv"], key="eval_upload_v2")
    if eval_upload is not None:
        try:
            eval_df = pd.read_csv(eval_upload)
            if len(eval_df.columns) < 2:
                st.error("The file needs at least a review-text column and a true-label column.")
            else:
                e1,e2 = st.columns(2)
                with e1: eval_text_col = st.selectbox("Review text column", eval_df.columns.tolist(), key="eval_text_col_v2")
                with e2:
                    label_candidates = [c for c in eval_df.columns if c != eval_text_col]
                    eval_label_col = st.selectbox("True sentiment label column", label_candidates, key="eval_label_col_v2")
                st.caption(f"{len(eval_df):,} rows in upload. Up to 5,000 labelled rows can be evaluated per run.")
                if st.button("Evaluate on labelled data →", type="primary", key="evaluate_file_v2", width="stretch"):
                    work = eval_df[[eval_text_col, eval_label_col]].dropna().copy()
                    work[eval_text_col] = work[eval_text_col].astype(str).str.strip()
                    work["True sentiment"] = work[eval_label_col].map(clean_label)
                    work = work[work[eval_text_col].str.len() >= 3]
                    work = work[work["True sentiment"].isin(["Positive","Negative","Neutral"])]
                    work = work.head(5000)
                    if work.empty:
                        st.error("No rows with usable text and recognized Positive/Negative/Neutral labels were found.")
                    else:
                        try:
                            from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
                            with st.spinner(f"Predicting and evaluating {len(work):,} labelled reviews…"):
                                predicted, _, _, _, _ = predict_texts(work[eval_text_col].tolist(), include_scores=False)
                            truth = work["True sentiment"].tolist()
                            labels = ["Negative", "Neutral", "Positive"]
                            report = classification_report(truth, predicted, labels=labels, output_dict=True, zero_division=0)
                            res = work[[eval_text_col]].rename(columns={eval_text_col:"Review"}).reset_index(drop=True)
                            res["True sentiment"] = truth
                            res["Predicted sentiment"] = predicted
                            res["Correct"] = res["True sentiment"] == res["Predicted sentiment"]
                            st.session_state.eval_output_v2 = res
                            st.session_state.eval_metrics_v2 = report
                            st.session_state.eval_cm_v2 = confusion_matrix(truth, predicted, labels=labels)
                            st.session_state.eval_labels_v2 = labels
                            st.success("Evaluation completed. Results are shown below.")
                        except Exception as exc:
                            st.error(f"Evaluation failed: {type(exc).__name__}: {exc}")
        except Exception as exc:
            st.error(f"Could not read uploaded CSV: {exc}")
    if st.session_state.get("eval_metrics_v2"):
        report = st.session_state.eval_metrics_v2
        res = st.session_state.eval_output_v2
        k1,k2,k3,k4 = st.columns(4)
        with k1: metric_card("Evaluation accuracy", f"{res['Correct'].mean():.2%}", f"{len(res):,} labelled rows")
        with k2: metric_card("Macro precision", f"{report['macro avg']['precision']:.4f}", "Equal class weighting")
        with k3: metric_card("Macro recall", f"{report['macro avg']['recall']:.4f}", "Equal class weighting")
        with k4: metric_card("Macro F1", f"{report['macro avg']['f1-score']:.4f}", "Main balanced score")
        cm = pd.DataFrame(st.session_state.eval_cm_v2, index=st.session_state.eval_labels_v2, columns=st.session_state.eval_labels_v2)
        c1,c2 = st.columns([1,1], gap="large")
        with c1:
            st.markdown("#### Confusion matrix")
            fig = px.imshow(cm, text_auto=True, aspect="auto", color_continuous_scale="Teal", labels=dict(x="Predicted label", y="True label", color="Count"))
            fig.update_layout(height=390, margin=dict(l=0,r=0,t=10,b=5))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        with c2:
            st.markdown("#### Per-class performance")
            rpt = pd.DataFrame(report).T
            rpt.index.name = "Class / metric"
            st.dataframe(rpt.round(4), width="stretch")
            st.download_button("Download evaluation rows", res.to_csv(index=False).encode("utf-8"), file_name="heldout_evaluation_predictions.csv", mime="text/csv", width="stretch", key="download_eval_v2")

# TAB 4: Dataset explorer
with tabs[3]:
    st.markdown('<div class="eyebrow">04 / DATA EXPLORATION</div><div class="section-title">Dataset intelligence</div><div class="subcopy">Explore sentiment balance, review ratings, time trends, locations, restaurant categories, and frequent terms from your own CSV without publishing the raw dataset in the repository.</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight">Upload your labelled project CSV here when you want the charts to use actual records. The deployment package intentionally does not need to include the raw dataset.</div>', unsafe_allow_html=True)
    data_upload = st.file_uploader("Upload dataset CSV for exploration", type=["csv"], key="data_upload_v2")
    if data_upload is not None:
        try:
            df = pd.read_csv(data_upload)
            st.caption(f"Loaded {len(df):,} rows × {len(df.columns)} columns.")
            c1,c2,c3,c4 = st.columns(4)
            with c1: metric_card("Rows", f"{len(df):,}", "Uploaded dataset")
            with c2: metric_card("Columns", str(len(df.columns)), "Data fields")
            with c3: metric_card("Missing cells", f"{int(df.isna().sum().sum()):,}", "Across all columns")
            with c4: metric_card("Duplicate rows", f"{int(df.duplicated().sum()):,}", "Exact row duplicates")
            lowmap = {c.lower().strip(): c for c in df.columns}
            sentiment_col = next((lowmap[k] for k in ["rating_review", "sentiment", "label", "target", "sentiment_label"] if k in lowmap), None)
            text_col = next((lowmap[k] for k in ["text", "review", "review_text", "content"] if k in lowmap), None)
            rating_col = next((lowmap[k] for k in ["stars_review", "stars", "rating", "review_rating"] if k in lowmap), None)
            date_col = next((lowmap[k] for k in ["date", "review_date", "created_at"] if k in lowmap), None)
            category_col = next((lowmap[k] for k in ["categories", "category", "cuisine"] if k in lowmap), None)
            city_col = next((lowmap[k] for k in ["city", "location", "state"] if k in lowmap), None)
            f1,f2 = st.columns(2)
            if sentiment_col:
                sentiment_counts = df[sentiment_col].astype(str).map(clean_label).value_counts().rename_axis("Sentiment").reset_index(name="Reviews")
                with f1:
                    st.markdown("#### Sentiment distribution")
                    fig = px.pie(sentiment_counts, names="Sentiment", values="Reviews", hole=.58, color="Sentiment", color_discrete_map=SENTIMENT_COLORS)
                    fig.update_layout(height=360, margin=dict(l=0,r=0,t=10,b=5), legend_title=None)
                    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            else:
                with f1: st.warning("No known sentiment-label column found. Rename it to rating_review or select label mappings in a future extension.")
            with f2:
                st.markdown("#### Rating distribution" if rating_col else "#### Dataset preview")
                if rating_col:
                    rat = df[rating_col].value_counts(dropna=False).sort_index().rename_axis("Rating").reset_index(name="Reviews")
                    fig = px.bar(rat, x="Rating", y="Reviews", color="Reviews", color_continuous_scale="Teal")
                    fig.update_layout(height=360, margin=dict(l=0,r=0,t=10,b=5), coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white")
                    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
                else:
                    st.dataframe(df.head(25), width="stretch", height=350)
            if date_col:
                dt = pd.to_datetime(df[date_col], errors="coerce")
                tdf = df.loc[dt.notna()].copy()
                tdf["Month"] = dt.loc[dt.notna()].dt.to_period("M").astype(str).values
                if not tdf.empty:
                    st.markdown("#### Review volume over time")
                    monthly = tdf.groupby("Month").size().rename("Reviews").reset_index()
                    fig = px.line(monthly, x="Month", y="Reviews", markers=True)
                    fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=5), plot_bgcolor="white", paper_bgcolor="white")
                    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            if sentiment_col and rating_col:
                st.markdown("#### Sentiment vs review stars")
                cross = df.assign(_sentiment=df[sentiment_col].astype(str).map(clean_label)).groupby([rating_col,"_sentiment"]).size().rename("Reviews").reset_index()
                fig = px.bar(cross, x=rating_col, y="Reviews", color="_sentiment", barmode="stack", color_discrete_map=SENTIMENT_COLORS)
                fig.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=5), legend_title="Sentiment", plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            catcol = category_col or city_col
            if catcol:
                st.markdown(f"#### Review volume by {catcol}")
                top = df[catcol].fillna("Unknown").astype(str).value_counts().head(15).rename_axis(catcol).reset_index(name="Reviews")
                fig = px.bar(top.sort_values("Reviews"), x="Reviews", y=catcol, orientation="h", color="Reviews", color_continuous_scale="Teal")
                fig.update_layout(height=380, margin=dict(l=0,r=0,t=10,b=5), coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            if text_col:
                st.markdown("#### Frequent terms")
                joined = " ".join(df[text_col].dropna().astype(str).head(10000).tolist()).lower()
                toks = [t for t in re.findall(r"[a-z]{3,}", joined) if t not in STOPWORDS]
                terms = pd.DataFrame(Counter(toks).most_common(20), columns=["Term", "Frequency"])
                if not terms.empty:
                    fig = px.bar(terms.sort_values("Frequency"), x="Frequency", y="Term", orientation="h", color="Frequency", color_continuous_scale="Teal")
                    fig.update_layout(height=460, margin=dict(l=0,r=0,t=10,b=5), coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white")
                    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
                    st.caption("Basic frequency analysis over up to the first 10,000 non-empty reviews; stopwords removed using a small built-in list.")
            with st.expander("Inspect uploaded data (first 100 rows)"):
                st.dataframe(df.head(100), width="stretch", height=360)
        except Exception as exc:
            st.error(f"Dataset exploration failed: {type(exc).__name__}: {exc}")
    else:
        dist = pd.DataFrame({"Sentiment": list(SENTIMENT_COUNTS.keys()), "Reviews": list(SENTIMENT_COUNTS.values())})
        dist["Share"] = dist["Reviews"] / dist["Reviews"].sum()
        left,right = st.columns([1,1], gap="large")
        with left:
            st.markdown("#### Prepared dataset snapshot")
            fig = px.bar(dist, x="Sentiment", y="Reviews", color="Sentiment", color_discrete_map=SENTIMENT_COLORS)
            fig.update_layout(height=330, margin=dict(l=0,r=0,t=10,b=5), showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        with right:
            st.markdown("#### Why class balance matters")
            for _,row in dist.iterrows():
                st.progress(float(row["Share"]), text=f"{row['Sentiment']} · {int(row['Reviews']):,} reviews · {row['Share']:.1%}")
            st.caption("Upload the source CSV to explore rating, location, category, and time fields dynamically.")

# TAB 5: model benchmark
with tabs[4]:
    st.markdown('<div class="eyebrow">05 / COMPARATIVE EVALUATION</div><div class="section-title">Model benchmark</div><div class="subcopy">The best model is not necessarily the one with the highest accuracy. Compare multiple metrics and examine class-level trade-offs.</div>', unsafe_allow_html=True)
    metrics = read_metrics()
    if "Accuracy" in metrics.columns:
        metrics["Accuracy"] = pd.to_numeric(metrics["Accuracy"], errors="coerce")
        if metrics["Accuracy"].dropna().max() > 1.01: metrics["Accuracy"] = metrics["Accuracy"] / 100
    if "Macro F1" in metrics.columns:
        metrics["Macro F1"] = pd.to_numeric(metrics["Macro F1"], errors="coerce")
        if metrics["Macro F1"].dropna().max() > 1.01: metrics["Macro F1"] = metrics["Macro F1"] / 100
    max_acc = metrics.loc[metrics["Accuracy"].idxmax()] if "Accuracy" in metrics and metrics["Accuracy"].notna().any() else None
    max_f1 = metrics.loc[metrics["Macro F1"].idxmax()] if "Macro F1" in metrics and metrics["Macro F1"].notna().any() else None
    a,b,c = st.columns(3)
    with a: metric_card("Best accuracy", f"{max_acc['Accuracy']:.2%}" if max_acc is not None else "N/A", str(max_acc["Model"]) if max_acc is not None else "No metric")
    with b: metric_card("Best macro F1", f"{max_f1['Macro F1']:.4f}" if max_f1 is not None else "N/A", str(max_f1["Model"]) if max_f1 is not None else "No metric")
    with c: metric_card("Model deployed", model_name(), "Selected by the recorded macro-F1 criterion")
    chartcols = [c for c in ["Accuracy", "Macro F1", "Weighted F1", "Macro Precision", "Macro Recall"] if c in metrics.columns]
    if len(metrics) and chartcols:
        chart = metrics.melt(id_vars=["Model"], value_vars=chartcols, var_name="Metric", value_name="Score")
        fig = px.bar(chart, x="Model", y="Score", color="Metric", barmode="group", text_auto=".2f")
        fig.update_layout(height=400, margin=dict(l=0,r=0,t=18,b=5), yaxis=dict(range=[0,1], title="Score", gridcolor="#e5ece9"), xaxis_title=None, legend_title=None, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.dataframe(metrics.round(4), hide_index=True, width="stretch")
    if (RESULTS_DIR / "report_LogisticRegression.csv").exists():
        with st.expander("View Logistic Regression classification report"):
            st.dataframe(pd.read_csv(RESULTS_DIR / "report_LogisticRegression.csv"), width="stretch")
    with st.expander("How to interpret the benchmark"):
        st.markdown("- **Accuracy** measures the overall proportion of correct predictions.\n- **Macro F1** averages F1 across classes equally, helping make weaker minority-class results visible.\n- **Weighted F1** weights each class by its support.\n- Select a model using the metric that best reflects the project objective, not accuracy alone.")

# TAB 6: model card / limitations
with tabs[5]:
    st.markdown('<div class="eyebrow">06 / MODEL TRANSPARENCY</div><div class="section-title">Model card & limitations</div><div class="subcopy">A concise technical record of what this model is designed to do, how it is evaluated, and where its predictions should be treated cautiously.</div>', unsafe_allow_html=True)
    l,r = st.columns(2, gap="large")
    with l:
        st.markdown('<div class="card"><div class="eyebrow">INTENDED USE</div><h3>Classify review sentiment</h3><p>Input: English-language restaurant review text.</p><p>Output: Positive, Negative, or Neutral.</p><p>Primary use: academic demonstration and batch exploration of customer feedback.</p><hr><div class="eyebrow">ARTIFACT STATUS</div>', unsafe_allow_html=True)
        st.write(f"Model file found: **{'Yes' if MODEL_PATH.exists() else 'No'}**")
        st.write(f"Saved model path: `{MODEL_PATH}`")
        st.write(f"Selected model: **{model_name()}**")
        st.markdown('</div>', unsafe_allow_html=True)
    with r:
        st.markdown('<div class="card"><div class="eyebrow">KNOWN LIMITATIONS</div><h3>Predictions are estimates</h3><ul><li>Neutral examples are less frequent and harder to classify in the recorded run.</li><li>Sarcasm, mixed sentiment, slang, spelling variants, and domain shifts may reduce reliability.</li><li>Class score outputs are not necessarily calibrated probabilities.</li><li>Dataset-level patterns do not imply causal explanations about restaurant quality.</li></ul><hr><div class="eyebrow">RECOMMENDED NEXT EXPERIMENTS</div><ul><li>Evaluate on an untouched held-out dataset.</li><li>Improve neutral-class recall and macro F1.</li><li>Compare TF-IDF with an embedding-based text representation.</li><li>Perform error analysis by review length, rating, and aspect mention.</li></ul></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="insight"><b>Academic integrity note:</b> the interactive app predicts with a saved model. It does not retrain the model during each request. Any new performance claim should come from a documented evaluation run.</div>', unsafe_allow_html=True)

st.markdown('<div class="footer"><span>Food Review Intelligence · B.Tech CSE Minor Project</span><span>Applied NLP prototype · Outputs may be imperfect</span></div>', unsafe_allow_html=True)
