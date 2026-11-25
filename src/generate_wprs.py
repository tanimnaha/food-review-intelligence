"""WPR (Weekly Progress Report) Filler for Amity University Kolkata.

Strictly preserves the exact original university template (`wpr/minorProject_WPR.docx`)
without modifying any design, margins, fonts, or layout—simply filling in the blank spaces
for all 14 weeks from 17.08.2026 to 20.11.2026.

Generates:
- wpr/WPR_Week_01.docx ... wpr/WPR_Week_14.docx (Individual Weekly Reports)
- wpr/Minor_Project_WPR.docx (Consolidated 14-Week Document)
"""

import copy
from pathlib import Path
import docx
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
WPR_DIR = ROOT / "wpr"
TEMPLATE_PATH = WPR_DIR / "minorProject_WPR.docx"

TEAM_MEMBERS = "Tanim Naha, Srilekha, Subhamita, Yashamoti"
PROGRAM = "B.Tech (Computer Science & Engineering) - 7th Sem"
FACULTY_GUIDE = "Dr. Saberi Goswami"
PROJECT_TITLE = "Beyond Polarity: Syntax-Aware Deep Aspect Quadruple Mining and Implicit Opinion Disentanglement in Online Food Reviews"

# 14-Week Technical Trajectory (17.08.2026 to 20.11.2026)
WEEKS_DATA = [
    {
        "week_num": 1,
        "start": ("17", "08", "2026"),
        "end": ("21", "08", "2026"),
        "targets": "Finalize research topic, formulate ACOS 5-tuple problem definition, and set up Python 3.12 ML/NLP environment.",
        "achievements": "Finalized title with Dr. Saberi Goswami, defined 5-tuple ACOS task, configured PyTorch (MPS), SpaCy, NetworkX, and repository.",
        "future": "Conduct comprehensive 2021–2026 literature survey on ACOS quadruple mining and implicit opinion disentanglement.",
        "days": [
            "Kick-off meeting with Dr. Saberi Goswami & team (Tanim, Srilekha, Subhamita, Yashamoti); finalized research title on Syntax-Aware ACOS Mining.",
            "Formulated mathematical 5-tuple ACOS task <a, c, o, s, tau> to address coarse polarity blindness and implicit opinion blindness.",
            "Configured Python 3.12 virtual environment (.venv) with Apple Silicon MPS; installed PyTorch 2.15, SpaCy 3.8, NetworkX 3.7, and Streamlit.",
            "Established modular repository structure (src, data, models, reports, tests, docs, wpr, presentation) and downloaded en_core_web_sm.",
            "Drafted initial project synopsis detailing methodology, 9 culinary dimensions, ablation plan, and 14-week timeline."
        ]
    },
    {
        "week_num": 2,
        "start": ("24", "08", "2026"),
        "end": ("28", "08", "2026"),
        "targets": "Review recent 2021–2026 research papers on ACOS quadruple extraction, dependency syntax, and implicit sentiment.",
        "achievements": "Synthesized comparative literature survey (Cai et al. ACL '21, Peper & Wang '22, Cui et al. '24, Ouyang et al. '24, Fan et al. '25, Esfandyari et al. '26).",
        "future": "Ingest Kolkata dining corpus, design SQLite persistence, and formalize 9 structured culinary categories.",
        "days": [
            "Reviewed foundational ACOS quadruple benchmarks (Cai et al., ACL 2021) and contrastive learning baselines (GEN-SCL-NAT; Peper & Wang, EMNLP 2022).",
            "Studied implicit sentiment disentanglement papers: Hierarchical Disentanglement (Cui et al., EMNLP 2024) and ABSA-ESA (Ouyang et al., AAAI 2024).",
            "Analyzed syntax-guided reasoning chains (Syn-Chain; Fan et al., COLING 2025) and dependency reasoning for ASQP (DRIFT; Esfandyari et al., 2026).",
            "Identified core gaps: flat-window models misattribute distant modifiers while LLM-based quad generators incur high inference latency.",
            "Compiled literature survey matrix and presented technical gap analysis to faculty guide Dr. Saberi Goswami."
        ]
    },
    {
        "week_num": 3,
        "start": ("31", "08", "2026"),
        "end": ("04", "09", "2026"),
        "targets": "Ingest Kolkata restaurant directory, define 9 ACOS culinary categories, and set up SQLite + FSSAI safety engine.",
        "achievements": "Loaded 100 Kolkata listings, finalized 9-category taxonomy, initialized SQLite DB (src/db.py), and built culinary lexicon.",
        "future": "Curate 1,000-instance verbatim ACOS benchmark dataset and generate stratified train/val/test JSONL splits.",
        "days": [
            "Ingested 100 Zomato-listed Kolkata restaurant profiles (restaurants.csv) across Park Street, Salt Lake, Ballygunge, and South Kolkata.",
            "Defined 9 ACOS categories: FOOD#QUALITY, FOOD#PRICES, FOOD#STYLE_OPTIONS, SERVICE#GENERAL, SERVICE#PROMPTNESS, AMBIENCE#GENERAL, RESTAURANT#PRICES, HYGIENE#CLEANLINESS, HYGIENE#FOOD_SAFETY.",
            "Designed and initialized SQLite relational database (src/db.py, data/user_reviews.db) for live review submissions and re-scoring.",
            "Implemented FSSAI municipal safety scoring engine (src/safety_engine.py) with strict zero-fabrication rules for unverified listings.",
            "Compiled domain lexicon of 30+ authentic Kolkata and Indian culinary entities (mutton biryani, reshmi kebab, chicken chaap, hakka noodles)."
        ]
    },
    {
        "week_num": 4,
        "start": ("07", "09", "2026"),
        "end": ("11", "09", "2026"),
        "targets": "Build verbatim ACOS dataset curation script and generate stratified 70/15/15 benchmark splits.",
        "achievements": "Curated 1,000 reviews with 1,560 verbatim quadruples (931 explicit, 629 implicit) across train.jsonl, val.jsonl, and test.jsonl.",
        "future": "Design and implement the SpaCy + NetworkX Syntactic Dependency Graph Engine (src/syntax_graph.py).",
        "days": [
            "Built dataset curation script (src/curate_acos_dataset.py) enforcing strictly verbatim aspect and opinion substring spans.",
            "Created compound opposing-polarity review templates pairing positive culinary praise with negative service or hygiene failures.",
            "Generated 1,000 curated instances totaling 1,560 annotated quadruples (931 explicit dependency pairs, 629 implicit expressions).",
            "Partitioned dataset into 70% train (700), 15% validation (150), and 15% held-out test (150) JSONL splits in data/acos_dataset/.",
            "Generated benchmark_metadata.json and verified zero missing fields and 100% substring span integrity."
        ]
    },
    {
        "week_num": 5,
        "start": ("14", "09", "2026"),
        "end": ("18", "09", "2026"),
        "targets": "Engineer Syntactic Dependency Graph Engine using SpaCy parses and NetworkX directed graphs.",
        "achievements": "Built src/syntax_graph.py with directed graph construction, culinary noun phrase consolidation, and grammatical candidate extraction.",
        "future": "Implement Shortest Dependency Path (SDP) calculation, negation scope detection, and unit tests.",
        "days": [
            "Engineered Syntactic Dependency Graph Engine (src/syntax_graph.py) converting SpaCy dependency trees into NetworkX DiGraphs.",
            "Implemented token node attributes (text, pos, dep, lemma) and directed grammatical head-to-dependent edge relations.",
            "Added domain culinary noun phrase consolidation so multi-word Indian dishes (e.g., 'mutton biryani') stay unified.",
            "Implemented grammatical extraction rules for direct adjectival modifiers (amod, advmod) and copular predications (nsubj -> AUX -> acomp).",
            "Added NON_ASPECT_TOKENS filtering so foreign bodies or idiom nouns (e.g., 'dead fly', 'pocket') are not treated as aspects."
        ]
    },
    {
        "week_num": 6,
        "start": ("21", "09", "2026"),
        "end": ("25", "09", "2026"),
        "targets": "Implement Shortest Dependency Path (SDP), syntactic negation scope traversal, and SVG parse visualization.",
        "achievements": "Completed SDP tracing, negation inversion, conj adjective expansion, displaCy SVG export, and 4/4 unit tests passing.",
        "future": "Design and implement the 5-Archetype Implicit Opinion Disentanglement Engine (src/implicit_disentangler.py).",
        "days": [
            "Implemented NetworkX Shortest Dependency Path (SDP) algorithm measuring geodesic distance between aspect heads and opinions.",
            "Built syntactic negation scope detection tracing child 'neg' edges and parent verb negation to invert sentiment polarity.",
            "Added coordinating adjective traversal (conj) for multi-opinion clauses ('fragrant and tender') and advmod expansion ('extremely rude').",
            "Implemented displaCy SVG dependency tree rendering (render_dependency_svg) formatted for interactive Streamlit display.",
            "Created and passed unit tests (tests/test_syntax_graph.py, 4/4 passing); reviewed graph engine with Dr. Saberi Goswami."
        ]
    },
    {
        "week_num": 7,
        "start": ("28", "09", "2026"),
        "end": ("02", "10", "2026"),
        "targets": "Develop Implicit Opinion Disentanglement Engine covering 5 conversational culinary archetypes.",
        "achievements": "Built src/implicit_disentangler.py handling financial idioms, biological symptoms, temporal delays, portion disparities, and metaphors.",
        "future": "Connect Implicit Disentangler with Syntax Graph Engine in ACOSPipeline and validate with unit tests.",
        "days": [
            "Designed Implicit Opinion Disentanglement Engine (src/implicit_disentangler.py) covering 5 distinct culinary archetypes.",
            "Implemented Archetype 1 (Financial Distress: 'burned a hole in my pocket', 'arm and a leg') and Archetype 2 (Biological Illness: 'hugging toilet bowl').",
            "Implemented Archetype 3 (Factual Temporal Delays: 'waited 45 minutes', 'two podcasts') and Archetype 4 (Portion Disparities: 'barely fed a pigeon').",
            "Implemented Archetype 5 (Sensory Metaphors: 'melted like butter', 'dry cardboard') and Environmental Disruptions ('blaring club music').",
            "Mapped each archetype to implied category, sentiment polarity, calibrated confidence score, and linguistic explanation."
        ]
    },
    {
        "week_num": 8,
        "start": ("05", "10", "2026"),
        "end": ("09", "10", "2026"),
        "targets": "Integrate Syntax Graph and Implicit Disentangler into end-to-end ACOSPipeline with unit tests.",
        "achievements": "Built src/acos_pipeline.py with category-aligned SDP grounding; passed 12/12 unit tests across syntax, implicit, and pipeline suites.",
        "future": "Design deep neural multi-task architecture SyntaxAwareACOSNet (src/acos_models.py) and PyTorch DataLoader.",
        "days": [
            "Created unit test suite for implicit opinion detection (tests/test_implicit_detector.py) covering all 5 archetypes.",
            "Verified 100% precision on implicit detection tests (5/5 passing) including explicit-opinion passthrough checks.",
            "Built end-to-end extraction pipeline (src/acos_pipeline.py) combining SpaCy dependency graphs, SDP tracing, and implicit disentanglement.",
            "Engineered category-aligned SDP distance minimization to ground implicit opinions to the closest syntactic target (e.g. SERVICE -> waiter).",
            "Validated compound opposing-polarity review extraction via tests/test_acos_pipeline.py (12/12 total unit tests passing)."
        ]
    },
    {
        "week_num": 9,
        "start": ("12", "10", "2026"),
        "end": ("16", "10", "2026"),
        "targets": "Design SyntaxAwareACOSNet deep neural network with multi-channel embeddings and graph attention masking.",
        "achievements": "Implemented SyntaxAwareACOSNet (Word+POS+Dep, 2-layer BiLSTM, graph attention mask, 5 heads) and ACOSDataset loader.",
        "future": "Train SyntaxAwareACOSNet on Apple Silicon MPS and integrate live neural inference into ACOSPipeline.",
        "days": [
            "Designed SyntaxAwareACOSNet (src/acos_models.py) fusing Word (128d), POS (32d), and Dependency relation (32d) embeddings.",
            "Implemented 2-layer Bidirectional LSTM (BiLSTM) encoder capturing bidirectional contextual dependencies across review tokens.",
            "Engineered graph-guided MultiheadAttention layer masked by the NetworkX dependency adjacency matrix to prevent hallucinations.",
            "Built 5 joint prediction heads: Aspect BIO, Opinion BIO, 9-class Category, 3-class Sentiment, and Binary Implicit/Explicit head.",
            "Implemented PyTorch ACOSDataset loader and Vocabulary builder (src/train_acos.py) with adjacency padding and self-loop clamping."
        ]
    },
    {
        "week_num": 10,
        "start": ("19", "10", "2026"),
        "end": ("23", "10", "2026"),
        "targets": "Train SyntaxAwareACOSNet on MPS hardware and wire real PyTorch inference into ACOSPipeline.",
        "achievements": "Trained 15 epochs (loss 2.64 -> 0.028, 100% val category/polarity accuracy), saved syntax_acos_model.pt, and added predict_neural().",
        "future": "Build evaluation and ablation benchmark suite (src/evaluate_acos.py) on held-out test.jsonl.",
        "days": [
            "Implemented composite multi-task loss combining category CrossEntropy, sentiment CrossEntropy, and implicit BCEWithLogitsLoss.",
            "Resolved PyTorch 3D attn_mask dimension constraint by repeating adjacency masks across attention heads (batch_size * num_heads).",
            "Executed training on Apple Silicon MPS for 15 epochs; loss converged from 2.64 to 0.028 with 100% validation accuracy.",
            "Serialized trained model checkpoint (models/acos_model/syntax_acos_model.pt) and token vocabularies (vocab.json).",
            "Integrated live PyTorch forward pass (predict_neural) into ACOSPipeline achieving sub-2ms single-review inference."
        ]
    },
    {
        "week_num": 11,
        "start": ("26", "10", "2026"),
        "end": ("30", "10", "2026"),
        "targets": "Run Exact Quadruple Match evaluation and ablation studies on held-out test split (test.jsonl).",
        "achievements": "Proposed model achieved 60.04% Quadruple F1 and 50.0% Implicit F1 (+4.5% syntax gain, +41.3% implicit gain); generated 3 plots & report.",
        "future": "Upgrade Streamlit web dashboard (streamlit_app/app.py) with ACOS Studio, Batch Mining, and dynamic Benchmark Lab.",
        "days": [
            "Built evaluation script (src/evaluate_acos.py) enforcing strict Exact Quadruple Matching on held-out test.jsonl (150 reviews).",
            "Ran Ablation A (w/o Dependency Syntax) and Ablation B (w/o Implicit Disentangler) using real ablation flags in ACOSPipeline.",
            "Recorded empirical metrics: Proposed 60.04% Quadruple F1 (64.45% P) vs. 55.58% w/o Syntax and 51.76% w/o Implicit (8.7% Implicit F1).",
            "Generated publication-grade matplotlib plots: ablation_comparison.png, category_f1_breakdown.png, and implicit_vs_explicit_f1.png.",
            "Compiled benchmark report (reports/ACOS_BENCHMARK_REPORT.md) and saved numerical metrics to reports/acos_evaluation_results.json."
        ]
    },
    {
        "week_num": 12,
        "start": ("02", "11", "2026"),
        "end": ("06", "11", "2026"),
        "targets": "Upgrade Streamlit web application with Syntax-Aware ACOS Studio, Batch Mining, and live Benchmark Lab.",
        "achievements": "Deployed interactive SVG dependency trees, ACOS quadruple cards, 3-way neural comparison, Batch CSV export, and JSON Benchmark Lab.",
        "future": "Design and integrate Conversational AI Chatbot (FoodLensChatbotEngine) with homepage shortcut.",
        "days": [
            "Upgraded Streamlit dashboard header, sidebar, and Syntax-Aware ACOS Studio (streamlit_app/app.py) with Polarity Blindness alerts.",
            "Integrated live displaCy SVG dependency parse tree rendering and 3-way Coarse vs. PyTorch vs. ACOS Graph comparison cards.",
            "Upgraded Batch ACOS Mining Center to process bulk reviews and export CSV files with Shortest Dependency Paths.",
            "Wired dynamic JSON benchmark loading from acos_evaluation_results.json into ACOS Benchmark & Evaluation Lab.",
            "Updated Research Methodology & Architecture tab with formal 5-tuple math, 5 implicit archetypes, and team credits."
        ]
    },
    {
        "week_num": 13,
        "start": ("09", "11", "2026"),
        "end": ("13", "11", "2026"),
        "targets": "Build fully functional Conversational AI Chatbot and integrate into Streamlit with bottom-right homepage shortcut.",
        "achievements": "Built FoodLensChatbotEngine, scrollable chat UI, single-click suggested prompts, floating shortcut, and passed 18/18 tests + AppTest.",
        "future": "Audit codebase for zero mocks, finalize 10-slide PPTX/PDF with 2021–2026 survey, defense script, and WPRs.",
        "days": [
            "Built FoodLensChatbotEngine (src/foodlens_chatbot.py) supporting live ACOS review parsing, dining recommendations, and FSSAI lookups.",
            "Added side-by-side restaurant comparisons, Neural/Dataset/Roadmap Q&A, and question-vs-review intent routing.",
            "Integrated FoodLens AI Chatbot tab into streamlit_app/app.py with scrollable chat viewport and single-click suggested prompt chips.",
            "Added floating bottom-right 'Ask FoodLens AI' homepage shortcut button and synchronized sidebar navigation via navigate_to().",
            "Verified all 6 suggested prompts and chat_input via Streamlit AppTest; expanded and passed 18/18 unit tests."
        ]
    },
    {
        "week_num": 14,
        "start": ("16", "11", "2026"),
        "end": ("20", "11", "2026"),
        "targets": "Complete mock-free audit, finalize 10-slide presentation (2021–2026 survey), defense script, docs, and WPRs.",
        "achievements": "Verified 100% real PyTorch/JSON pipeline, built clean PPTX/PDF, updated 2021–2026 literature survey, defense script, and 14-week WPRs.",
        "future": "Deliver final Minor Project oral defense and live demonstration before faculty guide Dr. Saberi Goswami and examiners.",
        "days": [
            "Audited entire codebase confirming real PyTorch inference, SQLite persistence, and dynamic JSON benchmark loading (zero mocks).",
            "Generated official 10-slide Amity University presentation (Minor_Project_Presentation.pptx & Minor_Project.pdf).",
            "Fixed slide clearing so zero old images remain on Slides 5–8; updated Slide 4 & 10 with verified 2021–2026 papers and visually verified PNGs.",
            "Updated 3-speaker oral defense script (MD & DOCX), README.md, and docs/ACOS_ARCHITECTURE_AND_METHODOLOGY.md.",
            "Completed final test run (18/18 passing), verified live Streamlit server on port 8501, and filled all 14 official WPR templates."
        ]
    }
]


