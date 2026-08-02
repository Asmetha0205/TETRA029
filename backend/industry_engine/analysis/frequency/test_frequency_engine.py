"""
Comprehensive Unit Tests for the CurricuAlign AI Technology Frequency Analysis Engine.
Tests: FrequencyCounter, CategoryCounter, RoleCounter, StatisticsGenerator,
Aggregator, ReportGenerator, and end-to-end FrequencyEngine.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from backend.industry_engine.analysis.frequency.models import (
    CategoryFrequency,
    FrequencyReport,
    FrequencyStatistics,
    JobTechnologyRecord,
    RoleFrequency,
    TechnologyFrequency,
)
from backend.industry_engine.analysis.frequency.config import FrequencyConfig
from backend.industry_engine.analysis.frequency.exceptions import (
    DuplicateJobError,
    EmptyDatasetError,
    InvalidInputError,
    MalformedRecordError,
)
from backend.industry_engine.analysis.frequency.frequency_counter import FrequencyCounter
from backend.industry_engine.analysis.frequency.category_counter import CategoryCounter
from backend.industry_engine.analysis.frequency.role_counter import RoleCounter
from backend.industry_engine.analysis.frequency.statistics import StatisticsGenerator
from backend.industry_engine.analysis.frequency.aggregator import Aggregator
from backend.industry_engine.analysis.frequency.report_generator import ReportGenerator
from backend.industry_engine.analysis.frequency.frequency_engine import FrequencyEngine


SAMPLE_RECORDS = [
    JobTechnologyRecord(
        job_id="J001",
        technologies={"languages": ["Python"], "frameworks": ["FastAPI"], "databases": ["Redis"], "cloud": ["AWS"]},
        role="AI Engineer",
    ),
    JobTechnologyRecord(
        job_id="J002",
        technologies={"languages": ["Python", "Java"], "frameworks": ["Spring Boot"], "databases": ["PostgreSQL"], "cloud": ["AWS"]},
        role="AI Engineer",
    ),
    JobTechnologyRecord(
        job_id="J003",
        technologies={"languages": ["Python", "JavaScript"], "frameworks": ["FastAPI", "React"], "databases": ["PostgreSQL", "Redis"], "cloud": ["GCP"]},
        role="Full Stack Engineer",
    ),
    JobTechnologyRecord(
        job_id="J004",
        technologies={"languages": ["Python"], "frameworks": ["FastAPI", "Flask"], "databases": ["MongoDB"], "ai": ["PyTorch", "LangChain"]},
        role="AI Engineer",
    ),
    JobTechnologyRecord(
        job_id="J005",
        technologies={"languages": ["Go", "Python"], "frameworks": [], "databases": ["PostgreSQL"], "devops": ["Docker", "Kubernetes"]},
        role="Backend Engineer",
    ),
]

SAMPLE_DICTS = [
    {"job_id": "D001", "technologies": {"languages": ["Python"], "frameworks": ["FastAPI"]}, "role": "AI Engineer"},
    {"job_id": "D002", "technologies": {"languages": ["Python", "Java"], "cloud": ["AWS"]}, "role": "AI Engineer"},
]


# ============================================================
# FrequencyCounter
# ============================================================
class TestFrequencyCounter(unittest.TestCase):
    def setUp(self):
        self.counter = FrequencyCounter()

    def test_process_and_get_frequencies(self):
        self.counter.process_batch(SAMPLE_RECORDS)
        freqs = self.counter.get_technology_frequencies()
        self.assertGreater(len(freqs), 0)
        python_freq = next(f for f in freqs if f.name == "Python")
        self.assertEqual(python_freq.mentions, 5)
        self.assertEqual(python_freq.unique_jobs, 5)  # Python is in all 5 jobs
        self.assertEqual(python_freq.percentage, 100.0)
        self.assertEqual(python_freq.rank, 1)

    def test_min_mentions_filter(self):
        self.counter.process_batch(SAMPLE_RECORDS)
        freqs = self.counter.get_technology_frequencies(min_mentions=5)
        self.assertEqual(len(freqs), 1)
        self.assertEqual(freqs[0].name, "Python")

    def test_technology_count(self):
        self.assertEqual(self.counter.get_technology_count(), 0)
        self.counter.process_batch(SAMPLE_RECORDS)
        self.assertGreater(self.counter.get_technology_count(), 3)

    def test_reset(self):
        self.counter.process_batch(SAMPLE_RECORDS)
        self.counter.reset()
        self.assertEqual(self.counter.get_technology_count(), 0)
        self.assertEqual(self.counter.get_total_jobs(), 0)


# ============================================================
# CategoryCounter
# ============================================================
class TestCategoryCounter(unittest.TestCase):
    def setUp(self):
        self.counter = CategoryCounter()

    def test_record_and_summary(self):
        for rec in SAMPLE_RECORDS:
            for cat, names in rec.technologies.items():
                for name in names:
                    self.counter.record(cat, name, rec.job_id)
        summary = self.counter.build_summary()
        self.assertGreater(len(summary), 0)

    def test_reset(self):
        self.counter.record("languages", "Python", "J001")
        self.counter.reset()
        summary = self.counter.build_summary()
        self.assertEqual(len(summary), 0)


# ============================================================
# RoleCounter
# ============================================================
class TestRoleCounter(unittest.TestCase):
    def setUp(self):
        self.counter = RoleCounter()

    def test_record_and_top_for_role(self):
        for rec in SAMPLE_RECORDS:
            tech_names = [name for names in rec.technologies.values() for name in names]
            self.counter.record(rec.role or "", tech_names, rec.job_id)
        ai_top = self.counter.get_top_for_role("AI Engineer", top_n=5)
        self.assertTrue(any(t["technology"] == "Python" for t in ai_top))

    def test_build_all_roles(self):
        for rec in SAMPLE_RECORDS:
            tech_names = [name for names in rec.technologies.values() for name in names]
            self.counter.record(rec.role or "", tech_names, rec.job_id)
        all_roles = self.counter.build_all_roles()
        self.assertEqual(len(all_roles), 3)
        roles_list = [r["role"] for r in all_roles]
        self.assertIn("AI Engineer", roles_list)


# ============================================================
# StatisticsGenerator
# ============================================================
class TestStatisticsGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = StatisticsGenerator()

    def test_compute(self):
        tech_freqs = [
            TechnologyFrequency(name="Python", category="Programming Language", mentions=100, unique_jobs=90, percentage=90.0, rank=1),
            TechnologyFrequency(name="FastAPI", category="Framework", mentions=50, unique_jobs=40, percentage=40.0, rank=2),
        ]
        stats = self.generator.compute(tech_freqs, [], 100)
        self.assertEqual(len(stats.top_technologies), 2)
        self.assertEqual(stats.total_unique_technologies, 2)
        self.assertEqual(stats.average_technologies_per_job, 1.5)
        self.assertGreater(stats.technology_diversity_score, 0)


# ============================================================
# Aggregator
# ============================================================
class TestAggregator(unittest.TestCase):
    def setUp(self):
        self.aggregator = Aggregator()

    def test_process_batch(self):
        self.aggregator.process_batch(SAMPLE_RECORDS)
        tech_freqs, cat_freqs, role_freqs, total, _ = self.aggregator.process()
        self.assertEqual(total, 5)
        self.assertGreater(len(tech_freqs), 0)
        self.assertGreater(len(cat_freqs), 0)

    def test_throws_on_empty(self):
        with self.assertRaises(EmptyDatasetError):
            self.aggregator.process_batch([])


# ============================================================
# ReportGenerator
# ============================================================
class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self.config = FrequencyConfig()
        self.generator = ReportGenerator(self.config)

    def test_generate_report(self):
        tech_freqs = [
            TechnologyFrequency(name="Python", category="Programming Language", mentions=10, unique_jobs=5, percentage=100, rank=1),
        ]
        stats = FrequencyStatistics(total_unique_technologies=1, average_technologies_per_job=2.0)
        report = self.generator.generate(tech_freqs, [], [], stats, 5)
        self.assertEqual(report.summary["total_jobs"], 5)
        self.assertEqual(report.summary["unique_technologies"], 1)

    def test_generate_text_report(self):
        tech_freqs = [
            TechnologyFrequency(name="Python", category="Programming Language", mentions=10, unique_jobs=5, percentage=100, rank=1),
        ]
        report_text = self.generator.generate_technology_technical_report(tech_freqs)
        self.assertIn("Python", report_text)

    def test_export_report(self):
        tech_freqs = [
            TechnologyFrequency(name="Python", category="Programming Language", mentions=10, unique_jobs=5, percentage=100, rank=1),
        ]
        stats = FrequencyStatistics()
        report = self.generator.generate(tech_freqs, [], [], stats, 1)
        temp_dir = tempfile.mkdtemp()
        try:
            from pathlib import Path
            path = Path(temp_dir) / "report.json"
            self.generator.export_report(report, path)
            self.assertTrue(path.exists())
        finally:
            import shutil
            shutil.rmtree(temp_dir)

    def test_write_summary(self):
        s = self.generator.write_summary({"total_jobs": 100, "unique_technologies": 12, "average_technologies_per_job": 8.5})
        self.assertIn("100", s)
        self.assertIn("12", s)
        self.assertIn("8.5", s)


# ============================================================
# FrequencyEngine (End-to-End)
# ============================================================
class TestFrequencyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = FrequencyEngine()

    def test_e2e_with_records(self):
        report = self.engine.process(SAMPLE_RECORDS)
        self.assertEqual(report.summary["total_jobs"], 5)
        self.assertGreater(report.summary["unique_technologies"], 3)
        self.assertGreater(len(report.technologies), 3)
        self.assertGreater(len(report.categories), 1)
        self.assertGreater(len(report.statistics.top_technologies), 0)

    def test_e2e_with_dicts(self):
        report = self.engine.process(SAMPLE_DICTS)
        self.assertEqual(report.summary["total_jobs"], 2)
        self.assertGreater(report.summary["unique_technologies"], 2)

    def test_e2e_json_input(self):
        json_str = json.dumps(SAMPLE_DICTS)
        report = self.engine.analyze_json(json_str)
        self.assertEqual(report.summary["total_jobs"], 2)

    def test_empty_raises(self):
        with self.assertRaises(EmptyDatasetError):
            self.engine.process([])

    def test_duplicate_job_id_raises(self):
        dupes = [SAMPLE_RECORDS[0], SAMPLE_RECORDS[0]]
        with self.assertRaises(DuplicateJobError):
            self.engine.process(dupes)

    def test_invalid_json_raises(self):
        with self.assertRaises(InvalidInputError):
            self.engine.analyze_json("{ not json }")

    def test_non_array_json_raises(self):
        with self.assertRaises(InvalidInputError):
            self.engine.analyze_json('{"key": "val"}')

    def test_missing_job_id_raises(self):
        bad = [{"technologies": {"languages": ["Python"]}}]
        with self.assertRaises(MalformedRecordError):
            self.engine.process(bad)

    def test_export_report(self):
        self.engine.process([SAMPLE_DICTS[0]])
        temp_dir = tempfile.mkdtemp()
        try:
            from pathlib import Path
            path = Path(temp_dir) / "report.json"
            self.engine.export_report(path)
            self.assertTrue(path.exists())
        finally:
            import shutil
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main(verbosity=2)