"""
Core Data Models for CurricuAlign AI Semantic Intelligence Engine.
"""

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CoverageClassificationEnum(str, Enum):
    """Classification of skill coverage status."""
    COVERED = "Covered"
    PARTIAL = "Partial"
    GAP = "Gap"


class GapPriorityEnum(str, Enum):
    """Priority urgency level for curriculum gaps."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class CandidateMatch(BaseModel):
    """Candidate match retrieved between academic and industry technology."""
    academic_skill: str
    industry_skill: str
    industry_technology_id: str
    similarity_score: float = Field(..., ge=-1.0, le=1.0)
    category: str = Field(default="Unknown")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidenceItem(BaseModel):
    """Supporting evidence backing up a skill match/gap result."""
    summary: str
    job_mention_percentage: float = 0.0
    curriculum_status: str = ""
    rationale: str = ""


class SkillMatchResult(BaseModel):
    """Detailed skill comparison result item."""
    academic_skill: Optional[str] = Field(default=None)
    industry_skill: str
    industry_technology_id: str = ""
    category: str = "General"
    similarity: float = Field(..., ge=0.0, le=1.0)
    classification: CoverageClassificationEnum
    priority: GapPriorityEnum = GapPriorityEnum.LOW
    industry_score: float = 0.0
    demand_score: float = 0.0
    evidence: EvidenceItem = Field(default_factory=lambda: EvidenceItem(summary=""))


class CategoryAlignment(BaseModel):
    """Alignment score breakdown for a specific category."""
    category_name: str
    alignment_score: float = Field(..., ge=0.0, le=100.0)
    covered_count: int = 0
    partial_count: int = 0
    gap_count: int = 0


class SemanticComparisonReport(BaseModel):
    """
    Complete Semantic Comparison Report output for Curriculum Alignment.
    """
    alignment_score: float = Field(..., ge=0.0, le=100.0, description="Overall Curriculum Alignment Score (0-100)")
    statistics: Dict[str, int] = Field(..., description="Counts of covered, partial, gap skills")
    covered: List[Dict[str, Any]] = Field(default_factory=list)
    partial: List[Dict[str, Any]] = Field(default_factory=list)
    gap: List[Dict[str, Any]] = Field(default_factory=list)
    category_alignment: Dict[str, CategoryAlignment] = Field(default_factory=dict)
    visualization_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
