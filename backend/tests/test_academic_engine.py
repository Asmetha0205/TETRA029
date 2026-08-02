"""
Unit and Integration Tests for Academic Intelligence Engine (Phase 4).
Tests PDF extraction, syllabus parsing, Bloom's Taxonomy classifier, and academic models.
"""

import time
import pytest
from backend.academic_engine.service.academic_service import AcademicService
from backend.academic_engine.models.academic_document import ParsedAcademicDocument, ParsedSection
from backend.academic_engine.utils.pdf_utils import extract_text_from_pdf


def get_unique_pdf_bytes():
    header = b"%PDF-1.5\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 55 >>\nstream\nBT /F1 12 Tf 100 700 Td (CS106B Data Structures Algorithms) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000216 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n320\n%%EOF"
    return header + f"\n% Unique tag {time.time()}".encode()


def test_pdf_utils_extract():
    full_text, pages, engine = extract_text_from_pdf(get_unique_pdf_bytes())
    assert full_text is not None
    assert engine is not None


def test_parsed_academic_document_model():
    doc = ParsedAcademicDocument(
        document_id="doc_test_101",
        university_name="Stanford University",
        academic_year="2025-2026",
        department="Computer Science",
        clean_text="CS106B Data Structures & Algorithms course text",
        sections=[
          ParsedSection(
              title="Course Syllabus",
              content="Data Structures, Recursion, Trees, Graphs",
              section_type="syllabus",
          )
        ],
    )
    assert doc.document_id == "doc_test_101"
    assert len(doc.sections) == 1
    assert doc.sections[0].title == "Course Syllabus"


def test_academic_service_pipeline():
    service = AcademicService()
    result = service.process_pipeline(
        file_bytes=get_unique_pdf_bytes(),
        filename="test_syllabus.pdf",
        university_name="Test University",
        curriculum_year="2025-2026",
        department="Computer Science",
    )
    
    assert result is not None
    assert "documents_processed" in result
    assert result["documents_processed"] == 1


def test_corrupted_pdf_validation_rejection():
    service = AcademicService()
    corrupt_bytes = b"INVALID_BYTE_STREAM_WITHOUT_PDF_HEADER"
    
    # Should catch invalid PDF signature
    with pytest.raises(Exception):
        service.process_pipeline(
            file_bytes=corrupt_bytes,
            filename="corrupt.pdf",
            university_name="Fallback Univ",
            curriculum_year="2025-2026",
            department="Computer Science",
        )
