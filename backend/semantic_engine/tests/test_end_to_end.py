"""
End-to-End Integration Verification Suite for Semantic Intelligence Engine (Phase 5).

Verifies the complete pipeline flow:
Academic Knowledge -> Semantic Matching -> Similarity Engine -> Coverage Classification -> Priority -> Evidence -> Report Builder -> REST API.
"""

import tempfile
import unittest
from pathlib import Path

from backend.industry_engine.service import IndustryService
from backend.academic_engine.knowledge.academic_models import AcademicTechnologyRecord
from backend.semantic_engine.config.config import SemanticEngineConfig
from backend.semantic_engine.service import SemanticService
from backend.semantic_engine.api import SemanticController


class TestSemanticEngineEndToEnd(unittest.TestCase):
    """End-to-End verification test suite for the Semantic Intelligence Engine."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.industry_service = IndustryService(force_fallback_embeddings=True)
        self.service = SemanticService(industry_service=self.industry_service)
        self.controller = SemanticController(self.service)

        self.sample_academic_records = [
            AcademicTechnologyRecord(
                technology_id="python",
                canonical_name="Python",
                category="Programming Languages",
                frequency=5,
            ),
            AcademicTechnologyRecord(
                technology_id="machine-learning",
                canonical_name="Machine Learning",
                category="AI / ML",
                frequency=3,
            ),
            AcademicTechnologyRecord(
                technology_id="postgresql",
                canonical_name="PostgreSQL",
                category="Databases",
                frequency=2,
            ),
        ]

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_full_semantic_pipeline_and_api(self):
        # 1. Health Check
        health = self.service.health()
        self.assertEqual(health.status, "healthy")

        # 2. Compare Curriculum against Industry Knowledge
        report = self.service.compare_curriculum(self.sample_academic_records)

        # Validate Report Output Fields
        self.assertTrue(0.0 <= report.alignment_score <= 100.0)
        self.assertIn("covered", report.statistics)
        self.assertIn("partial", report.statistics)
        self.assertIn("gap", report.statistics)

        # Check visualization data structures
        viz = report.visualization_data
        self.assertIn("coverage_pie_chart", viz)
        self.assertIn("gap_bar_chart", viz)
        self.assertIn("alignment_gauge", viz)
        self.assertIn("radar_chart", viz)
        self.assertIn("category_heatmap", viz)
        self.assertIn("skill_network", viz)

        # 3. REST API Controller Verification
        gaps_res = self.controller.get_gaps()
        self.assertIsInstance(gaps_res, list)

        covered_res = self.controller.get_covered()
        self.assertIsInstance(covered_res, list)

        partial_res = self.controller.get_partial()
        self.assertIsInstance(partial_res, list)

        report_res = self.controller.get_report()
        self.assertTrue(report_res.alignment_score >= 0.0)


if __name__ == "__main__":
    unittest.main()
