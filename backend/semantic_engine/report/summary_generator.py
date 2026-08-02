"""
Executive Summary Generator for Semantic Engine.
"""

from typing import Any, Dict, List
from backend.semantic_engine.models.semantic_models import SkillMatchResult


class ExecutiveSummaryGenerator:
    """Generates narrative executive summaries for alignment reports."""

    @classmethod
    def generate_summary(
        cls, alignment_score: float, stats: Dict[str, Any], match_results: List[SkillMatchResult]
    ) -> str:
        """Generate executive summary paragraph."""
        covered_pct = stats.get("covered_percentage", 0.0)
        gap_pct = stats.get("gap_percentage", 0.0)

        if alignment_score >= 85.0:
            status_desc = "excellent alignment with current industry market demand."
        elif alignment_score >= 70.0:
            status_desc = "strong baseline alignment, with targeted opportunities to address emerging tech gaps."
        else:
            status_desc = "significant skill gaps between academic offerings and industry demand."

        return (
            f"The evaluated curriculum demonstrates an overall Alignment Score of {alignment_score:.1f}/100, "
            f"reflecting {status_desc} A total of {stats.get('covered', 0)} skills ({covered_pct}%) are fully covered, "
            f"{stats.get('partial', 0)} skills are partially covered, and {stats.get('gap', 0)} skills ({gap_pct}%) represent gaps."
        )
