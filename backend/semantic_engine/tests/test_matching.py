"""
Unit tests for Semantic Matching Engine.
"""

import unittest
from backend.industry_engine.service import IndustryService
from backend.semantic_engine.config.config import SemanticEngineConfig
from backend.semantic_engine.matching import MatchingQueryBuilder, SemanticMatcher


class TestSemanticMatchingModule(unittest.TestCase):
    """Test suite for query builder and semantic matcher."""

    def setUp(self):
        self.industry_service = IndustryService(force_fallback_embeddings=True)
        self.industry_service.refresh_industry()
        self.config = SemanticEngineConfig()
        self.matcher = SemanticMatcher(industry_service=self.industry_service, config=self.config)

    def test_query_builder(self):
        query = MatchingQueryBuilder.build_query("Python", category="Programming Languages")
        self.assertEqual(query["query_text"], "Python")
        self.assertEqual(query["where_filter"], {"category": "Programming Languages"})

    def test_semantic_matcher_candidate_retrieval(self):
        candidate = self.matcher.find_best_candidate("Machine Learning")
        self.assertIsNotNone(candidate)
        self.assertTrue(candidate.similarity_score >= 0.0)


if __name__ == "__main__":
    unittest.main()
