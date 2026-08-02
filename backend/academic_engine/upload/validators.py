"""
Upload Validators for PDF Upload Module.
"""

from pathlib import Path
from typing import Optional, Union

from backend.academic_engine.config.config import AcademicEngineConfig
from backend.academic_engine.upload.exceptions import FileTooLargeError, InvalidPDFError


class UploadValidator:
    """Validates PDF files for size, file extension, and magic header signatures."""

    def __init__(self, config: Optional[AcademicEngineConfig] = None) -> None:
        self.config = config or AcademicEngineConfig()

    def validate_file_size(self, file_bytes: bytes) -> None:
        """Validate file size does not exceed max limit."""
        size = len(file_bytes)
        if size == 0:
            raise InvalidPDFError("Uploaded file is empty (0 bytes).")
        if size > self.config.max_file_size_bytes:
            raise FileTooLargeError(
                f"File size {size} bytes exceeds maximum limit of {self.config.max_file_size_bytes} bytes."
            )

    def validate_pdf_content(self, file_bytes: bytes, filename: str = "") -> None:
        """Validate filename extension and %PDF- header magic bytes."""
        if filename:
            ext = Path(filename).suffix.lower()
            if ext not in self.config.allowed_extensions:
                raise InvalidPDFError(f"Invalid file extension '{ext}'. Allowed: {self.config.allowed_extensions}")

        # Magic bytes check for PDF (%PDF-)
        if not file_bytes.startswith(b"%PDF-"):
            raise InvalidPDFError("File content signature is invalid. File is not a valid PDF document.")
