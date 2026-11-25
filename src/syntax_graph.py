"""Syntax-Aware Dependency Graph Engine for Aspect Quadruple Mining.

Provides:
- Dependency graph construction (NetworkX) from SpaCy parse trees
- Domain-aware culinary noun phrase consolidation (e.g. reshmi kebab, mutton biryani)
- Shortest Dependency Path (SDP) calculation between word spans
- Syntactic negation scope detection (neg, advmod, conj)
- Candidate aspect and opinion extraction via grammatical relations
- HTML/SVG dependency parse visualization for Streamlit
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx
import spacy
from spacy import displacy

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

CULINARY_TERMS = {
    "biryani", "kebab", "kabab", "chaap", "roti", "naan", "paneer", "tikka",
    "dal", "daal", "curry", "thali", "phuchka", "puchka", "rolls", "roll",
    "momos", "momo", "bhetki", "ilish", "chingri", "prawn", "mutton", "chicken",
    "kosha", "rezala", "paratha", "pulao", "dessert", "jamun", "sandesh", "mishti",
    "noodles", "broth", "soup", "platter", "tea", "fish", "dosa", "starters"
}

NON_ASPECT_TOKENS = {
    "i", "we", "you", "they", "it", "this", "that", "my", "our", "us", "me", "them",
    "fly", "cockroach", "insect", "hair", "pocket", "arm", "leg", "night", "podcasts",
    "episodes", "hospital", "pigeon", "cardboard", "leather", "lap", "hole", "instant",
    "heart", "middle", "emergency", "lunch", "dinner", "person", "brother", "neighbor",
    "table four", "moment", "tongue", "cloud", "plate", "single plate", "serving", "someone", "anyone"
}


class SyntaxGraphEngine:
    def __init__(self, spacy_model: Optional[str] = None):
        self.nlp = spacy.load(spacy_model) if spacy_model else nlp

    def parse(self, text: str):
        """Returns SpaCy Doc object."""
        return self.nlp(text)

    def build_dependency_graph(self, doc_or_sent) -> nx.DiGraph:
        """Constructs a directed NetworkX graph representing the syntactic dependency tree.
        Nodes: token indices with attributes (text, pos, dep, lemma).
        Edges: directed from head to dependent with 'dep' attribute.
        """
        graph = nx.DiGraph()
        for token in doc_or_sent:
            graph.add_node(
                token.i,
                text=token.text,
                pos=token.pos_,
                dep=token.dep_,
                lemma=token.lemma_
            )
        for token in doc_or_sent:
            if token.head.i != token.i:
                graph.add_edge(token.head.i, token.i, dep=token.dep_)
        return graph

    def get_shortest_dependency_path(
        self, graph: nx.Graph, source_idx: int, target_idx: int
    ) -> List[Tuple[int, str, str]]:
        """Computes the shortest path in the undirected dependency graph between two tokens.
        Returns list of (token_idx, token_text, edge_dep) along the path.
        """
        undirected = graph.to_undirected()
        try:
            path = nx.shortest_path(undirected, source=source_idx, target=target_idx)
            path_details = []
            for i, node in enumerate(path):
                node_data = graph.nodes[node]
                dep_rel = "ROOT"
                if i > 0:
                    prev_node = path[i - 1]
                    if graph.has_edge(prev_node, node):
                        dep_rel = graph[prev_node][node].get("dep", "")
                    elif graph.has_edge(node, prev_node):
                        dep_rel = graph[node][prev_node].get("dep", "") + "_rev"
                path_details.append((node, node_data["text"], dep_rel))
            return path_details
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def check_negation_scope(self, token) -> Tuple[bool, Optional[str]]:
        """Checks if a token is syntactically modified by a negation word (e.g., not, never, no, n't).
        Traces children and head relations.
        """
        for child in token.children:
            if child.dep_ == "neg" or child.lower_ in {"not", "never", "no", "n't", "hardly", "barely"}:
                return True, child.text
        if token.head.i != token.i:
            for sibling in token.head.children:
                if sibling.dep_ == "neg" and abs(sibling.i - token.i) <= 3:
                    return True, sibling.text
        return False, None

    def extract_aspect_noun_phrases(self, doc) -> List[Dict[str, Any]]:
        """Extracts candidate aspect noun phrases incorporating domain culinary terms."""
        candidates = []
        seen_spans = set()

        # 1. Standard noun chunks
        for chunk in doc.noun_chunks:
            if chunk.root.pos_ in {"PRON"} or chunk.root.lower_ in NON_ASPECT_TOKENS:
                continue
            span_text = chunk.text.strip()
            # Expand with immediately following culinary term if separated
            end_idx = chunk.end
            if end_idx < len(doc) and doc[end_idx].lower_ in CULINARY_TERMS:
                span_text = f"{span_text} {doc[end_idx].text}".strip()
            
            clean_span = " ".join([w for w in span_text.split() if w.lower() not in {"the", "a", "an", "our", "my", "their"}])
            if clean_span and clean_span.lower() not in NON_ASPECT_TOKENS:
                span_key = clean_span.lower()
                if span_key not in seen_spans:
                    seen_spans.add(span_key)
                    candidates.append({
                        "text": clean_span,
                        "root_idx": chunk.root.i,
                        "root_token": chunk.root
                    })

        # 2. Check standalone or compound culinary terms not caught in noun chunks
        for i, token in enumerate(doc):
            if token.lower_ in CULINARY_TERMS:
                # check if preceded by modifier
                term_text = token.text
                root_idx = token.i
                if i > 0 and doc[i-1].pos_ in {"NOUN", "ADJ", "PROPN"}:
                    term_text = f"{doc[i-1].text} {token.text}"
                    root_idx = token.i
                term_key = term_text.lower()
                if term_key not in seen_spans:
                    seen_spans.add(term_key)
                    candidates.append({
                        "text": term_text,
                        "root_idx": root_idx,
                        "root_token": token
                    })

        return candidates

    def extract_syntactic_aspect_opinion_candidates(
        self, text: str
    ) -> List[Dict[str, Any]]:
        """Extracts candidate aspect-opinion pairs using syntactic dependency rules."""
        doc = self.nlp(text)
        graph = self.build_dependency_graph(doc)
        candidates = []

        aspect_phrases = self.extract_aspect_noun_phrases(doc)

        for asp in aspect_phrases:
            root_token = asp["root_token"]
            opinions = []

            # 1. Direct adjectival modifier: amod / advmod
            for child in root_token.children:
                if child.dep_ in {"amod", "advmod"}:
                    is_neg, neg_word = self.check_negation_scope(child)
                    adv = " ".join([c.text for c in child.children if c.dep_ == "advmod"])
                    full_op = f"{adv} {child.text}".strip() if adv else child.text
                    op_text = f"{neg_word} {full_op}".strip() if is_neg else full_op
                    opinions.append({
                        "opinion_text": op_text,
                        "opinion_idx": child.i,
                        "rel": child.dep_,
                        "is_negated": is_neg
                    })

            # 2. Copular / predicate adjective: nsubj -> AUX/VERB -> acomp/attr
            if root_token.dep_ in {"nsubj", "nsubjpass"} or root_token.head.pos_ in {"VERB", "AUX"}:
                head_verb = root_token.head
                for child in head_verb.children:
                    # Case 2a: Predicate adjective or acomp
                    if child.dep_ in {"acomp"} or (child.dep_ in {"attr", "conj"} and child.pos_ in {"ADJ"}):
                        is_neg, neg_word = self.check_negation_scope(child)
                        if not is_neg:
                            is_neg, neg_word = self.check_negation_scope(head_verb)
                        adv = " ".join([c.text for c in child.children if c.dep_ == "advmod"])
                        full_op = f"{adv} {child.text}".strip() if adv else child.text
                        op_text = f"{neg_word} {full_op}".strip() if is_neg else full_op
                        opinions.append({
                            "opinion_text": op_text,
                            "opinion_idx": child.i,
                            "rel": f"{root_token.dep_}->{head_verb.text}->{child.dep_}",
                            "is_negated": is_neg
                        })
                        # Check coordinating conjunct adjectives (e.g. fragrant and tender)
                        for conj_child in child.children:
                            if conj_child.dep_ == "conj" and conj_child.pos_ == "ADJ":
                                c_neg, c_neg_word = self.check_negation_scope(conj_child)
                                c_adv = " ".join([c.text for c in conj_child.children if c.dep_ == "advmod"])
                                c_op = f"{c_adv} {conj_child.text}".strip() if c_adv else conj_child.text
                                c_text = f"{c_neg_word} {c_op}".strip() if c_neg else c_op
                                opinions.append({
                                    "opinion_text": c_text,
                                    "opinion_idx": conj_child.i,
                                    "rel": f"{root_token.dep_}->{head_verb.text}->conj",
                                    "is_negated": c_neg
                                })

                    # Case 2b: Direct object noun with adjectival modifiers (e.g. set a really nice mood)
                    elif child.dep_ in {"dobj", "attr"} and child.pos_ in {"NOUN", "PROPN"}:
                        for mod in child.children:
                            if mod.dep_ in {"amod"} and mod.pos_ == "ADJ":
                                is_neg, neg_word = self.check_negation_scope(mod)
                                adv = " ".join([c.text for c in mod.children if c.dep_ == "advmod"])
                                full_op = f"{adv} {mod.text}".strip() if adv else mod.text
                                op_text = f"{neg_word} {full_op}".strip() if is_neg else full_op
                                opinions.append({
                                    "opinion_text": op_text,
                                    "opinion_idx": mod.i,
                                    "rel": f"{root_token.dep_}->{head_verb.text}->{child.dep_}->amod",
                                    "is_negated": is_neg
                                })

                    # Case 2c: Prepositional phrase complement (e.g. cooked to perfection)
                    elif child.dep_ == "prep":
                        pobjs = [p.text for p in child.children if p.dep_ == "pobj"]
                        if pobjs and any(p.lower() in {"perfection", "disaster", "excess", "shreds", "death"} for p in pobjs):
                            is_neg, neg_word = self.check_negation_scope(child)
                            prep_op = f"{child.text} {' '.join(pobjs)}"
                            opinions.append({
                                "opinion_text": f"{neg_word} {prep_op}".strip() if is_neg else prep_op,
                                "opinion_idx": child.i,
                                "rel": f"{root_token.dep_}->{head_verb.text}->prep",
                                "is_negated": is_neg
                            })

            for op in opinions:
                sdp = self.get_shortest_dependency_path(graph, root_token.i, op["opinion_idx"])
                sdp_str = " -> ".join([f"{item[1]}[{item[2]}]" for item in sdp])
                candidates.append({
                    "aspect_text": asp["text"],
                    "aspect_root_idx": root_token.i,
                    "opinion_text": op["opinion_text"],
                    "opinion_idx": op["opinion_idx"],
                    "syntactic_relation": op["rel"],
                    "is_negated": op["is_negated"],
                    "sdp": sdp_str,
                    "sdp_distance": len(sdp)
                })

        return candidates

    def render_dependency_svg(self, text: str) -> str:
        """Renders an SVG string of the dependency tree for web display."""
        doc = self.nlp(text)
        options = {
            "compact": True,
            "color": "#0F766E",
            "bg": "#F8FAFC",
            "font": "Verdana",
            "distance": 90
        }
        return displacy.render(doc, style="dep", jupyter=False, options=options)
