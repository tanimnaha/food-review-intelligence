# Architecture, Methodology, and Technical Specification
## "Beyond Polarity: Syntax-Aware Deep Aspect Quadruple Mining and Implicit Opinion Disentanglement in Online Food Reviews"

**Author**: Tanim Naha  
**Faculty Guide**: Dr. Saberi Goswami, Faculty Guide  
**Department**: Computer Science & Engineering, Amity School of Engineering & Technology  
**Institution**: Amity University, Kolkata  
**Academic Year**: 2026–2027 (7th Semester Minor Project, Course Code: ETMN100)  

---

## 1. Executive Summary & Research Motivation

### 1.1 The Polarity Blindness Bottleneck
Traditional natural language processing (NLP) pipelines for customer feedback rely on coarse sentiment classification: mapping an entire document or sentence into a scalar value (Positive, Neutral, or Negative). When applied to conversational dining reviews, this creates **Polarity Blindness**:
$$\text{Sentence: } \text{"The mutton biryani was fragrant and tender, but the waiter was extremely rude."}$$
$$\text{Conventional Classifier} \longrightarrow \text{Neutral (Confidence: 45.2\%) } \quad \text{[FAIL]}$$

In this example, culinary praise ($+1$) and service hostility ($-1$) cancel each other out. This produces two critical real-world failures:
1. **Consumer Misguidance**: Diners looking for exceptional culinary quality are discouraged by mediocre composite ratings.
2. **Managerial Inaction**: Restaurant operators cannot determine which operational department (kitchen vs. front-of-house staff) requires remediation.

### 1.2 The Implicit Opinion Disentanglement Gap
In conversational culinary reviews, customers frequently communicate strong sentiment without using conventional explicit adjectives (e.g., *delicious*, *terrible*, *bad*). Instead, they employ:
- **Cultural Financial Metaphors**: *"A single plate of prawn malai curry burned a massive hole in my pocket."*
- **Factual Temporal Delays**: *"We finished two full podcast episodes before our food arrived."*
- **Biological Illness Consequences**: *"Both of us spent the entire night hugging the toilet bowl."*
- **Portion Disparities**: *"Barely fed a pigeon for that steep price."*

Existing Aspect-Based Sentiment Analysis (ABSA) systems ignore these implicit opinions because their token taggers look solely for explicit adjectival modifiers.

---

## 2. Formal Problem Formulation

We formalize the problem as extracting structured 5-tuple representations:
$$\mathcal{Q} = \langle a, c, o, s, \tau \rangle$$

