"""Unit tests for the end-to-end ACOS pipeline."""

import unittest
from src.acos_pipeline import ACOSPipeline

class TestACOSPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = ACOSPipeline()

    def test_compound_sentence_quadruples(self):
        text = "The mutton biryani was fragrant, but the washroom was a biohazard and the bill was astronomical."
        quads = self.pipeline.extract_quadruples(text)
        self.assertGreaterEqual(len(quads), 2)

        categories = [q["category"] for q in quads]
        sentiments = [q["sentiment"] for q in quads]
        types = [q["type"] for q in quads]

        self.assertIn("FOOD#QUALITY", categories)
        self.assertIn("positive", sentiments)
        self.assertIn("negative", sentiments)
        self.assertIn("implicit", types)
        self.assertIn("explicit", types)

    def test_implicit_factual_delay(self):
        text = "We waited forty-five minutes before a waiter brought water."
        quads = self.pipeline.extract_quadruples(text)
        self.assertGreater(len(quads), 0)
        has_promptness = any(q["category"] == "SERVICE#PROMPTNESS" for q in quads)
        has_negative = any(q["sentiment"] == "negative" for q in quads)
        self.assertTrue(has_promptness)
        self.assertTrue(has_negative)

    def test_syntax_svg_rendering(self):
        text = "The mutton biryani was delicious."
        svg = self.pipeline.render_syntax_visualization(text)
        self.assertIn("<svg", svg)
        self.assertIn("displacy", svg)

if __name__ == "__main__":
    unittest.main()
