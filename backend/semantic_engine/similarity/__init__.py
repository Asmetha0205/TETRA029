"""
Similarity Package for CurricuAlign AI Semantic Engine.
"""

from backend.semantic_engine.similarity.cosine_similarity import CosineSimilarityCalculator
from backend.semantic_engine.similarity.exceptions import InvalidThresholdError, SimilarityError
from backend.semantic_engine.similarity.similarity_service import SimilarityService
from backend.semantic_engine.similarity.threshold_manager import ThresholdManager

__all__ = [
    "SimilarityService",
    "CosineSimilarityCalculator",
    "ThresholdManager",
    "SimilarityError",
    "InvalidThresholdError",
]
