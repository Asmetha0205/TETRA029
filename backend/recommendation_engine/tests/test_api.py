"""
Unit Tests for REST APIs and Controller Logic.
"""

import unittest
from backend.recommendation_engine.api.controllers import RecommendationController
from backend.recommendation_engine.api.schemas import GenerateRecommendationsApiRequest
from backend.recommendation_engine.graph.graph_service import GraphService
from backend.recommendation_engine.service.recommendation_service import RecommendationService


class TestApiModule(unittest.TestCase):

    def setUp(self):
        self.graph_svc = GraphService()
        self.rec_svc = RecommendationService(repository=self.graph_svc.repo)
        self.controller = RecommendationController(self.rec_svc, self.graph_svc)

    def test_api_generate_recommendations(self):
        req = GenerateRecommendationsApiRequest(
            gap_analysis_data={
                "alignment_score": 75.0,
                "gap": ["Redis", "Docker", "FastAPI"]
            }
        )
        res = self.controller.generate_recommendations(req)
        self.assertEqual(res.status, "success")
        self.assertIn("recommendations", res.data)

    def test_api_get_graph_statistics(self):
        res = self.controller.get_graph_summary()
        self.assertEqual(res.status, "success")
        self.assertIn("total_nodes", res.data)

    def test_api_get_learning_path(self):
        res = self.controller.get_learning_path(["Docker", "Redis", "FastAPI"])
        self.assertEqual(res.status, "success")
        self.assertGreater(res.data["total_steps"], 0)

    def test_api_get_report(self):
        res = self.controller.get_report("markdown")
        self.assertEqual(res.status, "success")
        self.assertIn("content", res.data)
