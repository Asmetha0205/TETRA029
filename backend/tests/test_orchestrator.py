"""
Integration tests for Analysis Orchestrator.
"""

import unittest
import fitz  # PyMuPDF
from backend.orchestrator.analysis_orchestrator import AnalysisOrchestrator


def create_sample_pdf_bytes() -> bytes:
    """Helper to generate a valid PDF byte stream with curriculum text."""
    doc = fitz.open()
    page = doc.new_page()
    content = (
        "Computer Science Curriculum Syllabus\n"
        "Course Code: CS101\n"
        "Title: Introduction to Computer Science & Software Engineering\n"
        "Topics Covered: Python programming, Object-Oriented Design, Data Structures, "
        "PostgreSQL Databases, Machine Learning fundamentals, Docker containerization, "
        "and Web Development with FastAPI.\n"
    )
    page.insert_text((50, 50), content)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


class TestAnalysisOrchestrator(unittest.TestCase):

    def test_full_pipeline_orchestration(self):
        orchestrator = AnalysisOrchestrator()
        sample_pdf_bytes = create_sample_pdf_bytes()

        result = orchestrator.analyze_curriculum(
            file_bytes=sample_pdf_bytes,
            filename="syllabus.pdf",
            university_name="Stanford University",
            curriculum_year="2025-2026",
            department="Computer Science",
        )

        self.assertIn("analysis_id", result)
        self.assertIn("alignment_score", result)
        self.assertIn("covered_skills", result)
        self.assertIn("partial_skills", result)
        self.assertIn("gap_skills", result)
        self.assertIn("recommendations", result)
        self.assertIn("learning_paths", result)
        self.assertIn("processing_metrics", result)
        self.assertGreater(result["execution_time"], 0.0)


if __name__ == "__main__":
    unittest.main()
