"""
Embedding Matcher for Semantic Matching Engine.
"""

import logging
from typing import List, Tuple

from backend.semantic_engine.utils.vector_utils import cosine_similarity

logger = logging.getLogger("semantic_engine.matching.embedding_matcher")


class EmbeddingMatcher:
    """Calculates exact vector similarity between numerical embeddings."""

    @classmethod
    def match_vectors(
        self,
        academic_vector: List[float],
        industry_vector: List[float],
    ) -> float:
        """
        Compute cosine similarity between two 384-d vectors.

        Returns:
            Cosine similarity score [0.0 - 1.0].
        """
        score = cosine_similarity(academic_vector, industry_vector)
        return max(0.0, score)
