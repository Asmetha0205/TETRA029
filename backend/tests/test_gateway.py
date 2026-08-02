"""
Unit tests for Gateway Layer.
"""

import unittest
from backend.gateway.academic_gateway import AcademicGateway
from backend.gateway.industry_gateway import IndustryGateway
from backend.gateway.semantic_gateway import SemanticGateway
from backend.gateway.recommendation_gateway import RecommendationGateway


class TestGateways(unittest.TestCase):

    def test_gateway_names(self):
        ac_gw = AcademicGateway()
        ind_gw = IndustryGateway()
        sem_gw = SemanticGateway()
        rec_gw = RecommendationGateway()

        self.assertIn("Academic", ac_gw.get_engine_name())
        self.assertIn("Industry", ind_gw.get_engine_name())
        self.assertIn("Semantic", sem_gw.get_engine_name())
        self.assertIn("Recommendation", rec_gw.get_engine_name())

    def test_gateway_health_checks(self):
        ac_gw = AcademicGateway()
        ind_gw = IndustryGateway()
        sem_gw = SemanticGateway()
        rec_gw = RecommendationGateway()

        self.assertIsNotNone(ac_gw.check_health())
        self.assertIsNotNone(ind_gw.check_health())
        self.assertIsNotNone(sem_gw.check_health())
        self.assertIsNotNone(rec_gw.check_health())


if __name__ == "__main__":
    unittest.main()
