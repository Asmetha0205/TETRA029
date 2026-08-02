"""
FastAPI Routes for Unified CurricuAlign AI API.
Exposes all orchestration, reporting, monitoring, and health endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, FastAPI
from backend.api.controllers import SystemApiController
from backend.api.dependencies import (
    get_cache_service,
    get_health_service,
    get_orchestrator,
)
from backend.api.schemas import ApiResponse
from backend.cache.cache_service import CacheService
from backend.health.health_service import HealthService
from backend.orchestrator.analysis_orchestrator import AnalysisOrchestrator

router = APIRouter(prefix="", tags=["CurricuAlign AI Unified Platform"])


def _get_controller(
    orchestrator: AnalysisOrchestrator = Depends(get_orchestrator),
    health_service: HealthService = Depends(get_health_service),
    cache_service: CacheService = Depends(get_cache_service),
) -> SystemApiController:
    return SystemApiController(orchestrator, health_service, cache_service)


@router.post("/analyze-curriculum", response_model=ApiResponse)
async def analyze_curriculum(
    file: UploadFile = File(...),
    university_name: str = Form("Unknown University"),
    curriculum_year: str = Form("2025-2026"),
    department: str = Form("Computer Science"),
    controller: SystemApiController = Depends(_get_controller),
):
    """
    Single-call end-to-end curriculum analysis endpoint.
    Uploads PDF -> Academic Engine -> Industry Engine -> Semantic Engine -> Recommendation Engine -> Unified Response.
    """
    return await controller.analyze_curriculum(
        file=file,
        university_name=university_name,
        curriculum_year=curriculum_year,
        department=department,
    )


@router.get("/analysis/{analysis_id}", response_model=ApiResponse)
def get_analysis(
    analysis_id: str,
    controller: SystemApiController = Depends(_get_controller),
):
    """Retrieve full analysis result by analysis_id."""
    return controller.get_analysis(analysis_id)


@router.get("/report/{analysis_id}", response_model=ApiResponse)
def get_report(
    analysis_id: str,
    controller: SystemApiController = Depends(_get_controller),
):
    """Retrieve executive report summary for analysis_id."""
    return controller.get_report(analysis_id)


@router.get("/dashboard", response_model=ApiResponse)
def get_dashboard(
    controller: SystemApiController = Depends(_get_controller),
):
    """Get aggregate system dashboard analytics."""
    return controller.get_dashboard()


@router.get("/status", response_model=ApiResponse)
def get_status(
    controller: SystemApiController = Depends(_get_controller),
):
    """Get operational status and active workflow list."""
    return controller.get_status()


@router.get("/health", response_model=ApiResponse)
def get_health(
    controller: SystemApiController = Depends(_get_controller),
):
    """Comprehensive system-wide health evaluation of all 4 engines and infrastructure."""
    return controller.get_health()


@router.get("/system/statistics", response_model=ApiResponse)
def get_system_statistics(
    controller: SystemApiController = Depends(_get_controller),
):
    """Retrieve telemetry metrics and cache performance statistics."""
    return controller.get_system_statistics()


# Master FastAPI application factory
def create_app() -> FastAPI:
    """Create and configure master FastAPI web application."""
    app = FastAPI(
        title="CurricuAlign AI - Complete Unified Backend Platform API",
        version="1.0.0",
        description="Unified Orchestration Layer coordinating Academic, Industry, Semantic, and Recommendation Engines.",
    )
    app.include_router(router)
    return app


app = create_app()
