"""
Cosine Similarity Calculator for Similarity Engine.
"""

from typing import List
from backend.semantic_engine.utils.vector_utils import cosine_similarity


class CosineSimilarityCalculator:
    """Calculates cosine similarity between vectors."""

    @classmethod
    def calculate(cls, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Calculate cosine similarity between vec_a and vec_b.

        Returns:
            Cosine similarity score [0.0 - 1.0].
        """
        return max(0.0, cosine_similarity(vec_a, vec_b))
