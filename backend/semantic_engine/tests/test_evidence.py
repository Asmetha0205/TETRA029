"""
Unit tests for Evidence Engine.
"""

import unittest
from backend.semantic_engine.evidence import EvidenceBuilder, ExplanationGenerator
from backend.semantic_engine.models.semantic_models import CoverageClassificationEnum


class TestEvidenceModule(unittest.TestCase):
    """Test suite for ExplanationGenerator and EvidenceBuilder."""

    def test_partial_evidence_text(self):
        exp = ExplanationGenerator.generate_explanation(
            academic_skill="Machine Learning",
            industry_skill="TensorFlow",
            similarity=0.81,
            classification=CoverageClassificationEnum.PARTIAL,
            demand_percentage=41.0,
        )
        self.assertIn("TensorFlow appears in 41.0% of industry jobs", exp)
        self.assertIn("Machine Learning", exp)

    def test_evidence_builder(self):
        ev = EvidenceBuilder.build_evidence(
            academic_skill="Machine Learning",
            industry_skill="TensorFlow",
            similarity=0.81,
            classification=CoverageClassificationEnum.PARTIAL,
            demand_percentage=41.0,
        )
        self.assertIsNotNone(ev.summary)
        self.assertEqual(ev.job_mention_percentage, 41.0)


if __name__ == "__main__":
    unittest.main()
