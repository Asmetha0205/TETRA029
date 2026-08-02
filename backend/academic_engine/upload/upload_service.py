"""
PDF Upload Service for CurricuAlign AI Academic Engine.

Orchestrates file size/signature validation, file manager storage,
checksum generation, and document metadata cataloging.
"""

import logging
from typing import List, Optional

from backend.academic_engine.config.config import AcademicEngineConfig
from backend.academic_engine.upload.file_manager import FileManager
from backend.academic_engine.upload.metadata import DocumentUploadMetadata
from backend.academic_engine.upload.validators import UploadValidator

logger = logging.getLogger("academic_engine.upload.upload_service")


class UploadService:
    """
    Public Service facade for uploading and validating curriculum PDF documents.
    """

    def __init__(
        self,
        config: Optional[AcademicEngineConfig] = None,
        file_manager: Optional[FileManager] = None,
    ) -> None:
        self.config = config or AcademicEngineConfig()
        self.validator = UploadValidator(config=self.config)
        self.file_manager = file_manager or FileManager(config=self.config)

    def upload_pdf(
        self,
        file_bytes: bytes,
        filename: str,
        university_name: str = "Unknown University",
        curriculum_year: str = "2025-2026",
        department: str = "Computer Science",
    ) -> DocumentUploadMetadata:
        """
        Validate and upload a curriculum PDF file.

        Args:
            file_bytes: Raw bytes of the uploaded PDF file.
            filename: Original file name.
            university_name: University name tag.
            curriculum_year: Academic year tag.
            department: Department tag.

        Returns:
            DocumentUploadMetadata model describing the stored file.
        """
        # Step 1: Validate
        self.validator.validate_file_size(file_bytes)
        self.validator.validate_pdf_content(file_bytes, filename=filename)

        # Step 2: Save & Catalog
        meta = self.file_manager.save_pdf(
            file_bytes=file_bytes,
            filename=filename,
            university_name=university_name,
            curriculum_year=curriculum_year,
            department=department,
        )

        return meta

    def get_document(self, document_id: str) -> Optional[DocumentUploadMetadata]:
        """Retrieve document metadata by ID."""
        return self.file_manager.get_metadata(document_id)

    def list_documents(self) -> List[DocumentUploadMetadata]:
        """List all uploaded curriculum documents."""
        return self.file_manager.list_documents()
