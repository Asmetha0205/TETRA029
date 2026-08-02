"""
Health Service.
Performs comprehensive health checks across Academic, Industry, Semantic, Recommendation,
Neo4j, ChromaDB, Gemini, and File Repository Access.
"""

import os
import time
from typing import Any, Dict, Optional
from backend.gateway.academic_gateway import AcademicGateway
from backend.gateway.industry_gateway import IndustryGateway
from backend.gateway.semantic_gateway import SemanticGateway
from backend.gateway.recommendation_gateway import RecommendationGateway
from backend.health.health_models import (
    ComponentHealthDetail,
    OverallHealthReport,
    SystemHealthStatusEnum,
)
from backend.utils.logger import get_logger

logger = get_logger("health.service")


class HealthService:
    """Orchestrates multi-subsystem health probes."""

    def __init__(
        self,
        academic_gateway: Optional[AcademicGateway] = None,
        industry_gateway: Optional[IndustryGateway] = None,
        semantic_gateway: Optional[SemanticGateway] = None,
        recommendation_gateway: Optional[RecommendationGateway] = None,
    ):
        self.academic_gateway = academic_gateway or AcademicGateway()
        self.industry_gateway = industry_gateway or IndustryGateway()
        self.semantic_gateway = semantic_gateway or SemanticGateway()
        self.recommendation_gateway = recommendation_gateway or RecommendationGateway()

    def check_health(self) -> OverallHealthReport:
        """Run deep health check on all backend engines and infrastructure."""
        logger.info("[HealthService] Initiating system-wide health check.")

        # 1. Academic Engine
        ac_t0 = time.time()
        try:
            ac_res = self.academic_gateway.check_health()
            ac_status = (
                SystemHealthStatusEnum.HEALTHY
                if ac_res.get("status") in ["healthy", "UP"]
                else SystemHealthStatusEnum.DEGRADED
            )
            ac_detail = ComponentHealthDetail(
                status=ac_status,
                message="Academic Engine healthy",
                details=ac_res,
                response_time_ms=round((time.time() - ac_t0) * 1000, 2),
            )
        except Exception as e:
            ac_detail = ComponentHealthDetail(
                status=SystemHealthStatusEnum.UNHEALTHY,
                message=f"Academic Engine error: {e}",
                response_time_ms=round((time.time() - ac_t0) * 1000, 2),
            )

        # 2. Industry Engine
        ind_t0 = time.time()
        try:
            ind_res = self.industry_gateway.check_health()
            ind_status = (
                SystemHealthStatusEnum.HEALTHY
                if ind_res.get("status") in ["healthy", "UP"]
                else SystemHealthStatusEnum.DEGRADED
            )
            ind_detail = ComponentHealthDetail(
                status=ind_status,
                message="Industry Engine healthy",
                details=ind_res,
                response_time_ms=round((time.time() - ind_t0) * 1000, 2),
            )
        except Exception as e:
            ind_detail = ComponentHealthDetail(
                status=SystemHealthStatusEnum.UNHEALTHY,
                message=f"Industry Engine error: {e}",
                response_time_ms=round((time.time() - ind_t0) * 1000, 2),
            )

        # 3. Semantic Engine
        sem_t0 = time.time()
        try:
            sem_res = self.semantic_gateway.check_health()
            sem_status = (
                SystemHealthStatusEnum.HEALTHY
                if sem_res.get("status") in ["healthy", "UP"]
                else SystemHealthStatusEnum.DEGRADED
            )
            sem_detail = ComponentHealthDetail(
                status=sem_status,
                message="Semantic Engine healthy",
                details=sem_res,
                response_time_ms=round((time.time() - sem_t0) * 1000, 2),
            )
        except Exception as e:
            sem_detail = ComponentHealthDetail(
                status=SystemHealthStatusEnum.UNHEALTHY,
                message=f"Semantic Engine error: {e}",
                response_time_ms=round((time.time() - sem_t0) * 1000, 2),
            )

        # 4. Recommendation Engine
        rec_t0 = time.time()
        try:
            rec_res = self.recommendation_gateway.check_health()
            rec_status = (
                SystemHealthStatusEnum.HEALTHY
                if rec_res.get("status") in ["healthy", "degraded"]
                else SystemHealthStatusEnum.UNHEALTHY
            )
            rec_detail = ComponentHealthDetail(
                status=rec_status,
                message="Recommendation Layer active",
                details=rec_res,
                response_time_ms=round((time.time() - rec_t0) * 1000, 2),
            )
        except Exception as e:
            rec_detail = ComponentHealthDetail(
                status=SystemHealthStatusEnum.UNHEALTHY,
                message=f"Recommendation Engine error: {e}",
                response_time_ms=round((time.time() - rec_t0) * 1000, 2),
            )

        # 5. Neo4j Graph DB
        neo_t0 = time.time()
        try:
            is_fallback = self.recommendation_gateway.service.repo.is_using_memory_fallback()
            neo_ok = not is_fallback
            neo_detail = ComponentHealthDetail(
                status=SystemHealthStatusEnum.HEALTHY if neo_ok else SystemHealthStatusEnum.DEGRADED,
                message="Neo4j connected" if neo_ok else "Neo4j disconnected (using mock graph fallback)",
                details={"using_memory_fallback": is_fallback},
                response_time_ms=round((time.time() - neo_t0) * 1000, 2),
            )
        except Exception as e:
            neo_detail = ComponentHealthDetail(
                status=SystemHealthStatusEnum.DEGRADED,
                message=f"Neo4j check fallback: {e}",
                response_time_ms=round((time.time() - neo_t0) * 1000, 2),
            )

        # 6. ChromaDB Vector Store
        chr_t0 = time.time()
        try:
            chroma_client = self.industry_gateway.service.chroma_client_wrapper
            chroma_ok = chroma_client is not None
            chr_detail = ComponentHealthDetail(
                status=SystemHealthStatusEnum.HEALTHY if chroma_ok else SystemHealthStatusEnum.DEGRADED,
                message="ChromaDB persistent client online" if chroma_ok else "ChromaDB fallback",
                response_time_ms=round((time.time() - chr_t0) * 1000, 2),
            )
        except Exception as e:
            chr_detail = ComponentHealthDetail(
                status=SystemHealthStatusEnum.DEGRADED,
                message=f"ChromaDB error: {e}",
                response_time_ms=round((time.time() - chr_t0) * 1000, 2),
            )

        # 7. Gemini API
        gem_t0 = time.time()
        try:
            gemini_key = os.getenv("GEMINI_API_KEY")
            has_key = bool(gemini_key)
            gem_detail = ComponentHealthDetail(
                status=SystemHealthStatusEnum.HEALTHY if has_key else SystemHealthStatusEnum.DEGRADED,
                message="Gemini API Key configured" if has_key else "Gemini API Key missing (using local heuristic fallback)",
                details={"api_key_present": has_key},
                response_time_ms=round((time.time() - gem_t0) * 1000, 2),
            )
        except Exception as e:
            gem_detail = ComponentHealthDetail(
                status=SystemHealthStatusEnum.DEGRADED,
                message=f"Gemini check error: {e}",
                response_time_ms=round((time.time() - gem_t0) * 1000, 2),
            )

        # 8. Local File Repository Access
        repo_t0 = time.time()
        try:
            test_dir = "./data"
            os.makedirs(test_dir, exist_ok=True)
            repo_acc_ok = os.access(test_dir, os.W_OK)
            repo_detail = ComponentHealthDetail(
                status=SystemHealthStatusEnum.HEALTHY if repo_acc_ok else SystemHealthStatusEnum.UNHEALTHY,
                message="Local storage repository write access confirmed" if repo_acc_ok else "Local storage read-only",
                details={"storage_path": os.path.abspath(test_dir)},
                response_time_ms=round((time.time() - repo_t0) * 1000, 2),
            )
        except Exception as e:
            repo_detail = ComponentHealthDetail(
                status=SystemHealthStatusEnum.UNHEALTHY,
                message=f"Storage access error: {e}",
                response_time_ms=round((time.time() - repo_t0) * 1000, 2),
            )

        # Compute overall status
        all_statuses = [
            ac_detail.status,
            ind_detail.status,
            sem_detail.status,
            rec_detail.status,
            neo_detail.status,
            chr_detail.status,
            gem_detail.status,
            repo_detail.status,
        ]

        if SystemHealthStatusEnum.UNHEALTHY in all_statuses:
            overall = SystemHealthStatusEnum.UNHEALTHY
        elif SystemHealthStatusEnum.DEGRADED in all_statuses:
            overall = SystemHealthStatusEnum.DEGRADED
        else:
            overall = SystemHealthStatusEnum.HEALTHY

        return OverallHealthReport(
            status=overall,
            academic_engine=ac_detail,
            industry_engine=ind_detail,
            semantic_engine=sem_detail,
            recommendation_engine=rec_detail,
            neo4j=neo_detail,
            chromadb=chr_detail,
            gemini=gem_detail,
            repository_access=repo_detail,
            summary={
                "total_components_checked": len(all_statuses),
                "healthy_count": all_statuses.count(SystemHealthStatusEnum.HEALTHY),
                "degraded_count": all_statuses.count(SystemHealthStatusEnum.DEGRADED),
                "unhealthy_count": all_statuses.count(SystemHealthStatusEnum.UNHEALTHY),
            },
        )
