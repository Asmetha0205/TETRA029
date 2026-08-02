"""
Coverage Models for Coverage Classification Module.
"""

from typing import Dict, List
from pydantic import BaseModel, Field

from backend.semantic_engine.models.semantic_models import CoverageClassificationEnum, SkillMatchResult


class CoverageClassificationSummary(BaseModel):
    """Aggregate summary counts of skill coverage."""
    total_skills: int = 0
    covered_count: int = 0
    partial_count: int = 0
    gap_count: int = 0
    coverage_percentage: float = 0.0
    partial_percentage: float = 0.0
    gap_percentage: float = 0.0
