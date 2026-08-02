"""
Semantic REST API Package for CurricuAlign AI Semantic Engine.
"""

from backend.semantic_engine.api.controllers import SemanticController
from backend.semantic_engine.api.dependencies import get_semantic_service, set_semantic_service_instance
from backend.semantic_engine.api.routes import router
from backend.semantic_engine.api.schemas import ComparisonReportResponse, SkillMatchResponseItem

__all__ = [
    "router",
    "SemanticController",
    "get_semantic_service",
    "set_semantic_service_instance",
    "SkillMatchResponseItem",
    "ComparisonReportResponse",
]
