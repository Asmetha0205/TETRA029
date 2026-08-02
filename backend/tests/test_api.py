"""
Integration tests for Unified System API.
"""

import unittest
from backend.api.controllers import SystemApiController
from backend.orchestrator.analysis_orchestrator import AnalysisOrchestrator
from backend.health.health_service import HealthService
from backend.cache.cache_service import CacheService

try:
    from fastapi.testclient import TestClient
    from backend.api.routes import app
    HAS_TEST_CLIENT = True
except Exception:
    HAS_TEST_CLIENT = False


class TestUnifiedAPI(unittest.TestCase):

    def setUp(self):
        self.orchestrator = AnalysisOrchestrator()
        self.health_service = HealthService()
        self.cache_service = CacheService()
        self.controller = SystemApiController(
            orchestrator=self.orchestrator,
            health_service=self.health_service,
            cache_service=self.cache_service,
        )
        if HAS_TEST_CLIENT:
            self.client = TestClient(app)

    def test_status_endpoint(self):
        if HAS_TEST_CLIENT:
            resp = self.client.get("/status")
            self.assertEqual(resp.status_code, 200)
            json_data = resp.json()
            self.assertTrue(json_data["success"])
            self.assertEqual(json_data["data"]["status"], "OPERATIONAL")
        else:
            res = self.controller.get_status()
            self.assertTrue(res.success)
            self.assertEqual(res.data["status"], "OPERATIONAL")

    def test_health_endpoint(self):
        if HAS_TEST_CLIENT:
            resp = self.client.get("/health")
            self.assertEqual(resp.status_code, 200)
            json_data = resp.json()
            self.assertTrue(json_data["success"])
        else:
            res = self.controller.get_health()
            self.assertTrue(res.success)
            self.assertIn("status", res.data)

    def test_dashboard_endpoint(self):
        if HAS_TEST_CLIENT:
            resp = self.client.get("/dashboard")
            self.assertEqual(resp.status_code, 200)
            json_data = resp.json()
            self.assertTrue(json_data["success"])
        else:
            res = self.controller.get_dashboard()
            self.assertTrue(res.success)

    def test_system_statistics_endpoint(self):
        if HAS_TEST_CLIENT:
            resp = self.client.get("/system/statistics")
            self.assertEqual(resp.status_code, 200)
            json_data = resp.json()
            self.assertTrue(json_data["success"])
        else:
            res = self.controller.get_system_statistics()
            self.assertTrue(res.success)


if __name__ == "__main__":
    unittest.main()
