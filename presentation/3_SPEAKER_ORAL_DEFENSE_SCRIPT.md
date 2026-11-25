# 3-Speaker Oral Defense & Live Demonstration Script

## "Beyond Polarity: Syntax-Aware Deep Aspect Quadruple Mining and Implicit Opinion Disentanglement in Online Food Reviews"

**Course**: Minor Project (ETMN100)  
**Department**: Computer Science & Engineering, Amity School of Engineering & Technology  
**Institution**: Amity University, Kolkata  
**Student Investigator**: Tanim Naha (7th Semester B.Tech CSE)  
**Faculty Guide**: Dr. Saberi Goswami, Assistant Professor / Faculty Guide  
**Total Allocated Defense Duration**: 10 to 12 minutes (Presentation + Live Demo + Viva Q&A)  

---

## Master Speaker Assignment Matrix

| Speaker | Assigned Slides & Responsibilities | Core Focus & Delivery Style |
| :--- | :--- | :--- |
| **🎤 SPEAKER 1** | **Slides 1, 2, 3, 4** (Opening, Agenda, Problem Statement, Literature Survey) | Professional, authoritative, sets the academic stage, articulates polarity blindness and implicit opinion failures. |
| **🎤 SPEAKER 2** | **Slides 5, 6** (Proposed Methodology, Syntax Graph Engine, Implicit Disentangler, Multi-Task Architecture) | Deep technical precision, mathematical formulation, graph theory, multi-channel embeddings, multi-task loss. |
| **🎤 SPEAKER 3** | **Slides 7, 8, 9, 10 + Live App Demo + Viva Q&A** (Results, Ablation Analysis, Future Scope, Conclusion, Demo) | Data-driven, confident, leads empirical discussion, operates live Streamlit demonstration, answers examiner queries. |

*(Note: If presenting solo, Tanim Naha seamlessly delivers all 3 speaker parts continuously.)*

---

## SLIDE-BY-SLIDE ORAL DEFENSE TRANSCRIPT

### Slide 1: Title & Academic Cover
**[Action: Display Slide 1 with Amity University branding, research topic title, and guide details.]**

> **[SPEAKER 1 Speaks]**:  
> "Good morning, respected external examiners, esteemed faculty members, and our honorable faculty guide, **Dr. Saberi Goswami**.  
> I am **Tanim Naha**, and today we are proud to present our Minor Project defense titled:  
> **'Beyond Polarity: Syntax-Aware Deep Aspect Quadruple Mining and Implicit Opinion Disentanglement in Online Food Reviews'**.  
> This research represents a decisive departure from traditional, coarse sentiment analysis. Rather than compressing an entire review into a naive positive or negative label, our system mines structured 5-tuple Aspect-Category-Opinion-Sentiment representations using directed dependency graphs, Shortest Dependency Paths, and dedicated implicit opinion disentanglement across Kolkata's dining landscape."

---

### Slide 2: Table of Contents & Defense Agenda
**[Action: Transition to Slide 2 showing the two-part structured agenda.]**

> **[SPEAKER 1 Speaks]**:  
> "Our oral defense today is organized into two primary divisions:  
> **Part I** covers the foundational research motivation, literature survey, formal problem formulation, and our end-to-end technical methodology.  
> **Part II** presents our empirical benchmark results, ablation study proving the isolated gains of dependency syntax and implicit disentanglement, future directions towards our Major Project, followed by an interactive live demonstration of our production Streamlit platform."

---

### Slide 3: Problem Statement & Research Motivation
**[Action: Transition to Slide 3 highlighting the three critical research gaps.]**

> **[SPEAKER 1 Speaks]**:  
> "Let us address the fundamental limitation in existing sentiment analysis systems: **Polarity Blindness**.  
> Consider a common customer review: *'The mutton biryani was fragrant, tender and cooked to perfection, but the waiter completely ignored our table for 45 minutes.'*  
> When passed through conventional sentiment models, positive culinary praise and negative service neglect cancel each other out, resulting in a **Neutral** classification. This polarity blindness misleads consumers and denies restaurant managers actionable insights.  
> Furthermore, current systems suffer from **Implicit Opinion Blindness**. In conversational food reviews, customers rarely restrict themselves to explicit adjectives like 'bad' or 'delicious'. Instead, they express intense sentiment through:
> 1. Cultural financial idioms: *'A single plate burned a massive hole in my pocket'*;
> 2. Factual wait durations: *'We finished two full podcast episodes before our food arrived'*;
> 3. Objective health consequences: *'Spent the entire night hugging the toilet bowl'*.  
> Baseline models miss these completely because no surface sentiment words exist. Our research solves both challenges systematically."

