"""
Unit tests for PDF Upload Module.
"""

import tempfile
import unittest
from pathlib import Path

from backend.academic_engine.config.config import AcademicEngineConfig
from backend.academic_engine.upload import (
    DuplicateDocumentError,
    FileManager,
    InvalidPDFError,
    UploadService,
    UploadValidator,
)


class TestPDFUploadModule(unittest.TestCase):
    """Test suite for UploadValidator, FileManager, and UploadService."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.config = AcademicEngineConfig(
            upload_dir=str(Path(self.tmp_dir.name) / "uploads"),
            document_catalog_path=str(Path(self.tmp_dir.name) / "catalog.json"),
        )
        self.service = UploadService(config=self.config)
        self.valid_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Title (Test Curriculum) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_upload_valid_pdf(self):
        meta = self.service.upload_pdf(
            file_bytes=self.valid_pdf_bytes,
            filename="syllabus.pdf",
            university_name="Stanford University",
        )
        self.assertIsNotNone(meta.document_id)
        self.assertEqual(meta.university_name, "Stanford University")
        self.assertTrue(Path(meta.storage_path).exists())

    def test_upload_invalid_header_fails(self):
        invalid_bytes = b"NOT_A_PDF_FILE_HEADER"
        with self.assertRaises(InvalidPDFError):
            self.service.upload_pdf(file_bytes=invalid_bytes, filename="fake.pdf")

    def test_duplicate_upload_raises_error(self):
        self.service.upload_pdf(file_bytes=self.valid_pdf_bytes, filename="doc1.pdf")
        with self.assertRaises(DuplicateDocumentError):
            self.service.upload_pdf(file_bytes=self.valid_pdf_bytes, filename="doc2.pdf")


if __name__ == "__main__":
    unittest.main()
