"""
API Schemas for Semantic REST API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CompareRequestPayload(BaseModel):
    """Optional request payload for curriculum comparison."""
    university_name: Optional[str] = Field(default=None)
    department: Optional[str] = Field(default=None)


class SkillMatchResponseItem(BaseModel):
    """Schema for single skill comparison result item."""
    academic_skill: Optional[str] = None
    industry_skill: str
    similarity: float
    priority: Optional[str] = None
    industry_score: float = 0.0
    category: str = "General"
    evidence: Optional[str] = None


class ComparisonReportResponse(BaseModel):
    """Schema for full Semantic Comparison Report output."""
    alignment_score: float
    statistics: Dict[str, int]
    covered: List[SkillMatchResponseItem] = Field(default_factory=list)
    partial: List[SkillMatchResponseItem] = Field(default_factory=list)
    gap: List[SkillMatchResponseItem] = Field(default_factory=list)
    visualization_data: Dict[str, Any] = Field(default_factory=dict)
