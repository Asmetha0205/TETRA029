"""
Unit tests for Coverage Classification Module.
"""

import unittest
from backend.semantic_engine.classification import CoverageClassifier
from backend.semantic_engine.models.semantic_models import CoverageClassificationEnum


class TestCoverageClassificationModule(unittest.TestCase):
    """Test suite for CoverageClassifier."""

    def setUp(self):
        self.classifier = CoverageClassifier()

    def test_exact_name_match_is_covered(self):
        cls = self.classifier.classify_match("Python", "python", 0.5)
        self.assertEqual(cls, CoverageClassificationEnum.COVERED)

    def test_summary_statistics(self):
        items = [CoverageClassificationEnum.COVERED, CoverageClassificationEnum.PARTIAL, CoverageClassificationEnum.GAP]
        summary = self.classifier.summarize_classifications(items)
        self.assertEqual(summary.total_skills, 3)
        self.assertEqual(summary.covered_count, 1)
        self.assertAlmostEqual(summary.coverage_percentage, 33.3, places=1)


if __name__ == "__main__":
    unittest.main()
