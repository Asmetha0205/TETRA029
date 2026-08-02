"""
Coverage Classifier for CurricuAlign AI Semantic Engine.

Ensures every academic and industry technology receives a deterministic coverage classification.
"""

import logging
from typing import List, Optional

from backend.semantic_engine.config.config import SemanticEngineConfig
from backend.semantic_engine.classification.coverage_models import CoverageClassificationSummary
from backend.semantic_engine.classification.coverage_rules import CoverageRulesEvaluator
from backend.semantic_engine.models.semantic_models import CoverageClassificationEnum

logger = logging.getLogger("semantic_engine.classification.coverage_classifier")


class CoverageClassifier:
    """Classifies skill matches into Covered, Partial, or Gap."""

    def __init__(self, config: Optional[SemanticEngineConfig] = None) -> None:
        self.config = config or SemanticEngineConfig()
        self.evaluator = CoverageRulesEvaluator(self.config.thresholds)

    def classify_match(
        self, academic_skill: str, industry_skill: str, similarity: float
    ) -> CoverageClassificationEnum:
        """Classify a single skill match."""
        return self.evaluator.evaluate(academic_skill, industry_skill, similarity)

    def summarize_classifications(
        self, classifications: List[CoverageClassificationEnum]
    ) -> CoverageClassificationSummary:
        """Compute aggregate summary percentage breakdown."""
        total = len(classifications)
        if total == 0:
            return CoverageClassificationSummary()

        covered = sum(1 for c in classifications if c == CoverageClassificationEnum.COVERED)
        partial = sum(1 for c in classifications if c == CoverageClassificationEnum.PARTIAL)
        gap = sum(1 for c in classifications if c == CoverageClassificationEnum.GAP)

        return CoverageClassificationSummary(
            total_skills=total,
            covered_count=covered,
            partial_count=partial,
            gap_count=gap,
            coverage_percentage=round((covered / total) * 100.0, 1),
            partial_percentage=round((partial / total) * 100.0, 1),
            gap_percentage=round((gap / total) * 100.0, 1),
        )
