"""
End-to-End Integration Test Suite for Academic Intelligence Engine (Phase 4).

Verifies the complete pipeline flow:
PDF Upload -> Validation -> Store -> Parse -> Clean -> Extract -> Normalize -> Knowledge Builder -> Repository -> Snapshot -> REST API -> Health.
"""

import tempfile
import unittest
from pathlib import Path

from backend.academic_engine.config.config import AcademicEngineConfig
from backend.academic_engine.service.academic_service import AcademicService
from backend.academic_engine.api.controllers import AcademicController


class TestAcademicEngineEndToEnd(unittest.TestCase):
    """End-to-End verification test suite for the Academic Engine."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.config = AcademicEngineConfig(
            upload_dir=str(Path(self.tmp_dir.name) / "uploads"),
            repository_path=str(Path(self.tmp_dir.name) / "academic_repo.json"),
            snapshot_path=str(Path(self.tmp_dir.name) / "academic_snapshots.json"),
            document_catalog_path=str(Path(self.tmp_dir.name) / "doc_catalog.json"),
            force_offline_extraction=True,
        )
        self.service = AcademicService(config=self.config)
        self.controller = AcademicController(self.service)

        self.sample_pdf_text = """
        Stanford University
        Department of Computer Science
        B.Tech Computer Science Curriculum 2025-2026

        CS101: Data Structures and Machine Learning Systems
        Credits: 4.0
        Semester 1

        Course Overview
        Students will build high-performance data systems using Python, C++, PyTorch, Docker, PostgreSQL, and Kubernetes on AWS.

        Learning Outcomes
        - Design scalable machine learning models with PyTorch.
        - Deploy microservices using Docker, Kubernetes, and FastAPI.
        """
        # Create minimal PDF bytes containing readable text stream
        self.pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Length 200 >>\nstream\nBT\n" + self.sample_pdf_text.encode("utf-8") + b"\nET\nendstream\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_full_academic_pipeline_and_apis(self):
        # 1. Health Check
        health = self.service.health()
        self.assertEqual(health.status, "healthy")

        # 2. Execute End-to-End Processing Pipeline
        summary = self.service.process_pipeline(
            file_bytes=self.pdf_bytes,
            filename="stanford_cs_curriculum.pdf",
            university_name="Stanford University",
            department="Computer Science",
        )

        # Validate strict Summary Output format
        self.assertEqual(summary["documents_processed"], 1)
        self.assertTrue(summary["courses_detected"] >= 1)
        self.assertTrue(summary["technologies_extracted"] > 0)
        self.assertTrue(summary["normalized"] > 0)
        self.assertTrue(summary["snapshot_created"])
        self.assertIn("execution_time", summary)

        # 3. Verify Knowledge Layer Content
        records = self.service.get_all_technologies()
        self.assertTrue(len(records) > 0)
        tech_ids = [r.technology_id for r in records]
        self.assertIn("python", tech_ids)
        self.assertIn("pytorch", tech_ids)
        self.assertIn("docker", tech_ids)

        # 4. REST API Controller Methods
        doc_list_res = self.controller.list_documents()
        self.assertEqual(doc_list_res.total, 1)

        course_list_res = self.controller.list_courses()
        self.assertTrue(course_list_res.total >= 1)

        search_res = self.controller.search_technologies("python")
        self.assertTrue(search_res.total >= 1)

        stats_res = self.controller.get_statistics()
        self.assertTrue(stats_res["total_technologies"] > 0)


if __name__ == "__main__":
    unittest.main()
