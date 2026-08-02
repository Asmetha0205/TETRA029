"""
Recommendation Engine Gateway.
Provides unified interface to Recommendation Intelligence Layer.
"""

from typing import Any, Dict, List, Optional
from backend.recommendation_engine.service.recommendation_service import RecommendationService
from backend.recommendation_engine.service.service_models import (
    GenerateRecommendationsRequest,
    ServiceExecutionResponse,
)
from backend.gateway.engine_gateway import BaseEngineGateway
from backend.utils.logger import get_logger

logger = get_logger("gateway.recommendation")


class RecommendationGateway(BaseEngineGateway):
    """Unified Gateway for Recommendation Intelligence Layer."""

    def __init__(self, recommendation_service: Optional[RecommendationService] = None):
        self.service = recommendation_service or RecommendationService()
        logger.info("[RecommendationGateway] Initialized RecommendationGateway.")

    def get_engine_name(self) -> str:
        return "Recommendation Intelligence Layer"

    def generate_recommendations(
        self,
        gap_analysis_data: Dict[str, Any],
        target_gaps: Optional[List[str]] = None,
        knowledge_context: Optional[Dict[str, Any]] = None,
    ) -> ServiceExecutionResponse:
        """Generate AI recommendations, learning path, and executive report."""
        logger.info("[RecommendationGateway] Generating recommendations.")
        request = GenerateRecommendationsRequest(
            gap_analysis_data=gap_analysis_data,
            target_gaps=target_gaps,
            knowledge_context=knowledge_context,
        )
        return self.service.generate_recommendations(request)

    def check_health(self) -> Dict[str, Any]:
        """Check Recommendation Engine & Neo4j Graph health."""
        try:
            is_fallback = self.service.repo.is_using_memory_fallback()
            return {
                "status": "healthy" if not is_fallback else "degraded",
                "neo4j": "connected" if not is_fallback else "in-memory fallback",
            }
        except Exception as e:
            logger.error("[RecommendationGateway] Health check failed: %s", e)
            return {"status": "unhealthy", "error": str(e)}
