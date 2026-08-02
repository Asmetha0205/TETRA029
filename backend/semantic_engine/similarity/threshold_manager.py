"""
Threshold Manager for Similarity Engine.

Manages configurable similarity thresholds for Covered, Partial, and Gap classification.
"""

import logging
from typing import Optional

from backend.semantic_engine.config.config import SemanticThresholdConfig
from backend.semantic_engine.models.semantic_models import CoverageClassificationEnum
from backend.semantic_engine.similarity.exceptions import InvalidThresholdError

logger = logging.getLogger("semantic_engine.similarity.threshold_manager")


class ThresholdManager:
    """Manages classification threshold rules."""

    def __init__(self, config: Optional[SemanticThresholdConfig] = None) -> None:
        self.config = config or SemanticThresholdConfig()
        self.validate()

    def validate(self) -> None:
        """Validate threshold parameters."""
        if not (0.0 <= self.config.partial_threshold <= self.config.covered_threshold <= 1.0):
            raise InvalidThresholdError(
                f"Invalid thresholds: partial ({self.config.partial_threshold}) "
                f"must be <= covered ({self.config.covered_threshold})."
            )

    def classify_similarity(self, similarity: float) -> CoverageClassificationEnum:
        """
        Classify similarity score into Covered, Partial, or Gap.

        Returns:
            CoverageClassificationEnum.
        """
        if similarity >= self.config.covered_threshold:
            return CoverageClassificationEnum.COVERED
        elif similarity >= self.config.partial_threshold:
            return CoverageClassificationEnum.PARTIAL
        else:
            return CoverageClassificationEnum.GAP
