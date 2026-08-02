"""
Configuration Settings for the CurricuAlign AI Academic Intelligence Engine.
"""

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class AcademicEngineConfig(BaseModel):
    """Configuration parameters for the Academic Engine."""

    # File Upload settings
    upload_dir: str = Field(default="data/academic_uploads")
    max_file_size_bytes: int = Field(default=52428800)  # 50 MB
    allowed_extensions: List[str] = Field(default_factory=lambda: [".pdf"])
    allowed_mime_types: List[str] = Field(default_factory=lambda: ["application/pdf"])

    # Persistence settings
    repository_path: str = Field(default="data/academic_repository.json")
    snapshot_path: str = Field(default="data/academic_snapshots.json")
    document_catalog_path: str = Field(default="data/academic_documents.json")

    # LLM Extraction settings
    gemini_model_name: str = Field(default="gemini-1.5-flash")
    gemini_api_key: Optional[str] = Field(default=None)
    force_offline_extraction: bool = Field(default=False)

    # Parsing settings
    min_text_length: int = Field(default=20)