---

### Slide 4: Literature Survey & Technical Research Gaps
**[Action: Transition to Slide 4 showing the comparative literature table.]**

> **[SPEAKER 1 Speaks]**:  
> "Looking at the most recent academic literature from 2021 to 2026 directly tied to our topic:  
> In 2021, **Cai, Xia, and Yu (ACL 2021)** formally introduced ACOS quadruple extraction with implicit aspects and opinions, followed by **Peper & Wang (EMNLP Findings 2022)** (`GEN-SCL-NAT`) applying supervised contrastive learning to separate implicit and explicit quadruples—yet unconstrained generative models remained syntax-agnostic and prone to span hallucinations.  
> In 2024, **Cui et al. (EMNLP Findings 2024)** introduced hierarchical disentanglement for implicit sentiment, while **Ouyang et al. (AAAI 2024)** (`ABSA-ESA`) applied T5 explicit sentiment augmentation with syntax-distance weighting.  
> Most recently in 2025–2026, **Fan et al. (COLING 2025)** (`Syn-Chain`) and **Esfandyari et al. (2026)** (`DRIFT`) integrated syntax-opinion reasoning chains and dependency trees into LLMs, which still suffer from heavy inference latency for real-time consumer portals.  
> Our proposed framework directly bridges these gaps by combining **directed NetworkX Shortest Dependency Paths**, a **5-archetype Implicit Disentangler**, and **sub-2ms PyTorch inference** in a live Streamlit application and AI chatbot.  
> I now hand over to **Speaker 2** to walk through our technical methodology."

---

### Slide 5: Proposed Methodology & Architecture
**[Action: Speaker 2 takes the floor. Display Slide 5 showing the 4-stage architectural quadrants.]**

> **[SPEAKER 2 Speaks]**:  
> "Thank you, Speaker 1.  
> To operationalize our framework, we formulated the task as extracting structured 5-tuples:  
> $$\mathcal{Q} = \langle a, c, o, s, 	au angle$$  
> where $a$ is the aspect span, $c$ is one of 9 culinary categories, $o$ is the opinion span, $s$ is sentiment polarity, and $	au$ denotes explicit versus implicit typology.  
> Our architecture proceeds through four synchronized stages:  
> 1. **Syntactic Dependency Graph Engine**: We parse incoming review sentences using SpaCy and construct directed NetworkX graphs where tokens are nodes and grammatical relations are directed edges. We enforce domain entity consolidation so compound culinary terms like *'mutton biryani'* or *'reshmi kebab'* are extracted as complete aspect spans rather than fragmented tokens.  
> 2. **Shortest Dependency Path (SDP) Tracing**: Rather than relying on arbitrary linear distance, we calculate the shortest path in the undirected dependency graph between aspect candidates and opinion modifiers. This allows the model to correctly resolve predicate copular relations like *nsubj -> AUX -> acomp* and trace syntactic negation scopes (`neg` child relations) that invert polarity.  
> 3. **Implicit Opinion Disentanglement**: For sentences lacking explicit adjectives, our engine activates 5 archetypal inference modules: Metaphorical Financial Distress, Biological Illness Symptoms, Factual Temporal Delays, Portion Disparities, and Sensory Texture Metaphors.  
> 4. **Deep Multi-Task Neural Network (`SyntaxAwareACOSNet`)**: Our neural network combines multi-channel token embeddings (Word + POS + Dependency tags), a 2-layer Bidirectional LSTM contextualizer, a syntax graph attention mask that restricts self-attention strictly along valid dependency edges, and 5 multi-task prediction heads."

---

