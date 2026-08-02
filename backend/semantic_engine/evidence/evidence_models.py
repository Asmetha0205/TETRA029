"""
Evidence Models for Evidence Engine.
"""

from typing import Optional
from pydantic import BaseModel, Field


class DetailedEvidence(BaseModel):
    """Detailed evidence supporting a skill gap or match statement."""
    summary: str
    job_mention_percentage: float = 0.0
    curriculum_status: str = ""
    rationale: str = ""
    academic_skill: Optional[str] = None
    industry_skill: str = ""
    similarity: float = 0.0
