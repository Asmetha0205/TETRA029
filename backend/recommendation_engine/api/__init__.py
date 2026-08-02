"""
API package for Recommendation Intelligence Layer.
"""

from backend.recommendation_engine.api.schemas import GenerateRecommendationsApiRequest, ApiResponse
from backend.recommendation_engine.api.dependencies import get_graph_service, get_recommendation_service
from backend.recommendation_engine.api.controllers import RecommendationController
from backend.recommendation_engine.api.routes import router

__all__ = [
    "GenerateRecommendationsApiRequest",
    "ApiResponse",
    "get_graph_service",
    "get_recommendation_service",
    "RecommendationController",
    "router",
]
