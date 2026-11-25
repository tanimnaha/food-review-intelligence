"""Unit Tests for FoodLensChatbotEngine.

Validates:
1. Conversational greetings and guidance
2. Dynamic ACOS review parsing & polarity blindness detection
3. Implicit opinion disentanglement handling
4. Restaurant recommendations by cuisine and zone
5. Specific restaurant profile and verified FSSAI audit lookup
6. Academic credits and methodology answers (Dr. Saberi Goswami)
"""

import unittest
from src.foodlens_chatbot import FoodLensChatbotEngine


class TestFoodLensChatbotEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chatbot = FoodLensChatbotEngine()

    def test_greeting_and_help(self):
        res = self.chatbot.respond("hello")
        self.assertIn("ACOS FoodLens", res)
        self.assertIn("Review Parsing", res)

    def test_polarity_blindness_review_analysis(self):
        review = "The mutton biryani was fragrant, tender and cooked to perfection, but the waiter completely ignored our table for 45 minutes."
        res = self.chatbot.respond(f"Analyze review: {review}")
        self.assertIn("Polarity Blindness Averted", res)
        self.assertIn("mutton biryani", res)
        self.assertIn("waiter", res)
        self.assertIn("FOOD#QUALITY", res)

    def test_implicit_biological_symptom_analysis(self):
        review = "Both of us spent the entire night hugging the toilet bowl after eating the seafood platter."
        res = self.chatbot.respond(review)
        self.assertIn("HYGIENE#FOOD_SAFETY", res)
        self.assertIn("IMPLICIT", res)

    def test_restaurant_recommendations(self):
        res = self.chatbot.respond("Recommend top biryani places in Park Street")
        self.assertIn("Top Dining Recommendations", res)
        self.assertIn("Park Street", res)

    def test_specific_restaurant_profile(self):
        res = self.chatbot.respond("Tell me about Arsalan")
        self.assertIn("Restaurant Profile: **Arsalan**", res)
        self.assertIn("Park Street", res)
        self.assertIn("Municipal Safety Score", res)

    def test_academic_supervisor_and_acos(self):
        res_guide = self.chatbot.respond("Who is the faculty guide for this project?")
        self.assertIn("Dr. Saberi Goswami", res_guide)
        self.assertIn("Tanim Naha", res_guide)
        self.assertIn("Srilekha", res_guide)
        self.assertIn("Subhamita", res_guide)
        self.assertIn("Yashamoti", res_guide)

        res_acos = self.chatbot.respond("What is the ACOS formulation?")
        self.assertIn("Aspect-Category-Opinion-Sentiment", res_acos)


if __name__ == "__main__":
    unittest.main()
