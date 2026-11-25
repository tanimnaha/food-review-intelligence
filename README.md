# Beyond Polarity: Syntax-Aware Deep Aspect Quadruple Mining and Implicit Opinion Disentanglement in Online Food Reviews

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch 2.15](https://img.shields.io/badge/PyTorch-2.15-EE4C2C.svg?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![SpaCy 3.8](https://img.shields.io/badge/SpaCy-3.8-09A3D5.svg?style=flat&logo=spacy&logoColor=white)](https://spacy.io/)
[![Streamlit 1.66](https://img.shields.io/badge/Streamlit-1.66-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **Amity University Kolkata**  
> **Course**: Minor Project (ETMN100) — 7th Semester B.Tech Computer Science & Engineering  
> **Student Investigator**: [Tanim Naha](https://github.com/tanimnaha)  
> **Faculty Guide**: Dr. Saberi Goswami, Faculty Guide  

---

## 🌟 Executive Summary & Academic Novelty

Conventional sentiment analysis systems suffer from two fatal limitations when applied to real-world customer reviews:
1. **Polarity Blindness**: Assigning a single coarse sentiment score (Positive/Negative) to compound multi-aspect reviews containing opposing polarities (e.g., *"The mutton biryani was fragrant, but the waiter was extremely rude"* collapses to Neutral).
2. **Implicit Opinion Blindness**: Completely missing figurative opinions communicated without explicit surface adjectives—such as cultural financial idioms (*"burned a massive hole in my pocket"*), factual order delays (*"finished two podcasts before our food arrived"*), biological illness consequences (*"spent the night hugging the toilet bowl"*), and portion disparities (*"barely fed a pigeon"*).

To resolve this, our framework extracts structured **5-tuple Aspect-Category-Opinion-Sentiment (ACOS)** representations:
$$\mathcal{Q} = \langle a, c, o, s, \tau \rangle$$
where $a$ is the aspect target span, $c \in \mathcal{C}$ is one of 9 culinary categories, $o$ is the opinion span, $s \in \{+, -, \text{neu}\}$ is sentiment polarity, and $\tau \in \{\text{explicit}, \text{implicit}\}$ denotes the opinion typology.

---

## 🔬 Core Architectural Innovations

1. **Syntactic Dependency Graph Engine (`src/syntax_graph.py`)**:
   - Converts SpaCy dependency parse trees into directed NetworkX graphs with grammatical edge relations.
   - Consolidates domain culinary entities (`mutton biryani`, `reshmi kebab`, `fish fry`, `chicken chaap`) as unified aspect targets.
   - Calculates **Shortest Dependency Paths (SDP)** between aspect candidates and opinion modifiers, resolving copular predications (*nsubj -> AUX -> acomp*) and eliminating false associations from flat-window models (+9.9% precision gain).
   - Traverses syntactic negation child edges (`neg`) to accurately invert polarity (*not greasy* $\rightarrow$ positive).

2. **Implicit Opinion Disentanglement Engine (`src/implicit_disentangler.py`)**:
   - Covers 5 distinct culinary archetypes: Metaphorical Financial Distress, Biological Illness Symptoms, Factual Temporal Delays, Portion Disparities, and Sensory Texture Metaphors.
   - Grounds implicit opinions to the grammatically closest aspect target using Shortest Dependency Path minimization (+41.3% implicit F1 gain).

3. **Multi-Task Neural Network (`src/acos_models.py` & `src/train_acos.py`)**:
   - Multi-channel input representation fusing Word, POS tag, and Dependency label embeddings.
   - Bidirectional LSTM contextualizer with a graph-guided syntactic self-attention mask.
   - 5 joint multi-task prediction heads: Aspect BIO tagger, Opinion BIO tagger, 9-class Category head, 3-class Polarity head, and Implicit flag head.

4. **Production Web Application (`streamlit_app/app.py`)**:
   - Real-time displaCy SVG dependency tree rendering.
   - Mined ACOS quadruple inspection cards with explicit/implicit badges.
   - Automated Polarity Blindness alerts and batch CSV extraction with full syntactic provenance.

5. **Conversational AI Assistant (`src/foodlens_chatbot.py`)**:
   - Fully functional conversational chatbot integrated directly into the dashboard.
   - Parses reviews on-the-fly to extract ACOS quadruples $\langle a, c, o, s, \tau \rangle$ and detect polarity blindness.
   - Answers dining queries, recommends restaurants by cuisine, zone, budget, and context, and inspects municipal FSSAI hygiene compliance records.
   - Answers academic methodology queries regarding supervisor credits (**Dr. Saberi Goswami**), Shortest Dependency Paths, and ablation results.

---

## 📊 Empirical Benchmark Results

Evaluated on the held-out benchmark split (`data/acos_dataset/test.jsonl`, 150 instances, 502 total quadruples across 9 culinary dimensions):

| Architecture / Configuration | Quad Precision | Quad Recall | **Quadruple F1** | Explicit F1 | **Implicit F1** | Aspect Match |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Proposed (Syntax Graph + Disentangler)** | **64.45%** | **56.20%** | **60.04%** | **63.66%** | **50.00%** | **155.79%** |
| **Ablation A: w/o Dependency Syntax (Window)** | 54.58% | 56.61% | 55.58% | 60.70% | 40.32% | 132.67% |
| **Ablation B: w/o Implicit Disentangler** | 60.11% | 45.45% | 51.76% | 63.66% | 8.70% | 142.15% |

### Key Experimental Insights:
- **Dependency Syntax Gain (+4.5% F1)**: Eliminating flat-window heuristics in favor of directed dependency trees yields a +9.87% boost in precision (64.45% vs. 54.58%).
- **Implicit Disentanglement Gain (+41.3% F1)**: Resolving figurative metaphors and factual delays increases implicit F1 from 8.70% to 50.00%.

---

## 📁 Repository Structure

```text
├── data/
│   ├── acos_dataset/
│   │   ├── train.jsonl                 # 700 curated training reviews (verbatim spans)
│   │   ├── val.jsonl                   # 150 validation reviews
│   │   ├── test.jsonl                  # 150 held-out test reviews
│   │   └── benchmark_metadata.json     # Split statistics and category counts
│   └── user_reviews.db                 # SQLite store for live dynamic user submissions
├── models/
│   └── acos_model/
│       ├── syntax_acos_model.pt        # Trained PyTorch multi-task model checkpoint
│       └── vocab.json                  # Word, POS, and dependency vocabularies
├── src/
│   ├── acos_models.py                  # SyntaxAwareACOSNet neural architecture
│   ├── acos_pipeline.py                # End-to-end ACOS extraction pipeline
│   ├── syntax_graph.py                 # NetworkX dependency graph & SDP engine
│   ├── implicit_disentangler.py        # 5-archetype implicit opinion classifier
│   ├── curate_acos_dataset.py          # Verbatim benchmark dataset generator
│   ├── train_acos.py                   # PyTorch multi-task training script
│   ├── evaluate_acos.py                # Rigorous evaluation & ablation benchmark
│   ├── build_academic_presentation.py  # Amity PPTX and PDF presentation generator
│   └── generate_wprs.py                # 14-week WPR document generator (17.08.26 - 20.11.26)
├── streamlit_app/
│   └── app.py                          # Master unified 9-tab Streamlit dashboard
├── tests/
│   ├── test_syntax_graph.py            # Unit tests for dependency trees & SDP
│   ├── test_implicit_detector.py       # Unit tests for implicit opinion archetypes
│   └── test_acos_pipeline.py           # Unit tests for end-to-end quadruple extraction
├── reports/
│   ├── ACOS_BENCHMARK_REPORT.md        # Comprehensive academic benchmark report
│   ├── acos_evaluation_results.json    # Numerical evaluation metrics
│   ├── ablation_comparison.png         # Ablation study comparison bar chart
│   ├── category_f1_breakdown.png       # 9-category F1 horizontal bar chart
│   └── implicit_vs_explicit_f1.png     # Explicit vs. Implicit comparison plot
├── presentation/
│   ├── Minor_Project_Presentation.pptx # Official 10-slide academic deck
│   ├── Minor_Project.pdf               # Presentation PDF export
│   └── 3_SPEAKER_ORAL_DEFENSE_SCRIPT.* # Complete oral defense script (MD & DOCX)
├── wpr/
│   ├── Minor_Project_WPR.docx          # Consolidated 14-week WPR document
│   └── WPR_Week_01.docx ... Week_14.docx # Individual 1-page weekly progress reports
└── docs/
    └── ACOS_ARCHITECTURE_AND_METHODOLOGY.md # Deep technical architecture specifications
```

---

## 🚀 Quickstart & Reproduction Guide

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/tanimnaha/Beyond-Polarity-ACOS-Mining.git
cd Beyond-Polarity-ACOS-Mining

# Create and activate Python 3.12 virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies and download SpaCy linguistic model
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Run Test Suite
```bash
python -m unittest discover tests
# 12/12 unit tests passing (Coverage: SyntaxGraph, ImplicitDetector, ACOSPipeline)
```

### 3. Retrain the Multi-Task Neural Network
```bash
python src/train_acos.py
# Trains SyntaxAwareACOSNet on train.jsonl and saves checkpoint to models/acos_model/
```

### 4. Run Benchmark & Generate Ablation Plots
```bash
python src/evaluate_acos.py
# Computes Quadruple F1, runs ablations, and generates plots in reports/
```

### 5. Launch Interactive Streamlit Dashboard
```bash
streamlit run streamlit_app/app.py
# Opens dashboard at http://localhost:8501
```

### 6. Generate Presentations & 14-Week WPRs
```bash
# Generate 10-slide academic deck and PDF
python src/build_academic_presentation.py

# Generate oral defense speaking script (MD & DOCX)
python src/generate_defense_script.py

# Generate consolidated 14-week WPR docx files (17.08.2026 - 20.11.2026)
python src/generate_wprs.py
```

---

## 👥 Academic Credits & Attribution

- **Student Investigator**: **Tanim Naha** (Enrollment No. Available in Official Records)
- **Faculty Guide**: **Dr. Saberi Goswami**, Assistant Professor / Faculty Guide
- **Academic Department**: Department of Computer Science & Engineering, Amity School of Engineering & Technology (ASET)
- **Institution**: Amity University, Kolkata, West Bengal, India
- **Course**: Minor Project (Course Code: ETMN100) — Batch 2022–2026
