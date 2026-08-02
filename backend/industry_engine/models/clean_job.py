"""
CleanJob Data Model for CurricuAlign AI Industry Engine Preprocessing.
"""

import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CleanJob(BaseModel):
    """
    Standardized Cleaned Job Posting ready for AI Skill Extraction.
    """
    job_id: str = Field(..., description="Unique identifier for the job posting.")
    title: str = Field(..., description="Normalized job position title.")
    company: str = Field(default="Unknown", description="Hiring organization.")
    location: str = Field(default="Remote / Unspecified", description="Job location.")
    clean_description: str = Field(..., description="Sanitized, normalized, English job description text.")
    source: str = Field(..., description="Origin job fetcher source identifier.")
    url: Optional[str] = Field(default="", description="Source link URL.")
    posted_date: Optional[str] = Field(default="", description="Original posting date.")
    processing_timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="ISO timestamp when preprocessing was completed."
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata audit trail (char counts, language, hashes).")

    class Config:
        frozen = False
