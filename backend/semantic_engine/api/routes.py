"""
FastAPI Routes for the Semantic REST API.

Provides production-ready REST endpoints under the '/semantic' prefix.
"""

import logging
from typing import Any, Dict, List, Optional

from backend.semantic_engine.api.controllers import SemanticController
from backend.semantic_engine.api.dependencies import get_semantic_service
from backend.semantic_engine.api.schemas import ComparisonReportResponse, SkillMatchResponseItem
from backend.semantic_engine.service.semantic_service import SemanticService

logger = logging.getLogger("semantic_engine.api.routes")

_FASTAPI_AVAILABLE = False
try:
    from fastapi import APIRouter, Depends, HTTPException, Query
    _FASTAPI_AVAILABLE = True
except ImportError:
    _FASTAPI_AVAILABLE = False


if _FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/semantic", tags=["Semantic Intelligence Engine"])

    @router.post("/compare", response_model=ComparisonReportResponse, summary="Compare curriculum against Industry Knowledge")
    def compare_curriculum(service: SemanticService = Depends(get_semantic_service)):
        controller = SemanticController(service)
        return controller.compare_curriculum()

    @router.get("/gaps", response_model=List[SkillMatchResponseItem], summary="Get missing industry skill gaps")
    def get_gaps(service: SemanticService = Depends(get_semantic_service)):
        controller = SemanticController(service)
        return controller.get_gaps()

    @router.get("/covered", response_model=List[SkillMatchResponseItem], summary="Get covered skills")
    def get_covered(service: SemanticService = Depends(get_semantic_service)):
        controller = SemanticController(service)
        return controller.get_covered()

    @router.get("/partial", response_model=List[SkillMatchResponseItem], summary="Get partially covered skills")
    def get_partial(service: SemanticService = Depends(get_semantic_service)):
        controller = SemanticController(service)
        return controller.get_partial()

    @router.get("/statistics", summary="Get coverage statistics")
    def get_statistics(service: SemanticService = Depends(get_semantic_service)):
        controller = SemanticController(service)
        return controller.get_statistics()

    @router.get("/report", response_model=ComparisonReportResponse, summary="Generate full alignment report")
    def get_report(service: SemanticService = Depends(get_semantic_service)):
        controller = SemanticController(service)
        return controller.get_report()

    @router.get("/search", summary="Vector similarity candidate search")
    def search_similar(
        q: str = Query(..., min_length=1, description="Query text"),
        limit: int = Query(default=10, ge=1, le=100),
        service: SemanticService = Depends(get_semantic_service),
    ):
        controller = SemanticController(service)
        return controller.search_similar(query=q, limit=limit)

else:
    class MockRoute:
        def __init__(self, path: str, method: str, endpoint: Any) -> None:
            self.path = path
            self.method = method
            self.endpoint = endpoint

    class MockRouter:
        def __init__(self, prefix: str = "/semantic") -> None:
            self.prefix = prefix
            self.routes: List[MockRoute] = []

        def get(self, path: str, **kwargs: Any):
            def decorator(fn):
                self.routes.append(MockRoute(self.prefix + path, "GET", fn))
                return fn
            return decorator

        def post(self, path: str, **kwargs: Any):
            def decorator(fn):
                self.routes.append(MockRoute(self.prefix + path, "POST", fn))
                return fn
            return decorator

    router = MockRouter(prefix="/semantic")

    @router.post("/compare")
    def compare_curriculum(service: Optional[SemanticService] = None):
        c = SemanticController(service or get_semantic_service())
        return c.compare_curriculum()

    @router.get("/gaps")
    def get_gaps(service: Optional[SemanticService] = None):
        c = SemanticController(service or get_semantic_service())
        return c.get_gaps()

    @router.get("/covered")
    def get_covered(service: Optional[SemanticService] = None):
        c = SemanticController(service or get_semantic_service())
        return c.get_covered()

    @router.get("/partial")
    def get_partial(service: Optional[SemanticService] = None):
        c = SemanticController(service or get_semantic_service())
        return c.get_partial()

    @router.get("/statistics")
    def get_statistics(service: Optional[SemanticService] = None):
        c = SemanticController(service or get_semantic_service())
        return c.get_statistics()

    @router.get("/report")
    def get_report(service: Optional[SemanticService] = None):
        c = SemanticController(service or get_semantic_service())
        return c.get_report()

    @router.get("/search")
    def search_similar(q: str, limit: int = 10, service: Optional[SemanticService] = None):
        c = SemanticController(service or get_semantic_service())
        return c.search_similar(q, limit=limit)
