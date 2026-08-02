"""
Document Upload Metadata Model for PDF Upload Module.
"""

import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class DocumentUploadMetadata(BaseModel):
    """
    Metadata associated with an uploaded curriculum PDF document.
    """
    document_id: str = Field(..., description="Unique document ID (e.g. 'doc-a1b2c3d4').")
    filename: str = Field(..., description="Original name of the uploaded file.")
    file_size_bytes: int = Field(..., ge=0, description="Size of file in bytes.")
    checksum: str = Field(..., description="SHA-256 checksum of the file content.")
    storage_path: str = Field(..., description="Absolute path on disk where file is stored.")
    university_name: str = Field(default="Unknown University")
    curriculum_year: str = Field(default="2025-2026")
    department: str = Field(default="Computer Science")
    upload_timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    status: str = Field(default="uploaded", description="'uploaded', 'parsed', or 'processed'.")
    metadata: Dict[str, Any] = Field(default_factory=dict)