### Slide 6: Experimental Setup & Dataset Curation
**[Action: Transition to Slide 6 detailing benchmark splits and loss functions.]**

> **[SPEAKER 2 Speaks]**:  
> "To train and benchmark this framework without data leakage or synthetic hallucinations, we curated a strictly verbatim 1,000-instance ACOS dataset.  
> Every aspect span and opinion span in our dataset is an exact verbatim substring present in the text.  
> We partitioned the corpus into **70% train (700 samples), 15% validation (150 samples), and 15% held-out test (150 samples)**, encompassing 1,560 total quadruples across 9 culinary dimensions:  
> *FOOD#QUALITY, FOOD#PRICES, FOOD#STYLE_OPTIONS, SERVICE#GENERAL, SERVICE#PROMPTNESS, AMBIENCE#GENERAL, RESTAURANT#PRICES, HYGIENE#CLEANLINESS, and HYGIENE#FOOD_SAFETY*.  
> We trained the network on Apple Silicon Metal Performance Shaders (MPS) using our composite multi-task loss:  
> $$\mathcal{L}_{	ext{total}} = \mathcal{L}_{	ext{aspect}} + \mathcal{L}_{	ext{opinion}} + \mathcal{L}_{	ext{category}} + \mathcal{L}_{	ext{sentiment}} + \mathcal{L}_{	ext{implicit}}$$  
> Across 15 epochs, the training loss smoothly converged from 2.64 to 0.028, achieving 100% category and polarity accuracy on the validation split.  
> I now invite **Speaker 3** to present our empirical benchmark findings and demonstrate our live platform."

---

### Slide 7: Empirical Benchmark Results & Ablation Analysis
**[Action: Speaker 3 takes the floor. Display Slide 7 displaying the comparative ablation table.]**

> **[SPEAKER 3 Speaks]**:  
> "Thank you, Speaker 2. Respected examiners, let us examine our empirical benchmark results evaluated strictly on the 150 held-out test reviews.  
> In our evaluation, we enforced **Exact Quadruple Matching**: a prediction is considered a true positive only if the aspect target, culinary category, opinion expression, and sentiment polarity all match ground truth simultaneously.  
> Under this rigorous standard:  
> - Our **Proposed Full Model** achieved **60.04% Quadruple F1**, with **64.45% Precision**, **63.66% Explicit F1**, and **50.00% Implicit F1**.  
> - In **Ablation A**, where we removed the dependency graph and substituted naive window co-occurrence, Quadruple F1 dropped to **55.58%**, and Precision plummeted by nearly 10% to **54.58%**. This empirically proves that directed dependency syntax and Shortest Dependency Paths provide a **+4.5% absolute F1 gain** by eliminating false span associations.  
> - In **Ablation B**, where we disabled the Implicit Disentanglement Engine, Implicit F1 collapsed from **50.00% to just 8.70%**, causing overall Quadruple F1 to drop to **51.76%**. This confirms an extraordinary **+41.3% absolute gain on implicit opinion recovery**, demonstrating that our disentanglement engine successfully captures implicit customer sentiment that baseline models miss entirely."

---

### Slide 8: Future Direction Towards Major Project
**[Action: Transition to Slide 8 showing the 4 expansion quadrants.]**

> **[SPEAKER 3 Speaks]**:  
> "This Minor Project provides an airtight technical springboard for our 8th Semester Major Project.  
> We have mapped out four concrete technical extensions:  
> 1. **Graph Neural Networks (GCNs & GATs)**: Upgrading our attention layer to full relational Graph Convolutional Networks that perform multi-hop message passing directly over dependency tree nodes and edge labels.  
> 2. **Multilingual & Code-Mixed Bengali NLP**: Fine-tuning IndicBERT and BanglaBERT on code-mixed Romanized Bengali ('Banglish') reviews to parse regional Kolkata colloquialisms like *'besh bhalo'* or *'khub baje service'*.  
> 3. **Domain-Specific LLM Distillation**: Distilling large instruction-tuned models like Llama-3-8B into compact, sub-15ms student networks for on-device mobile inference.  
> 4. **Direct Civic Health Alert Integration**: Routing high-confidence *HYGIENE#FOOD_SAFETY* quadruples directly to municipal health desks at KMC and FSSAI for inspection prioritization."

