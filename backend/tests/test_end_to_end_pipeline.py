"""
End-to-End Orchestration Pipeline Test (Phase 7 & Phase 9 Validation).
Executes single-call end-to-end curriculum analysis from PDF bytes ingestion to recommendation graph generation.
"""

import time
import pytest
from backend.orchestrator.analysis_orchestrator import AnalysisOrchestrator

BASE_PDF_HEADER = b"%PDF-1.5\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 55 >>\nstream\nBT /F1 12 Tf 100 700 Td (CS106B CS110 CS229 Data Structures OS ML) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000216 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n320\n%%EOF"


def test_end_to_end_curriculum_analysis():
    orchestrator = AnalysisOrchestrator()
    unique_pdf = BASE_PDF_HEADER + f"\n% Unique test tag {time.time()}".encode()

    result = orchestrator.analyze_curriculum(
        file_bytes=unique_pdf,
        filename="stanford_cs_syllabus_e2e.pdf",
        university_name="Stanford University",
        curriculum_year="2025-2026",
        department="Computer Science",
    )

    assert result is not None
    assert "analysis_id" in result
    assert "alignment_score" in result
    assert result["alignment_score"] >= 0.0
    assert "recommendations" in result
    assert "learning_paths" in result
    assert result["execution_time"] >= 0.0


def test_orchestrator_cache_retrieval():
    orchestrator = AnalysisOrchestrator()
    unique_pdf = BASE_PDF_HEADER + f"\n% Unique cache tag {time.time()}".encode()

    result1 = orchestrator.analyze_curriculum(
        file_bytes=unique_pdf,
        filename="cache_test.pdf",
        university_name="Cache University",
        curriculum_year="2025-2026",
        department="Computer Science",
    )

    analysis_id = result1["analysis_id"]
    cached_result = orchestrator.get_analysis_result(analysis_id)
    assert cached_result is not None
    assert cached_result["analysis_id"] == analysis_id
