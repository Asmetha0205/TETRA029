"""
FastAPI Dependencies for Recommendation Intelligence Layer.
Provides singleton dependency providers for GraphService and RecommendationService.
"""

from typing import Generator, Optional
from backend.recommendation_engine.graph.graph_service import GraphService
from backend.recommendation_engine.service.recommendation_service import RecommendationService


# Global Service Singletons
_graph_service_instance: Optional[GraphService] = None
_recommendation_service_instance: Optional[RecommendationService] = None


def get_graph_service() -> GraphService:
    """Dependency provider for GraphService singleton."""
    global _graph_service_instance
    if _graph_service_instance is None:
        _graph_service_instance = GraphService()
    return _graph_service_instance


def get_recommendation_service() -> RecommendationService:
    """Dependency provider for RecommendationService singleton."""
    global _recommendation_service_instance
    if _recommendation_service_instance is None:
        graph_svc = get_graph_service()
        _recommendation_service_instance = RecommendationService(repository=graph_svc.repo)
    return _recommendation_service_instance
