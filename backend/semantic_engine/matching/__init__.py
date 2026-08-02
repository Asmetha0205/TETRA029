"""
Semantic Matching Package for CurricuAlign AI Semantic Engine.
"""

from backend.semantic_engine.matching.candidate_selector import CandidateSelector
from backend.semantic_engine.matching.embedding_matcher import EmbeddingMatcher
from backend.semantic_engine.matching.exceptions import CandidateSelectionError, MatchingError, QueryBuildError
from backend.semantic_engine.matching.query_builder import MatchingQueryBuilder
from backend.semantic_engine.matching.semantic_matcher import SemanticMatcher

__all__ = [
    "SemanticMatcher",
    "CandidateSelector",
    "EmbeddingMatcher",
    "MatchingQueryBuilder",
    "MatchingError",
    "CandidateSelectionError",
    "QueryBuildError",
]
