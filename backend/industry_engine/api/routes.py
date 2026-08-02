"""
FastAPI Routes for the Industry REST API.

Provides production-ready REST endpoints under the '/industry' prefix.
"""

import logging
from typing import Any, Dict, List, Optional

from backend.industry_engine.service.industry_service import IndustryService
from backend.industry_engine.api.dependencies import get_industry_service
from backend.industry_engine.api.controllers import IndustryController
from backend.industry_engine.api.schemas import (
    RefreshRequestPayload,
    RefreshResponse,
    RollbackRequestPayload,
    RollbackResponse,
    SimilarSearchResponse,
    TechnologyListResponse,
    TechnologyResponse,
)

logger = logging.getLogger("industry_engine.api.routes")

_FASTAPI_AVAILABLE = False
try:
    from fastapi import APIRouter, Depends, HTTPException, Query, status
    _FASTAPI_AVAILABLE = True
except ImportError:
    _FASTAPI_AVAILABLE = False


if _FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/industry", tags=["Industry Intelligence Engine"])

    @router.get("/technologies", response_model=TechnologyListResponse, summary="Get all technology records")
    def get_all_technologies(service: IndustryService = Depends(get_industry_service)):
        controller = IndustryController(service)
        return controller.list_technologies()

    @router.get("/technology/{technology_id}", response_model=TechnologyResponse, summary="Get technology by ID")
    def get_technology(technology_id: str, service: IndustryService = Depends(get_industry_service)):
        controller = IndustryController(service)
        try:
            return controller.get_technology(technology_id)
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/search", response_model=TechnologyListResponse, summary="Search technologies")
    def search_technologies(
        q: str = Query(..., min_length=1, description="Search query string"),
        service: IndustryService = Depends(get_industry_service),
    ):
        controller = IndustryController(service)
        return controller.search_technologies(q)

    @router.get("/search/similar", response_model=SimilarSearchResponse, summary="Vector similarity search")
    def search_similar(
        q: str = Query(..., min_length=1, description="Query string for vector similarity search"),
        limit: int = Query(default=10, ge=1, le=100),
        service: IndustryService = Depends(get_industry_service),
    ):
        controller = IndustryController(service)
        return controller.search_similar(query=q, limit=limit)

    @router.get("/trending", response_model=TechnologyListResponse, summary="Get trending technologies")
    def get_trending(
        limit: int = Query(default=10, ge=1, le=100),
        service: IndustryService = Depends(get_industry_service),
    ):
        controller = IndustryController(service)
        return controller.get_trending(limit=limit)

    @router.get("/emerging", response_model=TechnologyListResponse, summary="Get emerging technologies")
    def get_emerging(
        limit: int = Query(default=10, ge=1, le=100),
        service: IndustryService = Depends(get_industry_service),
    ):
        controller = IndustryController(service)
        return controller.get_emerging(limit=limit)

    @router.get("/core", response_model=TechnologyListResponse, summary="Get core technologies")
    def get_core(
        limit: int = Query(default=10, ge=1, le=100),
        service: IndustryService = Depends(get_industry_service),
    ):
        controller = IndustryController(service)
        return controller.get_core(limit=limit)

    @router.get("/statistics", summary="Get aggregate statistics")
    def get_statistics(service: IndustryService = Depends(get_industry_service)):
        controller = IndustryController(service)
        return controller.get_statistics()

    @router.get("/snapshots", summary="List knowledge snapshots")
    def get_snapshots(service: IndustryService = Depends(get_industry_service)):
        controller = IndustryController(service)
        return controller.get_snapshots()

    @router.get("/health", summary="Get overall engine health")
    def get_health(service: IndustryService = Depends(get_industry_service)):
        controller = IndustryController(service)
        return controller.get_health()

    @router.post("/refresh", response_model=RefreshResponse, summary="Trigger pipeline refresh")
    def refresh_industry(
        payload: RefreshRequestPayload,
        service: IndustryService = Depends(get_industry_service),
    ):
        controller = IndustryController(service)
        return controller.refresh_industry(payload)

    @router.post("/rollback", response_model=RollbackResponse, summary="Rollback snapshot")
    def rollback_snapshot(
        payload: RollbackRequestPayload,
        service: IndustryService = Depends(get_industry_service),
    ):
        controller = IndustryController(service)
        try:
            return controller.rollback_snapshot(payload)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

else:
    class MockRoute:
        def __init__(self, path: str, method: str, endpoint: Any) -> None:
            self.path = path
            self.method = method
            self.endpoint = endpoint

    class MockRouter:
        """Fallback APIRouter representation when FastAPI is not installed."""
        def __init__(self, prefix: str = "/industry") -> None:
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

    router = MockRouter(prefix="/industry")

    # Define fallback routes metadata so routes are registered in mock mode as well
    @router.get("/technologies")
    def get_all_technologies(service: Optional[IndustryService] = None):
        c = IndustryController(service or get_industry_service())
        return c.list_technologies()

    @router.get("/technology/{technology_id}")
    def get_technology(technology_id: str, service: Optional[IndustryService] = None):
        c = IndustryController(service or get_industry_service())
        return c.get_technology(technology_id)

    @router.get("/search")
    def search_technologies(q: str, service: Optional[IndustryService] = None):
        c = IndustryController(service or get_industry_service())
        return c.search_technologies(q)

    @router.get("/search/similar")
    def search_similar(q: str, limit: int = 10, service: Optional[IndustryService] = None):
        c = IndustryController(service or get_industry_service())
        return c.search_similar(query=q, limit=limit)

    @router.get("/trending")
    def get_trending(limit: int = 10, service: Optional[IndustryService] = None):
        c = IndustryController(service or get_industry_service())
        return c.get_trending(limit=limit)

    @router.get("/emerging")
    def get_emerging(limit: int = 10, service: Optional[IndustryService] = None):
        c = IndustryController(service or get_industry_service())
        return c.get_emerging(limit=limit)

    @router.get("/core")
    def get_core(limit: int = 10, service: Optional[IndustryService] = None):
        c = IndustryController(service or get_industry_service())
        return c.get_core(limit=limit)

    @router.get("/statistics")
    def get_statistics(service: Optional[IndustryService] = None):
        c = IndustryController(service or get_industry_service())
        return c.get_statistics()

    @router.get("/snapshots")
    def get_snapshots(service: Optional[IndustryService] = None):
        c = IndustryController(service or get_industry_service())
        return c.get_snapshots()

    @router.get("/health")
    def get_health(service: Optional[IndustryService] = None):
        c = IndustryController(service or get_industry_service())
        return c.get_health()

    @router.post("/refresh")
    def refresh_industry(payload: RefreshRequestPayload, service: Optional[IndustryService] = None):
        c = IndustryController(service or get_industry_service())
        return c.refresh_industry(payload)

    @router.post("/rollback")
    def rollback_snapshot(payload: RollbackRequestPayload, service: Optional[IndustryService] = None):
        c = IndustryController(service or get_industry_service())
        return c.rollback_snapshot(payload)
