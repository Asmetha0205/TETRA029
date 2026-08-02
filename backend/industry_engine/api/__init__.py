"""
Industry REST API Package for CurricuAlign AI Industry Intelligence Engine.

Provides production-ready FastAPI endpoints for discovery, search, similarity, health, and refresh.
"""

from backend.industry_engine.api.controllers import IndustryController
from backend.industry_engine.api.dependencies import get_industry_service, set_industry_service_instance
from backend.industry_engine.api.routes import router
from backend.industry_engine.api.schemas import (
    RefreshRequestPayload,
    RefreshResponse,
    RollbackRequestPayload,
    RollbackResponse,
    SimilarSearchResponse,
    SimilarSearchResponseItem,
    TechnologyListResponse,
    TechnologyResponse,
)

__all__ = [
    "router",
    "IndustryController",
    "get_industry_service",
    "set_industry_service_instance",
    "TechnologyResponse",
    "TechnologyListResponse",
    "SimilarSearchResponseItem",
    "SimilarSearchResponse",
    "RefreshRequestPayload",
    "RefreshResponse",
    "RollbackRequestPayload",
    "RollbackResponse",
]
