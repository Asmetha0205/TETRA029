"""
API Controllers.
Implements handler logic, security checks, and input sanitization for API routes.
"""

import os
import time
from typing import Any, Dict, Optional
from fastapi import HTTPException, UploadFile, status
from backend.api.schemas import ApiResponse
from backend.cache.cache_service import CacheService
from backend.health.health_service import HealthService
from backend.monitoring.performance_monitor import PerformanceMonitor
from backend.orchestrator.analysis_orchestrator import AnalysisOrchestrator
from backend.config.config import system_config
from backend.utils.logger import get_logger

logger = get_logger("api.controllers")

START_TIME = time.time()


class SystemApiController:
    """Controller for unified API endpoints."""

    def __init__(
        self,
        orchestrator: AnalysisOrchestrator,
        health_service: HealthService,
        cache_service: CacheService,
    ):
        self.orchestrator = orchestrator
        self.health_service = health_service
        self.cache_service = cache_service

    async def analyze_curriculum(
        self,
        file: UploadFile,
        university_name: str = "Unknown University",
        curriculum_year: str = "2025-2026",
        department: str = "Computer Science",
    ) -> ApiResponse:
        """Handle PDF upload and run full orchestration analysis."""
        # 1. Security & Validation Checks
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename missing.")

        # Sanitize filename (prevent path traversal)
        safe_filename = os.path.basename(file.filename).strip()
        if not safe_filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Only PDF files are supported.",
            )

        file_bytes = await file.read()
        max_bytes = system_config.max_upload_size_mb * 1024 * 1024
        if len(file_bytes) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed limit of {system_config.max_upload_size_mb} MB.",
            )

        # Sanitize metadata text inputs
        clean_univ = university_name.strip()[:100]
        clean_year = curriculum_year.strip()[:20]
        clean_dept = department.strip()[:100]

        try:
            result = self.orchestrator.analyze_curriculum(
                file_bytes=file_bytes,
                filename=safe_filename,
                university_name=clean_univ,
                curriculum_year=clean_year,
                department=clean_dept,
            )
            return ApiResponse(
                success=True,
                message="Curriculum analysis completed successfully.",
                data=result,
            )
        except Exception as e:
            logger.error("[ApiController] Analysis failed: %s", e)
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    def get_analysis(self, analysis_id: str) -> ApiResponse:
        """Retrieve completed analysis by analysis_id."""
        clean_id = os.path.basename(analysis_id).strip()
        result = self.orchestrator.get_analysis_result(clean_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Analysis ID '{clean_id}' not found.")
        return ApiResponse(
            success=True,
            message="Analysis retrieved successfully.",
            data=result,
        )

    def get_report(self, analysis_id: str) -> ApiResponse:
        """Retrieve executive report view of analysis."""
        clean_id = os.path.basename(analysis_id).strip()
        result = self.orchestrator.get_analysis_result(clean_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Report for Analysis ID '{clean_id}' not found.")

        report_summary = {
            "analysis_id": result["analysis_id"],
            "alignment_score": result["alignment_score"],
            "priority_summary": result["priority_summary"],
            "top_recommendations": result["recommendations"][:3],
            "learning_paths": result["learning_paths"],
            "generated_at": result["generated_at"],
        }
        return ApiResponse(
            success=True,
            message="Executive report retrieved successfully.",
            data=report_summary,
        )

    def get_dashboard(self) -> ApiResponse:
        """Retrieve system dashboard summary."""
        stats = self.cache_service.get_statistics()
        active_jobs = self.orchestrator.workflow_manager.list_active_jobs()
        health = self.health_service.check_health()

        dashboard_data = {
            "total_analyses_conducted": len(active_jobs),
            "system_health_status": health.status.value,
            "cache_hit_ratio": stats.hit_ratio,
            "top_industry_gaps": ["Docker", "Kubernetes", "Redis", "FastAPI", "GraphQL"],
            "active_workflows_count": len(active_jobs),
        }
        return ApiResponse(
            success=True,
            message="Dashboard summary retrieved successfully.",
            data=dashboard_data,
        )

    def get_status(self) -> ApiResponse:
        """Retrieve system status and active workflow state."""
        uptime = round(time.time() - START_TIME, 2)
        active_jobs = self.orchestrator.workflow_manager.list_active_jobs()

        return ApiResponse(
            success=True,
            message="System operational status.",
            data={
                "status": "OPERATIONAL",
                "uptime_seconds": uptime,
                "active_jobs_count": len(active_jobs),
                "active_jobs": active_jobs,
            },
        )

    def get_health(self) -> ApiResponse:
        """Run and return full health check."""
        health = self.health_service.check_health()
        return ApiResponse(
            success=True,
            message="System health evaluation completed.",
            data=health.model_dump(),
        )

    def get_system_statistics(self) -> ApiResponse:
        """Retrieve system-wide metrics and performance statistics."""
        telemetry = PerformanceMonitor.get_system_telemetry()
        cache_stats = self.cache_service.get_statistics().model_dump()

        return ApiResponse(
            success=True,
            message="System performance statistics retrieved.",
            data={
                "telemetry": telemetry,
                "cache_statistics": cache_stats,
            },
        )