---

### Slide 9: Conclusion
**[Action: Transition to Slide 9 summarizing core milestones.]**

> **[SPEAKER 3 Speaks]**:  
> "In conclusion, this project delivers three significant academic and practical breakthroughs:  
> First, it **completely resolves polarity blindness** in restaurant reviews by extracting structured 5-tuples.  
> Second, it **grounds aspect-opinion associations in syntactic dependency trees**, improving extraction precision by +9.9%.  
> Third, it **pioneers implicit opinion disentanglement in Indian culinary contexts**, boosting implicit F1 by +41.3%.  
> With our model weights trained and our benchmark report published, let us now switch to our live interactive demonstration."

---

## LIVE SYSTEM DEMONSTRATION SCRIPT (2–3 Minutes)
**[Action: Speaker 3 transitions screen share to the running Streamlit web application: `http://localhost:8501`.]**

> **[SPEAKER 3 Speaks during Demo]**:  
> "We are now looking at our live production platform, **ACOS FoodLens**, deployed via Streamlit.  
> Let us navigate to the **'Syntax-Aware ACOS Studio'** tab.  
> Notice our preset benchmark reviews. Let us select the first complex compound review:  
> *'The mutton biryani was fragrant, tender and cooked to perfection, but the waiter completely ignored our table for 45 minutes.'*  
> When we run AI inference:  
> Look at the **Polarity Blindness Warning**: The system immediately detects that positive culinary praise and negative service neglect coexist.  
> Below, observe the two mined ACOS quadruples:  
> 1. Aspect: *'mutton biryani'*, Category: *FOOD#QUALITY*, Opinion: *'fragrant, tender and cooked to perfection'*, Polarity: *Positive*, Typology: *Explicit*.  
> 2. Aspect: *'waiter'*, Category: *SERVICE#PROMPTNESS*, Opinion: *'completely ignored our table for 45 minutes'*, Polarity: *Negative*, Typology: *Implicit (temporal wait delay)*.  
> Now look below at the **live SVG Dependency Parse Tree rendered in real time**:  
> You can trace the exact grammatical arcs: *biryani* connects as *nsubj* to *cooked*, while *waiter* connects as *nsubj* to *ignored*.  
> Next, let us test an implicit biological symptom review:  
> *'Both of us spent the entire night hugging the toilet bowl after eating the seafood platter.'*  
> Notice that without a single explicit sentiment word, our engine correctly identifies the biological illness archetype, maps it to *HYGIENE#FOOD_SAFETY*, and uses Shortest Dependency Path minimization to ground the illness to the syntactic direct object: *'seafood platter'*.  
> Finally, in the **Batch ACOS Mining Center**, users can upload hundreds of reviews and export a full CSV with complete syntactic provenance.  
> And notice the floating **'Ask FoodLens AI'** shortcut button in the bottom-right corner of the homepage: clicking it opens our **Conversational AI Chatbot**, where users can paste reviews for instant quadruple parsing, ask for Kolkata dining recommendations, inspect FSSAI safety records, or query our academic methodology.  
> This completes our presentation and demonstration. We are now open for viva defense questions. Thank you!"

---

## COMPREHENSIVE VIVA DEFENSE Q&A PREPARATION

### Q1: Why did you transition from standard Aspect-Based Sentiment Analysis (ABSA) to Aspect-Category-Opinion-Sentiment (ACOS) Quadruple Mining?
**Answer**:  
"Standard ABSA, as formalized in SemEval 2014-2016, typically extracts either aspect-sentiment pairs or aspect-category pairs in isolation. However, in real-world reviews, stakeholders need to know *why* a customer felt that way (the opinion span) and whether that opinion was stated explicitly or implied figuratively. ACOS 5-tuple mining $\langle a, c, o, s, 	au angle$ provides the complete semantic provenance, eliminating polarity blindness where opposing aspect sentiments within the same review cancel each other out."

