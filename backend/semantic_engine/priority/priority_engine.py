"""
Priority Engine for CurricuAlign AI Semantic Intelligence Engine.
"""

import logging
from typing import List, Optional

from backend.semantic_engine.models.semantic_models import GapPriorityEnum, SkillMatchResult
from backend.semantic_engine.priority.priority_calculator import PriorityCalculator

logger = logging.getLogger("semantic_engine.priority.priority_engine")


class PriorityEngine:
    """Main Priority Engine calculating gap priority levels."""

    def assign_priorities(self, match_results: List[SkillMatchResult]) -> List[SkillMatchResult]:
        """
        Evaluate and assign priority level for every skill match item.

        Returns:
            List of SkillMatchResult objects with assigned priorities.
        """
        for item in match_results:
            breakdown = PriorityCalculator.calculate_priority(
                industry_score=item.industry_score,
                demand_score=item.demand_score,
                similarity=item.similarity,
            )
            item.priority = breakdown.priority

        logger.info("[Priority] Assigned priorities for %d skill match results.", len(match_results))
        return match_results
