"""
Job Data Model for CurricuAlign AI Industry Intelligence Engine.
"""

import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class Job(BaseModel):
    """
    Standardized Job Posting representation across all data fetcher plugins.
    """
    job_id: str = Field(..., description="Unique identifier for the job posting from the source.")
    title: str = Field(..., description="Title of the job position.")
    company: Optional[str] = Field(default="Unknown", description="Hiring company or organization.")
    location: Optional[str] = Field(default="Remote / Unspecified", description="Job location or work model.")
    description: str = Field(..., description="Full text description of the job posting.")
    source: str = Field(..., description="Identifier of the source plugin that fetched this job.")
    url: Optional[str] = Field(default="", description="Direct URL link to the job posting.")
    posted_date: Optional[str] = Field(default_factory=lambda: datetime.date.today().isoformat(), description="ISO date when the job was posted.")
    fetch_timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(), description="ISO timestamp when the job was fetched.")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Original unparsed dictionary payload from the source.")

    @field_validator("job_id", "title", "description")
    @classmethod
    def validate_non_empty_strings(cls, value: str, info) -> str:
        """
        Validates that critical string fields are not empty or blank.
        """
        if not value or not value.strip():
            raise ValueError(f"Field '{info.field_name}' must be a non-empty string.")
        return value.strip()

    class Config:
        frozen = False
        json_schema_extra = {
            "example": {
                "job_id": "api_job_10293",
                "title": "Senior AI Infrastructure Engineer",
                "company": "TechCorp Solutions",
                "location": "San Francisco, CA",
                "description": "Looking for an engineer proficient in Python, FastAPI, vLLM, Docker, and Kubernetes.",
                "source": "api",
                "url": "https://example.com/jobs/10293",
                "posted_date": "2026-08-01",
                "fetch_timestamp": "2026-08-01T19:21:00Z",
                "raw_data": {"id": 10293, "raw_title": "Senior AI Infra Eng"}
            }
        }
