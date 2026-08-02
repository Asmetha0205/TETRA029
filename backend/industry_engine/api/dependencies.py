"""
FastAPI Dependencies for Industry REST API.

Provides singleton instance injection for IndustryService.
"""

import logging
from typing import Generator, Optional

from backend.industry_engine.service.industry_service import IndustryService

logger = logging.getLogger("industry_engine.api.dependencies")

_service_instance: Optional[IndustryService] = None


def get_industry_service() -> IndustryService:
    """
    FastAPI dependency returning the singleton IndustryService instance.
    """
    global _service_instance
    if _service_instance is None:
        logger.info("[API] Initializing IndustryService singleton for API dependency injection.")
        _service_instance = IndustryService(force_fallback_embeddings=True)
    return _service_instance


def set_industry_service_instance(instance: IndustryService) -> None:
    """Explicitly override singleton instance (useful for testing or custom configuration)."""
    global _service_instance
    _service_instance = instance
