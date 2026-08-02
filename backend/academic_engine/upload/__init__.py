"""
PDF Upload Package for CurricuAlign AI Academic Engine.
"""

from backend.academic_engine.upload.exceptions import DuplicateDocumentError, FileTooLargeError, InvalidPDFError, UploadError
from backend.academic_engine.upload.file_manager import FileManager
from backend.academic_engine.upload.metadata import DocumentUploadMetadata
from backend.academic_engine.upload.upload_service import UploadService
from backend.academic_engine.upload.validators import UploadValidator

__all__ = [
    "UploadService",
    "FileManager",
    "UploadValidator",
    "DocumentUploadMetadata",
    "UploadError",
    "InvalidPDFError",
    "FileTooLargeError",
    "DuplicateDocumentError",
]
