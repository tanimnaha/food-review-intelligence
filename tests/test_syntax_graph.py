"""Unit tests for SyntaxGraphEngine."""

import unittest
from src.syntax_graph import SyntaxGraphEngine

class TestSyntaxGraphEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SyntaxGraphEngine()

    def test_graph_construction(self):
        text = "The mutton biryani was fragrant."
        doc = self.engine.parse(text)
        graph = self.engine.build_dependency_graph(doc)
        self.assertGreater(len(graph.nodes), 0)
        self.assertGreater(len(graph.edges), 0)

    def test_shortest_dependency_path(self):
        text = "The mutton biryani was fragrant."
        doc = self.engine.parse(text)
        graph = self.engine.build_dependency_graph(doc)
        # biryani (token 2) to fragrant (token 4)
        sdp = self.engine.get_shortest_dependency_path(graph, 2, 4)
        self.assertTrue(len(sdp) >= 2)
        words_in_path = [item[1] for item in sdp]
        self.assertIn("biryani", words_in_path)
        self.assertIn("fragrant", words_in_path)

    def test_negation_scope_detection(self):
        text = "The soup was not hot."
        doc = self.engine.parse(text)
        # 'hot' is token 4
        hot_token = doc[4]
        is_neg, neg_word = self.engine.check_negation_scope(hot_token)
        self.assertTrue(is_neg)
        self.assertEqual(neg_word.lower(), "not")

    def test_candidate_extraction(self):
        text = "The fragrant mutton biryani arrived quickly but the waiter was rude."
        candidates = self.engine.extract_syntactic_aspect_opinion_candidates(text)
        self.assertGreater(len(candidates), 0)
        aspects = [c["aspect_text"].lower() for c in candidates]
        opinions = [c["opinion_text"].lower() for c in candidates]
        # Should detect waiter / rude or biryani / fragrant
        has_waiter = any("waiter" in a for a in aspects)
        has_rude = any("rude" in o for o in opinions)
        self.assertTrue(has_waiter or has_rude)

if __name__ == "__main__":
    unittest.main()
