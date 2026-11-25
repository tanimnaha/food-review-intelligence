"""Unit tests for ImplicitOpinionDisentangler."""

import unittest
from src.implicit_disentangler import ImplicitOpinionDisentangler

class TestImplicitOpinionDisentangler(unittest.TestCase):
    def setUp(self):
        self.disentangler = ImplicitOpinionDisentangler()

    def test_idiomatic_metaphor(self):
        text = "A single plate of prawn malai curry burned a massive hole in my pocket."
        res = self.disentangler.classify_opinion(text, aspect_text="prawn malai curry")
        self.assertEqual(res["opinion_type"], "implicit")
        self.assertEqual(res["implied_sentiment"], "negative")
        self.assertEqual(res["implied_category"], "RESTAURANT#PRICES")
        self.assertTrue(res["is_metaphor"])

    def test_factual_delay(self):
        text = "We waited forty-five minutes before a waiter brought water."
        res = self.disentangler.classify_opinion(text, aspect_text="waiter")
        self.assertEqual(res["opinion_type"], "implicit")
        self.assertEqual(res["implied_sentiment"], "negative")
        self.assertEqual(res["implied_category"], "SERVICE#PROMPTNESS")

    def test_biological_consequence(self):
        text = "Both my brother and I spent the entire night throwing up after dinner."
        res = self.disentangler.classify_opinion(text, aspect_text="dinner")
        self.assertEqual(res["opinion_type"], "implicit")
        self.assertEqual(res["implied_sentiment"], "negative")
        self.assertEqual(res["implied_category"], "HYGIENE#FOOD_SAFETY")

    def test_portion_disparity(self):
        text = "The mutton biryani contained only one tiny potato for that price."
        res = self.disentangler.classify_opinion(text, aspect_text="mutton biryani")
        self.assertEqual(res["opinion_type"], "implicit")
        self.assertEqual(res["implied_sentiment"], "negative")
        self.assertEqual(res["implied_category"], "FOOD#PRICES")

    def test_explicit_opinion(self):
        text = "The mutton biryani was fragrant, aromatic and delicious."
        res = self.disentangler.classify_opinion(text, aspect_text="mutton biryani")
        self.assertEqual(res["opinion_type"], "explicit")
        self.assertEqual(res["implied_sentiment"], "positive")

if __name__ == "__main__":
    unittest.main()