where:
- **$a \in \mathcal{A}$ (Aspect Span)**: The explicit noun phrase target or implicit dining entity (e.g., `mutton biryani`, `server`, `washroom`, `pricing`).
- **$c \in \mathcal{C}$ (Culinary Category)**: One of 9 structured culinary dimensions:
  $$\mathcal{C} = \{\text{FOOD\#QUALITY}, \text{FOOD\#PRICES}, \text{FOOD\#STYLE\_OPTIONS}, \text{SERVICE\#GENERAL},$$
  $$\text{SERVICE\#PROMPTNESS}, \text{AMBIENCE\#GENERAL}, \text{RESTAURANT\#PRICES}, \text{HYGIENE\#CLEANLINESS}, \text{HYGIENE\#FOOD\_SAFETY}\}$$
- **$o \in \mathcal{O}$ (Opinion Expression Span)**: The verbatim text phrase conveying the evaluative sentiment (e.g., `fragrant and tender`, `completely ignored our table for 45 minutes`).
- **$s \in \mathcal{S}$ (Sentiment Polarity)**: The polarity sign $s \in \{\text{positive}, \text{neutral}, \text{negative}\}$.
- **$\tau \in \mathcal{T}$ (Typology)**: The semantic opinion mechanism $\tau \in \{\text{explicit}, \text{implicit}\}$.

---

## 3. System Architecture & Pipeline Workflow

```
                        ┌──────────────────────────────────────────────┐
                        │          Raw Customer Review Text            │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │      SpaCy Syntactic Dependency Parser       │
                        └──────────────────────┬───────────────────────┘
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       │                                               │
                       ▼                                               ▼
       ┌───────────────────────────────┐               ┌───────────────────────────────┐
       │   NetworkX Directed Graph     │               │ Implicit Opinion Disentangler │
       │   - Directed Head->Dep Edges  │               │ - 5 Culinary Archetypes       │
       │   - Shortest Dependency Path  │               │ - Metaphor/Fact Delays        │
       │   - Domain Entity Consolidation│              │ - Biological Symptoms         │
       └───────────────┬───────────────┘               └───────────────┬───────────────┘
                       │                                               │
                       └───────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │       SyntaxAwareACOSNet Multi-Task Net       │
                        │       - Word + POS + Dep Embeddings          │
                        │       - 2-Layer Bidirectional LSTM           │
                        │       - Graph-Guided Self-Attention Mask     │
                        │       - 5 Prediction Heads (BIO, Cat, Pol)   │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │    Mined ACOS Quadruples <a, c, o, s, tau>   │
                        │    + Live DisplaCy SVG Tree Visualization    │
                        └──────────────────────────────────────────────┘
```

---

## 4. Algorithmic Modules

### 4.1 Syntactic Dependency Graph Engine (`src/syntax_graph.py`)
1. **NetworkX Graph Construction**: Converts SpaCy dependency parse trees into a directed graph $G = (V, E)$, where $V$ are token indices with attributes $\{text, pos, dep, lemma\}$, and directed edges $E = \{(v_{\text{head}}, v_{\text{dep}}, rel)\}$.
2. **Domain-Aware Culinary Noun Phrase Consolidation**: Merges multi-token regional Indian and Kolkata culinary terms (e.g., `mutton biryani`, `reshmi kebab`, `fish fry`, `chicken chaap`) into unified aspect target spans, preventing fragmentation.
3. **Shortest Dependency Path (SDP)**: Calculates geodesic distance $d_G(v_a, v_o)$ in the undirected graph:
   $$\text{SDP}(v_a, v_o) = \arg\min_{p \in \mathcal{P}(v_a, v_o)} |p|$$
   This eliminates false associations from linear word proximity windows.
4. **Syntactic Negation Scope Traversal**: Traces child `neg` edges and copular head relations to accurately invert sentiment polarity (e.g., *not greasy* $\rightarrow$ positive, *not fresh* $\rightarrow$ negative).

### 4.2 Implicit Opinion Disentanglement Engine (`src/implicit_disentangler.py`)
Formalizes 5 distinct culinary archetypes:
1. **Metaphorical Financial Distress**: Detects idiomatic phrases (*burned a hole in my pocket*, *cost an arm and a leg*) and maps them to `FOOD#PRICES` or `RESTAURANT#PRICES` with negative polarity.
2. **Biological & Sanitary Illness Symptoms**: Detects acute health signals (*hugging the toilet bowl*, *acute food poisoning*, *cockroach scurrying*, *dead fly floating*) and maps them to `HYGIENE#FOOD_SAFETY`.
3. **Factual Temporal Delays**: Quantifies order/billing wait durations (*waited 45 minutes*, *finished two podcasts before food arrived*) and maps them to `SERVICE#PROMPTNESS`.
4. **Portion Size Disparities**: Extracts portion vs. price disparities (*contained only one tiny potato*, *barely fed a pigeon*) and maps them to `FOOD#PRICES`.
5. **Sensory & Texture Metaphors**: Extracts metaphorical eating experiences (*melted like butter*, *chewing on dry cardboard*, *tasted like pure leather*) and maps them to `FOOD#QUALITY`.

### 4.3 Deep Multi-Task Neural Network (`src/acos_models.py`)
- **Multi-Channel Embeddings**:
  $$\mathbf{x}_i = [\mathbf{e}_{\text{word}}(w_i) \,\|\, \mathbf{e}_{\text{pos}}(p_i) \,\|\, \mathbf{e}_{\text{dep}}(d_i)] \in \mathbb{R}^{d_{\text{word}} + d_{\text{pos}} + d_{\text{dep}}}$$
- **Bidirectional LSTM Contextualizer**:
  $$\mathbf{h}_i = [\overrightarrow{\text{LSTM}}(\mathbf{x}_{1:i}) \,\|\, \overleftarrow{\text{LSTM}}(\mathbf{x}_{i:N})] \in \mathbb{R}^{d_h}$$
- **Graph-Guided Syntactic Self-Attention**:
  Multi-head attention constrained by the adjacency matrix $\mathbf{A} \in \mathbb{R}^{N \times N}$ of the dependency graph:
  $$\mathbf{M}_{ij} = \begin{cases} 0 & \text{if } \mathbf{A}_{ij} = 1 \text{ or } i = j \\ -\infty & \text{otherwise} \end{cases}$$
  $$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}} + \mathbf{M}\right)\mathbf{V}$$
