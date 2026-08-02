"""
Recommendation Intelligence Layer (Phase 6) for CurricuAlign AI.
Transforms GapAnalysisResult into explainable, evidence-backed curriculum recommendations.
"""

from backend.recommendation_engine.service.recommendation_service import RecommendationService
from backend.recommendation_engine.graph.graph_service import GraphService

__all__ = [
    "RecommendationService",
    "GraphService",
]
