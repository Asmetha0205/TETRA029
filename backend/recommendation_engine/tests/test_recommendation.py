"""
Unit Tests for Recommendation Builder Module.
"""

import unittest
from backend.recommendation_engine.recommendation.recommendation_builder import RecommendationBuilder
from backend.recommendation_engine.recommendation.recommendation_validator import RecommendationValidator


class TestRecommendationModule(unittest.TestCase):

    def test_recommendation_builder(self):
        builder = RecommendationBuilder()
        llm_payload = {
            "recommendations": [
                {
                    "technology": "Redis",
                    "priority": "High",
                    "industry_score": 91,
                    "trend": "Rising",
                    "reason": "Redis is essential for backend systems.",
                    "recommended_course": "Advanced Backend Systems",
                    "recommended_module": "Caching & Distributed Systems",
                    "learning_outcomes": ["Implement Redis cache"],
                    "lab": "Implement Redis cache in FastAPI.",
                    "mini_project": "Distributed API Cache",
                    "learning_path": ["Docker", "Redis", "FastAPI"],
                    "references": ["Graph Evidence"],
                    "confidence": 0.94
                }
            ]
        }
        evidence = [{"tech_name": "Redis", "industry_score": 91}]

        res_set = builder.build_recommendations(llm_payload, evidence)
        self.assertEqual(res_set.total_recommendations, 1)
        rec = res_set.recommendations[0]
        self.assertEqual(rec.technology, "Redis")
        self.assertEqual(rec.priority, "High")
        self.assertEqual(rec.industry_score, 91.0)
        self.assertEqual(rec.lab, "Implement Redis cache in FastAPI.")

    def test_recommendation_validator(self):
        builder = RecommendationBuilder()
        llm_payload = {
            "recommendations": [
                {
                    "technology": "Docker",
                    "priority": "Critical",
                    "industry_score": 90,
                    "trend": "Rising",
                    "reason": "Containerization foundation",
                    "recommended_course": "Cloud Systems",
                    "recommended_module": "Containers",
                    "learning_outcomes": ["Build Dockerfiles"],
                    "lab": "Docker compose lab",
                    "mini_project": "Container Project",
                    "learning_path": ["SQL", "Docker"],
                    "references": ["Ref"],
                    "confidence": 0.92
                }
            ]
        }
        res_set = builder.build_recommendations(llm_payload, [{"tech_name": "Docker"}])
        report = RecommendationValidator.validate_result_set(res_set)
        self.assertTrue(report.is_valid)