- **Composite Multi-Task Loss**:
  $$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{aspect\_BIO}} + \mathcal{L}_{\text{opinion\_BIO}} + \mathcal{L}_{\text{category}} + \mathcal{L}_{\text{sentiment}} + \mathcal{L}_{\text{implicit}}$$

---

## 5. Experimental Benchmark & Ablation Results

Evaluated on the held-out benchmark split (`data/acos_dataset/test.jsonl`, 150 instances, 502 total quadruples across 9 culinary dimensions):

| Architecture / Configuration | Quad Precision | Quad Recall | **Quadruple F1** | Explicit F1 | **Implicit F1** | Aspect Match |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Proposed (Syntax Graph + Disentangler)** | **64.45%** | **56.20%** | **60.04%** | **63.66%** | **50.00%** | **155.79%** |
| **Ablation A: w/o Dependency Syntax (Window)** | 54.58% | 56.61% | 55.58% | 60.70% | 40.32% | 132.67% |
| **Ablation B: w/o Implicit Disentangler** | 60.11% | 45.45% | 51.76% | 63.66% | 8.70% | 142.15% |

### Key Empirical Takeaways:
1. **Syntactic Dependency Value (+4.5% F1)**: Incorporating directed NetworkX dependency trees boosts Precision from 54.58% to 64.45% (+9.87% gain) by eliminating false linear co-occurrences.
2. **Implicit Disentanglement Value (+41.3% F1)**: Disentangling figurative idioms and delay facts boosts implicit F1 from 8.70% to 50.00%, solving a critical failure mode of conventional ABSA models.

---

## 6. Generated Artifacts & Reproducibility

- **Model Checkpoint**: `models/acos_model/syntax_acos_model.pt`
- **Vocabulary Mapping**: `models/acos_model/vocab.json`
- **Dataset Splits**: `data/acos_dataset/train.jsonl`, `val.jsonl`, `test.jsonl`
- **Benchmark Visualizations**:
  - `reports/ablation_comparison.png`
  - `reports/category_f1_breakdown.png`
  - `reports/implicit_vs_explicit_f1.png`
- **Benchmark Report**: `reports/ACOS_BENCHMARK_REPORT.md`
- **Presentation Deck**: `presentation/Minor_Project_Presentation.pptx` & `presentation/Minor_Project.pdf`
- **Oral Defense Script**: `presentation/3_SPEAKER_ORAL_DEFENSE_SCRIPT.md` & `presentation/3_SPEAKER_ORAL_DEFENSE_SCRIPT.docx`
- **14-Week WPRs (17.08.2026 – 20.11.2026)**: `wpr/Minor_Project_WPR.docx` (consolidated) & `wpr/WPR_Week_01.docx` ... `WPR_Week_14.docx`
