"""
FastAPI Dependencies for Semantic REST API.
"""

import logging
from typing import Optional

from backend.semantic_engine.service.semantic_service import SemanticService

logger = logging.getLogger("semantic_engine.api.dependencies")

_service_instance: Optional[SemanticService] = None


def get_semantic_service() -> SemanticService:
    """FastAPI dependency returning singleton SemanticService instance."""
    global _service_instance
    if _service_instance is None:
        logger.info("[API] Initializing SemanticService singleton for dependency injection.")
        _service_instance = SemanticService()
    return _service_instance


def set_semantic_service_instance(instance: SemanticService) -> None:
    """Override singleton instance."""
    global _service_instance
    _service_instance = instance
