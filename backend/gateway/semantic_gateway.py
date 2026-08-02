"""
Semantic Engine Gateway.
Provides unified interface to Semantic Intelligence Engine.
"""

from typing import Any, Dict, List, Optional
from backend.semantic_engine.service.semantic_service import SemanticService
from backend.semantic_engine.models.semantic_models import SemanticComparisonReport
from backend.academic_engine.knowledge.academic_models import AcademicTechnologyRecord
from backend.gateway.engine_gateway import BaseEngineGateway
from backend.utils.logger import get_logger

logger = get_logger("gateway.semantic")


class SemanticGateway(BaseEngineGateway):
    """Unified Gateway for Semantic Intelligence Engine."""

    def __init__(self, semantic_service: Optional[SemanticService] = None):
        self.service = semantic_service or SemanticService()
        logger.info("[SemanticGateway] Initialized SemanticGateway.")

    def get_engine_name(self) -> str:
        return "Semantic Intelligence Engine"

    def compare_curriculum(
        self, academic_records: Optional[List[AcademicTechnologyRecord]] = None
    ) -> SemanticComparisonReport:
        """Run semantic matching and gap analysis."""
        logger.info("[SemanticGateway] Running curriculum comparison.")
        return self.service.compare_curriculum(academic_records=academic_records)

    def check_health(self) -> Dict[str, Any]:
        """Check Semantic Engine health."""
        try:
            health = self.service.health()
            return health.model_dump()
        except Exception as e:
            logger.error("[SemanticGateway] Health check failed: %s", e)
            return {"status": "unhealthy", "error": str(e)}
