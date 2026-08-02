"""
Statistics Engine for Semantic Intelligence Report.
"""

import logging
from typing import Any, Dict, List

from backend.semantic_engine.models.semantic_models import CoverageClassificationEnum, SkillMatchResult

logger = logging.getLogger("semantic_engine.report.statistics")


class SemanticStatisticsEngine:
    """Calculates coverage, gap, and partial percentage statistics."""

    @classmethod
    def compute_statistics(cls, match_results: List[SkillMatchResult]) -> Dict[str, Any]:
        """
        Compute statistics dictionary.

        Returns:
            Dict containing covered, partial, gap counts and percentage metrics.
        """
        total = len(match_results)
        if total == 0:
            return {"covered": 0, "partial": 0, "gap": 0, "total": 0}

        covered = sum(1 for item in match_results if item.classification == CoverageClassificationEnum.COVERED)
        partial = sum(1 for item in match_results if item.classification == CoverageClassificationEnum.PARTIAL)
        gap = sum(1 for item in match_results if item.classification == CoverageClassificationEnum.GAP)

        return {
            "covered": covered,
            "partial": partial,
            "gap": gap,
            "total": total,
            "covered_percentage": round((covered / total) * 100.0, 1),
            "partial_percentage": round((partial / total) * 100.0, 1),
            "gap_percentage": round((gap / total) * 100.0, 1),
        }
