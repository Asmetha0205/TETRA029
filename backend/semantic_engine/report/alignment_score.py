"""
Alignment Score Calculator for CurricuAlign AI Semantic Engine.

Computes Overall Curriculum Alignment Score (0-100) and Category-level Alignment.
"""

import logging
from typing import Dict, List

from backend.semantic_engine.config.config import SemanticEngineConfig
from backend.semantic_engine.models.semantic_models import CategoryAlignment, CoverageClassificationEnum, SkillMatchResult

logger = logging.getLogger("semantic_engine.report.alignment_score")


class AlignmentScoreCalculator:
    """Calculates overall and category-level curriculum alignment scores."""

    def __init__(self, config: SemanticEngineConfig) -> None:
        self.config = config

    def calculate_overall_alignment(self, match_results: List[SkillMatchResult]) -> float:
        """
        Calculate weighted Overall Curriculum Alignment Score (0.0 to 100.0).

        Returns:
            Float alignment score rounded to 1 decimal place.
        """
        if not match_results:
            return 0.0

        total_weight = 0.0
        weighted_score = 0.0

        for item in match_results:
            category = item.category or "General"
            cat_weight = self.config.category_weights.get(category, 1.0)
            ind_importance = max(1.0, item.industry_score / 20.0)
            combined_weight = cat_weight * ind_importance

            if item.classification == CoverageClassificationEnum.COVERED:
                item_score = 100.0 * item.similarity
            elif item.classification == CoverageClassificationEnum.PARTIAL:
                item_score = 65.0 * item.similarity
            else:
                item_score = 0.0

            weighted_score += item_score * combined_weight
            total_weight += combined_weight

        if total_weight == 0.0:
            return 0.0

        raw_score = weighted_score / total_weight
        final_score = round(max(0.0, min(100.0, raw_score)), 1)
        logger.info("[Report] Overall Curriculum Alignment Score: %.1f", final_score)
        return final_score

    def calculate_category_alignments(
        self, match_results: List[SkillMatchResult]
    ) -> Dict[str, CategoryAlignment]:
        """
        Calculate alignment score breakdown per category.

        Returns:
            Dict mapping category_name to CategoryAlignment models.
        """
        categories: Dict[str, List[SkillMatchResult]] = {}
        for item in match_results:
            cat = item.category or "General"
            categories.setdefault(cat, []).append(item)

        category_alignments: Dict[str, CategoryAlignment] = {}
        for cat_name, items in categories.items():
            cat_score = self.calculate_overall_alignment(items)
            cov_c = sum(1 for i in items if i.classification == CoverageClassificationEnum.COVERED)
            part_c = sum(1 for i in items if i.classification == CoverageClassificationEnum.PARTIAL)
            gap_c = sum(1 for i in items if i.classification == CoverageClassificationEnum.GAP)

            category_alignments[cat_name] = CategoryAlignment(
                category_name=cat_name,
                alignment_score=cat_score,
                covered_count=cov_c,
                partial_count=part_c,
                gap_count=gap_c,
            )

        return category_alignments
