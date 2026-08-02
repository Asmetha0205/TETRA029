"""
Unit Tests for Evidence Retrieval Engine.
"""

import unittest
from backend.recommendation_engine.retrieval.evidence_retriever import EvidenceRetriever
from backend.recommendation_engine.retrieval.ranking import EvidenceRanker
from backend.recommendation_engine.retrieval.retrieval_service import RetrievalService


class TestRetrievalModule(unittest.TestCase):

    def test_evidence_retriever_single_gap(self):
        retriever = EvidenceRetriever()
        ev = retriever.retrieve_evidence_for_gap("Redis")
        self.assertEqual(ev["tech_name"], "Redis")
        self.assertIn("demand_score", ev)
        self.assertIn("industry_score", ev)
        self.assertIn("trend", ev)

    def test_evidence_ranking(self):
        raw_evidence = [
            {"tech_name": "Docker", "demand_score": 90, "industry_score": 92, "frequency": 100, "trend": "Rising"},
            {"tech_name": "GraphQL", "demand_score": 75, "industry_score": 78, "frequency": 40, "trend": "Stable"},
        ]
        ranked = EvidenceRanker.rank_evidence(raw_evidence)
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0].technology, "Docker")
        self.assertGreater(ranked[0].rank_score, ranked[1].rank_score)

    def test_retrieval_service_caching(self):
        svc = RetrievalService()
        ev1 = svc.get_single_evidence("Redis")
        ev2 = svc.get_single_evidence("Redis")
        self.assertEqual(ev1, ev2)

