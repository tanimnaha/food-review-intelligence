"""End-to-End Syntax-Aware Aspect-Category-Opinion-Sentiment (ACOS)
Quadruple Mining and Implicit Opinion Disentanglement Pipeline.

Executes:
1. Sentence Segmentation & Syntactic Dependency Parsing (SpaCy + NetworkX)
2. Aspect Candidate Mining & Shortest Dependency Path (SDP) Tracing
3. Implicit Opinion Disentanglement & Syntactically-Grounded Aspect Attribution
4. Deep Category & Sentiment Classification
5. Formats structured ACOS Quadruples (a, c, o, s, tau)
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import networkx as nx
import numpy as np
import torch
import torch.nn.functional as F

from src.syntax_graph import SyntaxGraphEngine, NON_ASPECT_TOKENS, CULINARY_TERMS
from src.implicit_disentangler import ImplicitOpinionDisentangler
from src.acos_models import CATEGORIES, POLARITIES, SyntaxAwareACOSNet, Vocabulary

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models" / "acos_model"

POS_WORDS = {
    "good", "great", "delicious", "tasty", "fresh", "tender", "crispy", "juicy",
    "polite", "courteous", "attentive", "friendly", "clean", "spotless", "cozy",
    "cheap", "reasonable", "fragrant", "aromatic", "flavorful", "flavourful",
    "heavenly", "delectable", "succulent", "prompt", "fast", "generous",
    "authentic", "wonderful", "amazing", "superb", "excellent", "fluffy", "soft"
}

NEG_WORDS = {
    "bad", "bland", "cold", "stale", "salty", "oily", "overcooked", "dry",
    "rubbery", "rude", "slow", "dirty", "filthy", "arrogant", "expensive",
    "costly", "pricey", "overpriced", "astronomical", "exorbitant", "steep",
    "undercooked", "sour", "bitter", "rancid", "foul", "terrible", "horrible",
    "biohazard", "delayed", "greasy", "noisy", "loud", "cramped", "dated", "ignored"
}


class ACOSPipeline:
    def __init__(self, model_path: Optional[Path] = None):
        self.syntax_engine = SyntaxGraphEngine()
        self.disentangler = ImplicitOpinionDisentangler()
        self.model_path = model_path or (MODELS_DIR / "syntax_acos_model.pt")
        self.vocab_path = self.model_path.parent / "vocab.json"
        self.categories = CATEGORIES
        self.polarities = POLARITIES
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.vocab: Optional[Vocabulary] = None
        self.neural_model: Optional[SyntaxAwareACOSNet] = None
        self._load_neural_model()

    def _load_neural_model(self) -> None:
        """Loads trained PyTorch SyntaxAwareACOSNet weights and vocabulary if available."""
        if self.model_path.exists() and self.vocab_path.exists():
            with open(self.vocab_path, "r", encoding="utf-8") as f:
                v_data = json.load(f)
            vocab = Vocabulary()
            vocab.word2idx = v_data["word2idx"]
            vocab.pos2idx = v_data["pos2idx"]
            vocab.dep2idx = v_data["dep2idx"]
            self.vocab = vocab

            model = SyntaxAwareACOSNet(vocab_size=len(vocab.word2idx))
            state_dict = torch.load(self.model_path, map_location=self.device, weights_only=True)
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()
            self.neural_model = model

    def predict_neural(self, text: str, max_len: int = 40) -> Optional[Dict[str, Any]]:
        """Runs real PyTorch forward inference using trained SyntaxAwareACOSNet."""
        if self.neural_model is None or self.vocab is None or not text.strip():
            return None

        doc = self.syntax_engine.parse(text)
        tokens = [t.text for t in doc[:max_len]]
        pos_tags = [t.pos_ for t in doc[:max_len]]
        dep_tags = [t.dep_ for t in doc[:max_len]]
        if not tokens:
            return None

        g = self.syntax_engine.build_dependency_graph(doc[:max_len])
        adj = nx.to_numpy_array(g.to_undirected(), nodelist=range(len(tokens)))
        np.fill_diagonal(adj, 1.0)

        pad_len = max_len - len(tokens)
        w_ids = self.vocab.encode_words(tokens) + [0] * pad_len
        p_ids = self.vocab.encode_pos(pos_tags) + [0] * pad_len
        d_ids = self.vocab.encode_deps(dep_tags) + [0] * pad_len
        padded_adj = np.zeros((max_len, max_len), dtype=np.float32)
        padded_adj[:len(tokens), :len(tokens)] = adj

        w_t = torch.tensor([w_ids], dtype=torch.long, device=self.device)
        p_t = torch.tensor([p_ids], dtype=torch.long, device=self.device)
        d_t = torch.tensor([d_ids], dtype=torch.long, device=self.device)
        a_t = torch.from_numpy(padded_adj).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.neural_model(w_t, p_t, d_t, a_t)
            cat_probs = F.softmax(outputs["category_logits"], dim=-1)[0]
            pol_probs = F.softmax(outputs["sentiment_logits"], dim=-1)[0]
            imp_prob = torch.sigmoid(outputs["implicit_logits"][0]).item()

            cat_idx = int(torch.argmax(cat_probs).item())
            pol_idx = int(torch.argmax(pol_probs).item())

        return {
            "neural_category": self.categories[cat_idx],
            "neural_category_conf": round(float(cat_probs[cat_idx].item()), 4),
            "neural_sentiment": self.polarities[pol_idx],
            "neural_sentiment_conf": round(float(pol_probs[pol_idx].item()), 4),
            "neural_implicit_prob": round(float(imp_prob), 4),
        }

    def extract_quadruples(
        self, text: str, use_syntax: bool = True, use_implicit: bool = True
    ) -> List[Dict[str, Any]]:
        """Processes raw review text and returns structured ACOS quadruples.
        
        Args:
            text: Raw restaurant customer review.
            use_syntax: If True, uses dependency graph and Shortest Dependency Paths (SDP).
                        If False, falls back to naive surface window proximity (Ablation).
            use_implicit: If True, utilizes implicit opinion disentanglement engine.
                          If False, extracts only surface explicit terms (Ablation).
        """
        if not text or not text.strip():
            return []

        doc = self.syntax_engine.parse(text)
        quadruples = []

        if use_syntax:
            graph = self.syntax_engine.build_dependency_graph(doc)
            candidates = self.syntax_engine.extract_syntactic_aspect_opinion_candidates(text)
        else:
            graph = None
            # Ablation: Surface window co-occurrence without syntactic tree
            candidates = []
            noun_chunks = [nc for nc in doc.noun_chunks if nc.text.lower() not in {"i", "we", "you", "they", "it"}]
            for nc in noun_chunks:
                for token in doc:
                    if token.pos_ in {"ADJ"} and abs(token.i - nc.root.i) <= 3:
                        candidates.append({
                            "aspect_text": nc.text,
                            "aspect_root_idx": nc.root.i,
                            "opinion_text": token.text,
                            "opinion_idx": token.i,
                            "syntactic_relation": "window_cooccurrence",
                            "is_negated": False,
                            "sdp": f"{nc.text} --[window]-- {token.text}",
                            "sdp_distance": abs(token.i - nc.root.i)
                        })

        # 1. Process explicit candidates
        for cand in candidates:
            aspect_term = cand["aspect_text"]
            opinion_term = cand["opinion_text"]
            if aspect_term.lower() in NON_ASPECT_TOKENS or opinion_term.lower() in NON_ASPECT_TOKENS:
                continue

            is_negated = cand.get("is_negated", False)
            sdp_str = cand.get("sdp", "none")

            # Map category based on aspect semantics
            cat = "FOOD#QUALITY"
            a_lower = aspect_term.lower()
            if any(k in a_lower for k in ["waiter", "staff", "service", "captain", "server", "manager", "hostess"]):
                cat = "SERVICE#GENERAL"
            elif any(k in a_lower for k in ["clean", "washroom", "cutlery", "hygiene", "table", "plates", "counter", "restroom"]):
                cat = "HYGIENE#CLEANLINESS"
            elif any(k in a_lower for k in ["ambience", "decor", "music", "lighting", "seating", "vibe", "conditioning"]):
                cat = "AMBIENCE#GENERAL"
            elif any(k in a_lower for k in ["price", "cost", "bill", "money", "rate", "charge", "portion"]):
                cat = "FOOD#PRICES" if "portion" in a_lower else "RESTAURANT#PRICES"

            # Check explicit sentiment polarity
            pol = "neutral"
            o_tokens = set(opinion_term.lower().split())
            if any(w in o_tokens or w in opinion_term.lower() for w in NEG_WORDS):
                pol = "negative"
            elif any(w in o_tokens or w in opinion_term.lower() for w in POS_WORDS):
                pol = "positive"

            if is_negated:
                pol = "negative" if pol == "positive" else "positive"

            # Suppress non-evaluative neutral pairs unless clear sentiment
            if pol == "neutral":
                continue

            quadruples.append({
                "aspect": aspect_term,
                "category": cat,
                "opinion": opinion_term,
                "sentiment": pol,
                "type": "explicit",
                "archetype": "syntactic_dependency_pair" if use_syntax else "window_pair",
                "syntactic_path": sdp_str,
                "confidence": 0.92,
                "explanation": f"Extracted via {sdp_str} (syntactic relation: {cand['syntactic_relation']})."
            })

        # 2. Extract implicit opinions (if enabled)
        if use_implicit:
            for sent in doc.sents:
                s_text = sent.text.strip()
                implicit_eval = self.disentangler.classify_opinion(s_text)
                
                if implicit_eval["opinion_type"] == "implicit":
                    aspect_target = "dining experience"
                    best_score = 999
                    best_sdp = "implicit_inference"

                    if use_syntax and graph is not None:
                        aspect_candidates = self.syntax_engine.extract_aspect_noun_phrases(sent.as_doc())
                        for ac in aspect_candidates:
                            if ac["text"].lower() in NON_ASPECT_TOKENS:
                                continue
                            try:
                                sdp = self.syntax_engine.get_shortest_dependency_path(graph, sent.root.i, ac["root_idx"])
                                dist = len(sdp) if sdp else 99
                                # Category-aligned domain bonus for grounding implicit opinion
                                imp_cat = implicit_eval["implied_category"]
                                ac_low = ac["text"].lower()
                                if imp_cat.startswith("SERVICE#") and any(t in ac_low for t in ["waiter", "server", "staff", "waitstaff", "captain", "hostess", "manager", "service"]):
                                    dist -= 8
                                elif imp_cat.startswith("AMBIENCE#") and any(t in ac_low for t in ["ambience", "decor", "music", "lighting", "tables", "conditioning", "seating"]):
                                    dist -= 8
                                elif imp_cat.startswith("RESTAURANT#PRICES") and any(t in ac_low for t in ["bill", "price", "pricing", "charge", "cost", "rates"]):
                                    dist -= 8
                                elif (imp_cat.startswith("FOOD#") or imp_cat == "HYGIENE#FOOD_SAFETY") and any(t in ac_low for t in CULINARY_TERMS):
                                    dist -= 8
                                elif any(t in ac_low for t in CULINARY_TERMS) or any(t in ac_low for t in ["waiter", "server", "bill", "service", "decor", "music", "lighting"]):
                                    dist -= 3
                                if dist < best_score:
                                    best_score = dist
                                    aspect_target = ac["text"]
                                    best_sdp = " -> ".join([f"{item[1]}[{item[2]}]" for item in sdp])
                            except Exception:
                                pass
                    else:
                        # Fallback for ablation without syntax
                        noun_chunks = list(sent.noun_chunks)
                        for nc in noun_chunks:
                            if nc.text.lower() not in NON_ASPECT_TOKENS:
                                aspect_target = nc.text
                                break

                    quadruples.append({
                        "aspect": aspect_target,
                        "category": implicit_eval["implied_category"],
                        "opinion": s_text,
                        "sentiment": implicit_eval["implied_sentiment"],
                        "type": "implicit",
                        "archetype": implicit_eval["archetype"],
                        "syntactic_path": best_sdp,
                        "confidence": implicit_eval["confidence"],
                        "explanation": implicit_eval["explanation"]
                    })

        # 3. Deduplicate overlapping quadruples prioritizing explicit or higher confidence
        unique_quads = []
        seen = set()
        for q in quadruples:
            key = (q["aspect"].lower(), q["category"])
            if key not in seen:
                seen.add(key)
                unique_quads.append(q)
            else:
                # If existing is neutral and current is polar, replace
                for i, existing in enumerate(unique_quads):
                    if (existing["aspect"].lower(), existing["category"]) == key:
                        if existing["sentiment"] == "neutral" and q["sentiment"] != "neutral":
                            unique_quads[i] = q
                        break

        return unique_quads

    def render_syntax_visualization(self, text: str) -> str:
        """Returns the HTML/SVG representation of the syntactic dependency tree."""
        return self.syntax_engine.render_dependency_svg(text)