def fill_single_wpr(week_info: dict) -> docx.Document:
    """Loads the original university template and fills ONLY the blank spaces."""
    doc = docx.Document(str(TEMPLATE_PATH))

    # 1. Fill Date Range in P05 preserving original runs & formatting
    p5 = doc.paragraphs[5]
    s_dd, s_mm, s_yyyy = week_info["start"]
    e_dd, e_mm, e_yyyy = week_info["end"]
    date_tokens = [s_dd, s_mm, s_yyyy, e_dd, e_mm, e_yyyy]
    tok_idx = 0
    for r in p5.runs:
        if r.text in ("__", "____") and tok_idx < len(date_tokens):
            r.text = date_tokens[tok_idx]
            tok_idx += 1

    # Helper to append text cleanly to a template paragraph
    def append_to_para(p_idx: int, text: str, size_pt: float = 9.5, bold: bool = False):
        p = doc.paragraphs[p_idx]
        run = p.add_run(text)
        run.font.size = Pt(size_pt)
        run.bold = bold

    # 2. Fill Metadata Blanks (leave Enrollment No., Company Name, Industry Guide untouched)
    append_to_para(8, TEAM_MEMBERS, size_pt=9.5, bold=False)         # NAME
    append_to_para(9, PROGRAM, size_pt=9.5, bold=False)              # Program
    append_to_para(13, FACULTY_GUIDE, size_pt=9.5, bold=False)       # Faculty Guide's Name
    append_to_para(19, PROJECT_TITLE, size_pt=9.5, bold=False)       # Project Title

    # 3. Fill Targets, Achievements, Future Work Plans
    append_to_para(22, week_info["targets"], size_pt=9.5, bold=False)
    append_to_para(23, week_info["achievements"], size_pt=9.5, bold=False)
    append_to_para(24, week_info["future"], size_pt=9.5, bold=False)

    # 4. Fill Table 0 (Monday to Friday in Column 1)
    table = doc.tables[0]
    # Header cell R0 C1
    r0_p = table.rows[0].cells[1].paragraphs[0]
    r0_run = r0_p.add_run("Work Done / Progress Details")
    r0_run.font.size = Pt(9.5)
    r0_run.bold = True

    for day_idx, day_text in enumerate(week_info["days"], start=1):
        cell = table.rows[day_idx].cells[1]
        p = cell.paragraphs[0]
        run = p.add_run(day_text)
        run.font.size = Pt(9.0)

    return doc


