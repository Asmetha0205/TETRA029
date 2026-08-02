"""
Industry Engine Gateway.
Provides unified interface to Industry Intelligence Engine.
"""

from typing import Any, Dict, List, Optional
from backend.industry_engine.service.industry_service import IndustryService
from backend.industry_engine.knowledge.knowledge_models import TechnologyKnowledgeRecord
from backend.gateway.engine_gateway import BaseEngineGateway
from backend.utils.logger import get_logger

logger = get_logger("gateway.industry")


class IndustryGateway(BaseEngineGateway):
    """Unified Gateway for Industry Intelligence Engine."""

    def __init__(self, industry_service: Optional[IndustryService] = None):
        self.service = industry_service or IndustryService(force_fallback_embeddings=True)
        logger.info("[IndustryGateway] Initialized IndustryGateway.")

    def get_engine_name(self) -> str:
        return "Industry Intelligence Engine"

    def get_all_technologies(self) -> List[TechnologyKnowledgeRecord]:
        """Retrieve all industry technology records."""
        return self.service.get_all_technologies()

    def search_similar(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search similar industry technologies."""
        results = self.service.search_similar(query=query, limit=limit)
        return [r.model_dump() for r in results]

    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics for Industry Knowledge."""
        return self.service.knowledge_service.get_statistics().model_dump()

    def check_health(self) -> Dict[str, Any]:
        """Check Industry Engine health."""
        try:
            health = self.service.health()
            return health.model_dump()
        except Exception as e:
            logger.error("[IndustryGateway] Health check failed: %s", e)
            return {"status": "unhealthy", "error": str(e)}
