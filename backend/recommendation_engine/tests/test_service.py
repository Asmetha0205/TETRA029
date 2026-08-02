"""
Unit Tests for Recommendation Service Orchestrator.
"""

import unittest
from backend.recommendation_engine.service.recommendation_service import RecommendationService
from backend.recommendation_engine.service.service_models import ExportReportRequest, GenerateRecommendationsRequest


class TestServiceModule(unittest.TestCase):

    def test_recommendation_service_end_to_end(self):
        svc = RecommendationService()
        req = GenerateRecommendationsRequest(
            gap_analysis_data={
                "alignment_score": 75.0,
                "gap": [
                    {"industry_skill": "Redis", "industry_technology_id": "tech_redis"},
                    {"industry_skill": "Docker", "industry_technology_id": "tech_docker"},
                ]
            }
        )

        resp = svc.generate_recommendations(req)
        self.assertTrue(resp.success)
        self.assertIsNotNone(resp.recommendations)
        self.assertGreater(resp.recommendations.total_recommendations, 0)
        self.assertIsNotNone(resp.learning_path)
        self.assertIsNotNone(resp.report)

    def test_service_export_report(self):
        svc = RecommendationService()

        # Pre-generate
        svc.generate_recommendations(
            GenerateRecommendationsRequest(gap_analysis_data={"gap": ["Redis"]})
        )

        export_resp = svc.export_report(ExportReportRequest(format="markdown"))
        self.assertTrue(export_resp.success)
        self.assertIsNotNone(export_resp.exported_content)
        self.assertIn("CurricuAlign AI", export_resp.exported_content)

