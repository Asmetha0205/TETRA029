"""
Semantic Service Layer Package for CurricuAlign AI Semantic Engine.
"""

from backend.semantic_engine.service.exceptions import ComparisonExecutionError, EmptyCurriculumError, SemanticServiceError
from backend.semantic_engine.service.semantic_service import SemanticService
from backend.semantic_engine.service.service_models import SemanticEngineHealthStatus
from backend.semantic_engine.service.service_validator import SemanticServiceValidator

__all__ = [
    "SemanticService",
    "SemanticServiceValidator",
    "SemanticEngineHealthStatus",
    "SemanticServiceError",
    "ComparisonExecutionError",
    "EmptyCurriculumError",
]
