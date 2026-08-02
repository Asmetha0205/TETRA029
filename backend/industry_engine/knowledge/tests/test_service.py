"""
Unit tests for KnowledgeService business facade.
"""

import unittest
from backend.industry_engine.knowledge.exceptions import DuplicateTechnology, TechnologyNotFound, ValidationError
from backend.industry_engine.knowledge.knowledge_models import TechnologyClassification, TechnologyTrend
from backend.industry_engine.knowledge.knowledge_service import KnowledgeService


class TestKnowledgeService(unittest.TestCase):
    """Test suite for KnowledgeService CRUD, search, filter, and snapshot coordination."""

    def setUp(self):
        self.service = KnowledgeService()

    def test_create_and_get_technology(self):
        record = self.service.create_technology(
            canonical_name="TensorFlow",
            category="AI / ML",
            aliases=["tf"],
            demand_score=85.0,
            industry_score=80.0,
        )
        self.assertEqual(record.technology_id, "tensorflow")
        self.assertTrue(self.service.exists("tensorflow"))

        fetched = self.service.get_technology("tensorflow")
        self.assertEqual(fetched.canonical_name, "TensorFlow")

    def test_update_technology(self):
        self.service.create_technology(canonical_name="React", category="Framework", demand_score=80.0)
        updated = self.service.update_technology("react", demand_score=95.0, trend="Rapidly Rising")

        self.assertEqual(updated.demand_score, 95.0)
        self.assertEqual(updated.trend, TechnologyTrend.RAPIDLY_RISING)
        self.assertEqual(updated.version.to_string(), "1.0.1")

    def test_delete_technology(self):
        self.service.create_technology(canonical_name="Flask", category="Framework")
        self.assertTrue(self.service.delete_technology("flask"))
        self.assertFalse(self.service.exists("flask"))
        with self.assertRaises(TechnologyNotFound):
            self.service.get_technology("flask")

    def test_duplicate_error(self):
        self.service.create_technology(canonical_name="PostgreSQL", category="Database")
        with self.assertRaises(DuplicateTechnology):
            self.service.create_technology(canonical_name="PostgreSQL", category="Database")

    def test_validation_error(self):
        with self.assertRaises(ValidationError):
            self.service.create_technology(canonical_name="", category="Database")

    def test_search_and_filter(self):
        self.service.create_technology(canonical_name="Python", category="Language", trend="Rising", industry_score=90)
        self.service.create_technology(canonical_name="PyTorch", category="AI / ML", trend="Rising", industry_score=95)
        self.service.create_technology(canonical_name="Java", category="Language", trend="Stable", industry_score=70)

        py_results = self.service.search("py")
        self.assertEqual(len(py_results), 2)

        lang_results = self.service.filter_by_category("Language")
        self.assertEqual(len(lang_results), 2)

        rising_results = self.service.filter_by_trend("Rising")
        self.assertEqual(len(rising_results), 2)

    def test_statistics(self):
        self.service.create_technology(canonical_name="Redis", category="Database", demand_score=80.0, industry_score=85.0)
        stats = self.service.get_statistics()
        self.assertEqual(stats.total_technologies, 1)
        self.assertEqual(stats.avg_demand_score, 80.0)
        self.assertEqual(stats.avg_industry_score, 85.0)


if __name__ == "__main__":
    unittest.main()
