"""
Priority Models for Priority Engine.
"""

from typing import Dict
from pydantic import BaseModel, Field

from backend.semantic_engine.models.semantic_models import GapPriorityEnum


class PriorityScoreBreakdown(BaseModel):
    """Detailed breakdown of priority calculation components."""
    industry_demand_weight: float = 0.0
    industry_score_weight: float = 0.0
    trend_boost: float = 0.0
    gap_severity_weight: float = 0.0
    final_score: float = 0.0
    priority: GapPriorityEnum = GapPriorityEnum.LOW
