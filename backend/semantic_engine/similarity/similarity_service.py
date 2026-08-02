"""
Similarity Service for CurricuAlign AI Semantic Intelligence Engine.
"""

import logging
from typing import List, Optional

from backend.semantic_engine.config.config import SemanticThresholdConfig
from backend.semantic_engine.models.semantic_models import CoverageClassificationEnum
from backend.semantic_engine.similarity.cosine_similarity import CosineSimilarityCalculator
from backend.semantic_engine.similarity.threshold_manager import ThresholdManager

logger = logging.getLogger("semantic_engine.similarity.similarity_service")


class SimilarityService:
    """Service facade for similarity calculation and classification."""

    def __init__(self, threshold_config: Optional[SemanticThresholdConfig] = None) -> None:
        self.threshold_manager = ThresholdManager(config=threshold_config)

    def calculate_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculate cosine similarity score between two vectors."""
        return CosineSimilarityCalculator.calculate(vec_a, vec_b)

    def classify_score(self, similarity: float) -> CoverageClassificationEnum:
        """Classify similarity score into Covered, Partial, or Gap."""
        return self.threshold_manager.classify_similarity(similarity)
