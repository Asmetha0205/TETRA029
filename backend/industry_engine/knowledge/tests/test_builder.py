"""
Unit tests for KnowledgeBuilder in the Industry Knowledge Layer.
"""

import unittest
from backend.industry_engine.knowledge.knowledge_builder import KnowledgeBuilder
from backend.industry_engine.knowledge.knowledge_models import (
    TechnologyClassification,
    TechnologyStatus,
    TechnologyTrend,
)


class TestKnowledgeBuilder(unittest.TestCase):
    """Test suite for KnowledgeBuilder transformation logic."""

    def setUp(self):
        self.builder = KnowledgeBuilder()

    def test_build_single_record(self):
        record = self.builder.build_single(
            canonical_name="PyTorch",
            category="AI / ML",
            aliases=["pytorch", "torch"],
            frequency=100,
            demand_score=90.0,
            industry_score=88.5,
            trend="Rapidly Rising",
            growth=15.2,
            classification="Core Technology",
            role_coverage={"AI Engineer": 85.0, "Data Scientist": 60.0},
            source="test_source",
            timestamp="2026-08-02T10:00:00Z",
        )

        self.assertEqual(record.technology_id, "pytorch")
        self.assertEqual(record.canonical_name, "PyTorch")
        self.assertEqual(record.category, "AI / ML")
        self.assertEqual(record.aliases, ["pytorch", "torch"])
        self.assertEqual(record.frequency, 100)
        self.assertEqual(record.demand_score, 90.0)
        self.assertEqual(record.industry_score, 88.5)
        self.assertEqual(record.trend, TechnologyTrend.RAPIDLY_RISING)
        self.assertEqual(record.growth, 15.2)
        self.assertEqual(record.classification, TechnologyClassification.CORE)
        self.assertEqual(record.status, TechnologyStatus.ACTIVE)
        self.assertIn("AI Engineer", record.role_coverage)

    def test_determinism(self):
        """Verify identical inputs yield identical records."""
        input_data = [
            {"canonical_name": "Docker", "category": "DevOps", "aliases": ["docker-ce", "container"]},
            {"canonical_name": "Kubernetes", "category": "DevOps", "aliases": ["k8s"]},
        ]
        freq_data = {
            "technologies": [
                {"name": "Docker", "mentions": 50, "percentage": 25.0, "rank": 2},
                {"name": "Kubernetes", "mentions": 80, "percentage": 40.0, "rank": 1},
            ]
        }
        demand_data = {
            "technologies": [
                {"name": "Docker", "demand_score": 75.0, "industry_score": 78.0, "trend": "Rising"},
                {"name": "Kubernetes", "demand_score": 92.0, "industry_score": 90.0, "trend": "Rapidly Rising"},
            ]
        }

        records_1 = self.builder.build(
            normalization_result=input_data,
            frequency_report=freq_data,
            industry_report=demand_data,
            source="test",
            timestamp="2026-08-02T12:00:00Z",
        )

        records_2 = self.builder.build(
            normalization_result=input_data,
            frequency_report=freq_data,
            industry_report=demand_data,
            source="test",
            timestamp="2026-08-02T12:00:00Z",
        )

        self.assertEqual(len(records_1), len(records_2))
        for r1, r2 in zip(records_1, records_2):
            self.assertEqual(r1.model_dump(), r2.model_dump())


if __name__ == "__main__":
    unittest.main()
