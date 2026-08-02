"""
Vector Utilities for CurricuAlign AI Semantic Intelligence Engine.
"""

import math
from typing import List


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calculate Cosine Similarity between two numerical vectors.

    Returns:
        Float similarity score in [-1.0, 1.0], rounded to 4 decimals.
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    sim = max(-1.0, min(1.0, dot_product / (norm_a * norm_b)))
    return round(sim, 4)


def l2_normalize(vector: List[float]) -> List[float]:
    """L2 normalize a vector to unit length."""
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0.0:
        return vector
    return [x / norm for x in vector]
