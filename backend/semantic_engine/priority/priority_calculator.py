"""
Priority Calculator for Priority Engine.

Calculates numeric priority score and determines GapPriorityEnum level.
"""

import logging
from typing import Any, Dict

from backend.semantic_engine.models.semantic_models import GapPriorityEnum
from backend.semantic_engine.priority.priority_models import PriorityScoreBreakdown

logger = logging.getLogger("semantic_engine.priority.priority_calculator")


class PriorityCalculator:
    """Calculates gap priority urgency levels."""

    @classmethod
    def calculate_priority(
        cls,
        industry_score: float = 0.0,
        demand_score: float = 0.0,
        similarity: float = 0.0,
        trend: str = "Stable",
        classification: str = "Supporting Technology",
    ) -> PriorityScoreBreakdown:
        """
        Calculate numerical priority score and assign Critical, High, Medium, or Low level.

        Returns:
            PriorityScoreBreakdown model.
        """
        ind_weight = round(industry_score * 0.45, 2)
        dem_weight = round(demand_score * 0.35, 2)
        gap_severity = round((1.0 - similarity) * 20.0, 2)

        # Trend boost
        trend_lower = trend.lower()
        if "rising" in trend_lower or "explosive" in trend_lower:
            trend_boost = 10.0
        elif "emerging" in trend_lower:
            trend_boost = 5.0
        else:
            trend_boost = 0.0

        final_score = round(ind_weight + dem_weight + gap_severity + trend_boost, 2)

        # Priority level assignment
        if final_score >= 80.0 or (industry_score >= 85.0 and similarity < 0.30):
            priority = GapPriorityEnum.CRITICAL
        elif final_score >= 65.0:
            priority = GapPriorityEnum.HIGH
        elif final_score >= 45.0:
            priority = GapPriorityEnum.MEDIUM
        else:
            priority = GapPriorityEnum.LOW

        return PriorityScoreBreakdown(
            industry_demand_weight=dem_weight,
            industry_score_weight=ind_weight,
            trend_boost=trend_boost,
            gap_severity_weight=gap_severity,
            final_score=final_score,
            priority=priority,
        )
