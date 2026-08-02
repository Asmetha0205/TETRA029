"""
FastAPI Dependencies for Academic REST API.
"""

import logging
from typing import Optional

from backend.academic_engine.service.academic_service import AcademicService

logger = logging.getLogger("academic_engine.api.dependencies")

_service_instance: Optional[AcademicService] = None


def get_academic_service() -> AcademicService:
    """
    FastAPI dependency returning singleton AcademicService instance.
    """
    global _service_instance
    if _service_instance is None:
        logger.info("[API] Initializing AcademicService singleton for dependency injection.")
        _service_instance = AcademicService()
    return _service_instance


def set_academic_service_instance(instance: AcademicService) -> None:
    """Override singleton instance (useful for testing or custom configuration)."""
    global _service_instance
    _service_instance = instance
