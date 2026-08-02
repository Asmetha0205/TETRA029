"""
Unit Tests for LLM Recommendation Module.
"""

import unittest
from backend.recommendation_engine.llm.gemini_client import GeminiClient
from backend.recommendation_engine.llm.recommendation_generator import LLMRecommendationGenerator
from backend.recommendation_engine.llm.response_parser import LLMResponseParser
from backend.recommendation_engine.llm.validator import LLMOutputValidator


class TestLLMModule(unittest.TestCase):

    def test_response_parser_clean_json(self):
        raw_markdown = """```json
        {
          "recommendations": [
            {
              "technology": "Redis",
              "priority": "High",
              "industry_score": 91,
              "trend": "Rising",
              "reason": "Popular cache store.",
              "recommended_course": "Advanced Backend",
              "recommended_module": "Caching",
              "learning_outcomes": ["Master Redis"],
              "lab": "Implement Redis cache",
              "mini_project": "Redis API",
              "learning_path": ["Docker", "Redis"],
              "references": ["Graph"],
              "confidence": 0.94
            }
          ]
        }
        ```"""

        parsed = LLMResponseParser.parse_recommendations_json(raw_markdown)
        self.assertIn("recommendations", parsed)
        self.assertEqual(parsed["recommendations"][0]["technology"], "Redis")

    def test_llm_output_validator(self):
        parsed = {
            "recommendations": [
                {
                    "technology": "Redis",
                    "priority": "High",
                    "industry_score": 91,
                    "trend": "Rising",
                    "reason": "Reason",
                    "recommended_course": "Course",
                    "recommended_module": "Module",
                    "learning_outcomes": ["Outcome 1"],
                    "lab": "Lab",
                    "mini_project": "Project",
                    "learning_path": ["Docker", "Redis"],
                    "references": ["Ref"],
                    "confidence": 0.95
                }
            ]
        }
        val = LLMOutputValidator.validate_parsed_json(parsed, allowed_technologies=["Redis"])
        self.assertTrue(val.is_valid)

    def test_recommendation_generator_fallback(self):
        generator = LLMRecommendationGenerator()
        out = generator.generate_recommendations(
            gap_analysis_data={"gap": ["Redis"]},
            evidence_data=[{"tech_name": "Redis", "industry_score": 91}]
        )
        self.assertIn("payload", out)
        self.assertTrue(out["validation"].is_valid)

