"""
Coverage Rules Evaluator for Coverage Classification Module.
"""

import logging
from backend.semantic_engine.config.config import SemanticThresholdConfig
from backend.semantic_engine.models.semantic_models import CoverageClassificationEnum

logger = logging.getLogger("semantic_engine.classification.coverage_rules")


class CoverageRulesEvaluator:
    """Evaluates business rules for skill classification."""

    def __init__(self, thresholds: SemanticThresholdConfig) -> None:
        self.thresholds = thresholds

    def evaluate(self, academic_skill: str, industry_skill: str, similarity: float) -> CoverageClassificationEnum:
        """
        Evaluate classification using similarity score and exact name/alias matching rules.
        """
        clean_a = academic_skill.strip().lower()
        clean_i = industry_skill.strip().lower()

        # Rule 1: Exact string match -> Covered (1.0 similarity)
        if clean_a == clean_i:
            return CoverageClassificationEnum.COVERED

        # Rule 2: Numerical threshold classification
        if similarity >= self.thresholds.covered_threshold:
            return CoverageClassificationEnum.COVERED
        elif similarity >= self.thresholds.partial_threshold:
            return CoverageClassificationEnum.PARTIAL
        else:
            return CoverageClassificationEnum.GAP