### Q2: How does your Shortest Dependency Path (SDP) algorithm improve extraction precision over traditional window-based models?
**Answer**:  
"Flat-window models assume that words closer in linear sentence position are semantically related. However, in complex compound sentences, long-distance modifiers frequently occur. For example, in *'The biryani served yesterday at our wedding anniversary was tender'*, the adjective *'tender'* is 8 tokens away from *'biryani'*, but their syntactic dependency distance in our NetworkX graph is only 2 (*biryani[nsubj] -> was -> tender[acomp]*). Tracing the Shortest Dependency Path prevents the model from mistakenly binding *'tender'* to *'wedding anniversary'*, yielding a +9.9% precision improvement in our benchmark."

### Q3: How does the system detect implicit opinions when there are zero sentiment adjectives in the sentence?
**Answer**:  
"Our Implicit Opinion Disentanglement Engine operates on semantic and syntactic archetype patterns. When an explicit adjectival head is absent, the engine evaluates 5 specific archetypes:
1. Idiomatic financial loss patterns (e.g., *'burned a hole in my pocket'*, *'arm and a leg'*);
2. Objective temporal duration expressions (e.g., *'waited 45 minutes'*, *'finished two podcasts'*);
3. Biological illness symptoms (e.g., *'hugging the toilet bowl'*, *'vomiting'*);
4. Portion disparities (e.g., *'barely fed a pigeon'*);
5. Sensory texture metaphors (e.g., *'melted like butter'*).  
Each archetype maps directly to an implied category and sentiment with calibrated confidence scores."

### Q4: What is the purpose of the adjacency matrix mask in your neural network's self-attention layer?
**Answer**:  
"Standard Transformer multi-head self-attention allows all tokens to attend to all other tokens ($O(N^2)$ connectivity). While powerful, in fine-grained quadruple extraction, unconstrained self-attention often hallucinates non-existent relations between unrelated clauses. In `SyntaxAwareACOSNet`, our attention mask incorporates the adjacency matrix of the syntactic dependency tree, ensuring that attention weights are prioritized along true grammatical dependency arcs."

### Q5: What were the key numerical findings of your ablation study?
**Answer**:  
"On our held-out test split of 150 reviews (502 quadruples):
- The Full Proposed Model achieved **60.04% Quadruple F1**, **64.45% Precision**, and **50.00% Implicit F1**.
- Disabling dependency syntax (Ablation A) caused Quadruple F1 to fall to **55.58%** and Precision to drop to **54.58%**, proving an isolated **+4.5% F1 syntax gain**.
- Disabling the implicit disentangler (Ablation B) caused Implicit F1 to plummet from **50.00% to 8.70%**, proving an isolated **+41.3% F1 implicit opinion gain**."

### Q6: How does your engine handle domain culinary terms that SpaCy normally fragments?
**Answer**:  
"Standard English SpaCy models often split multi-word Indian and regional dishes—for example, treating *'mutton'* and *'biryani'* as separate tokens or treating *'chaap'* as an unknown noun. In `src/syntax_graph.py`, we implemented a specialized domain entity consolidation module that maintains a comprehensive lexicon of over 30 authentic Indian and Kolkata dishes. When a noun chunk is parsed, adjacent culinary nouns are merged into a unified aspect target span."

### Q7: Why did you evaluate exact quadruple match rather than loose sentiment accuracy?
**Answer**:  
"Evaluating loose sentiment accuracy is misleading because predicting a single positive or negative label on a compound review ignores whether the model identified the correct dish, correct service staff, or correct category. Exact Quadruple Matching requires all components $\langle a, c, o, s angle$ to be correctly extracted simultaneously, which is the gold standard established in international NLP literature by Cai et al. (ACL 2021)."

### Q8: What is your technical plan for expanding this research into your 8th Semester Major Project?
**Answer**:  
"For our Major Project, we plan three major technical extensions:
1. Replace the attention mask with full Graph Convolutional Networks (GCN) and Graph Attention Networks (GAT) to model multi-hop relational dependencies.
2. Extend the pipeline to code-mixed Romanized Bengali ('Banglish') by fine-tuning multilingual models like IndicBERT on Kolkata culinary social media reviews.
3. Integrate knowledge distillation from Large Language Models (Llama-3/Mistral) to extract quadruples in zero-shot settings."