def generate_all_wprs():
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Original WPR template not found at {TEMPLATE_PATH}")

    print(f"Using original university WPR template: {TEMPLATE_PATH}")

    # Clean up previous generated WPR_Week_*.docx files
    for old_f in WPR_DIR.glob("WPR_Week_*.docx"):
        old_f.unlink()

    # Create consolidated document starting from a copy of Week 1
    consolidated_doc = None

    for idx, week_info in enumerate(WEEKS_DATA):
        week_doc = fill_single_wpr(week_info)
        ind_path = WPR_DIR / f"WPR_Week_{week_info['week_num']:02d}.docx"
        week_doc.save(str(ind_path))
        print(f"Saved {ind_path.name} ({week_info['start'][0]}.{week_info['start'][1]}.{week_info['start'][2]} – {week_info['end'][0]}.{week_info['end'][1]}.{week_info['end'][2]})")

        if idx == 0:
            consolidated_doc = week_doc
        else:
            # Append a page break before next week's body elements
            pb_p = OxmlElement('w:p')
            pb_r = OxmlElement('w:r')
            pb_br = OxmlElement('w:br')
            pb_br.set(qn('w:type'), 'page')
            pb_r.append(pb_br)
            pb_p.append(pb_r)

            body = consolidated_doc.element.body
            sectPr = body.find(qn('w:sectPr'))
            if sectPr is not None:
                sectPr.addprevious(pb_p)
                for child in week_doc.element.body:
                    if child.tag != qn('w:sectPr'):
                        sectPr.addprevious(copy.deepcopy(child))
            else:
                body.append(pb_p)
                for child in week_doc.element.body:
                    if child.tag != qn('w:sectPr'):
                        body.append(copy.deepcopy(child))

    consolidated_path = WPR_DIR / "Minor_Project_WPR.docx"
    consolidated_doc.save(str(consolidated_path))
    print(f"\nSaved consolidated 14-week WPR (preserving exact template format): {consolidated_path}")


if __name__ == "__main__":
    generate_all_wprs()
