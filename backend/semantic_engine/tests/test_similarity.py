"""
Unit tests for Similarity Engine.
"""

import unittest
from backend.semantic_engine.config.config import SemanticThresholdConfig
from backend.semantic_engine.models.semantic_models import CoverageClassificationEnum
from backend.semantic_engine.similarity import CosineSimilarityCalculator, SimilarityService, ThresholdManager


class TestSimilarityModule(unittest.TestCase):
    """Test suite for CosineSimilarityCalculator, ThresholdManager, and SimilarityService."""

    def setUp(self):
        self.service = SimilarityService()

    def test_cosine_similarity_identical_vectors(self):
        vec_a = [0.1, 0.2, 0.3, 0.4]
        score = CosineSimilarityCalculator.calculate(vec_a, vec_a)
        self.assertAlmostEqual(score, 1.0, places=3)

    def test_threshold_classification(self):
        tm = ThresholdManager(config=SemanticThresholdConfig(covered_threshold=0.85, partial_threshold=0.60))
        self.assertEqual(tm.classify_similarity(0.90), CoverageClassificationEnum.COVERED)
        self.assertEqual(tm.classify_similarity(0.75), CoverageClassificationEnum.PARTIAL)
        self.assertEqual(tm.classify_similarity(0.40), CoverageClassificationEnum.GAP)


if __name__ == "__main__":
    unittest.main()
