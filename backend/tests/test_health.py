"""
Unit tests for Health Service.
"""

import unittest
from backend.health.health_service import HealthService
from backend.health.health_models import SystemHealthStatusEnum


class TestHealthService(unittest.TestCase):

    def test_overall_health_check(self):
        hs = HealthService()
        report = hs.check_health()

        self.assertIn(report.status, [
            SystemHealthStatusEnum.HEALTHY,
            SystemHealthStatusEnum.DEGRADED,
            SystemHealthStatusEnum.UNHEALTHY,
        ])
        self.assertIsNotNone(report.academic_engine)
        self.assertIsNotNone(report.industry_engine)
        self.assertIsNotNone(report.semantic_engine)
        self.assertIsNotNone(report.recommendation_engine)


if __name__ == "__main__":
    unittest.main()
