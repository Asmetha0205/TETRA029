"""
API Controllers for the Industry REST API.

Maps API requests to IndustryService business logic.
"""

import logging
from typing import Any, Dict, List, Optional

from backend.industry_engine.service.industry_service import IndustryService
from backend.industry_engine.service.service_models import RefreshRequestOptions
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

logger = logging.getLogger("industry_engine.api.controllers")


class IndustryController:
    """Controller delegating REST operations to IndustryService."""

    def __init__(self, service: IndustryService) -> None:
        self.service = service

    def list_technologies(self) -> TechnologyListResponse:
        logger.info("[API] GET /industry/technologies")
        records = self.service.get_all_technologies()
        items = [self._record_to_schema(r) for r in records]
        return TechnologyListResponse(total=len(items), technologies=items)

    def get_technology(self, technology_id: str) -> TechnologyResponse:
        logger.info("[API] GET /industry/technology/%s", technology_id)
        record = self.service.get_technology(technology_id)
        return self._record_to_schema(record)

    def search_technologies(self, query: str) -> TechnologyListResponse:
        logger.info("[API] GET /industry/search?q=%s", query)
        records = self.service.search(query)
        items = [self._record_to_schema(r) for r in records]
        return TechnologyListResponse(total=len(items), technologies=items)

    def search_similar(self, query: str, limit: int = 10) -> SimilarSearchResponse:
        logger.info("[API] GET /industry/search/similar?q=%s&limit=%d", query, limit)
        results = self.service.search_similar(query=query, limit=limit)
        items = [
            SimilarSearchResponseItem(
                technology_id=r.technology_id,
                canonical_name=r.canonical_name,
                category=r.category,
                similarity_score=r.similarity_score,
                distance=r.distance,
                metadata=r.metadata,
            )
            for r in results
        ]
        return SimilarSearchResponse(query=query, total=len(items), results=items)

    def get_trending(self, limit: int = 10) -> TechnologyListResponse:
        logger.info("[API] GET /industry/trending?limit=%d", limit)
        records = self.service.get_trending(limit=limit)
        items = [self._record_to_schema(r) for r in records]
        return TechnologyListResponse(total=len(items), technologies=items)

    def get_emerging(self, limit: int = 10) -> TechnologyListResponse:
        logger.info("[API] GET /industry/emerging?limit=%d", limit)
        records = self.service.get_emerging(limit=limit)
        items = [self._record_to_schema(r) for r in records]
        return TechnologyListResponse(total=len(items), technologies=items)

    def get_core(self, limit: int = 10) -> TechnologyListResponse:
        logger.info("[API] GET /industry/core?limit=%d", limit)
        records = self.service.get_core(limit=limit)
        items = [self._record_to_schema(r) for r in records]
        return TechnologyListResponse(total=len(items), technologies=items)

    def get_statistics(self) -> Dict[str, Any]:
        logger.info("[API] GET /industry/statistics")
        stats = self.service.get_statistics()
        return stats.model_dump()

    def get_snapshots(self) -> List[Dict[str, Any]]:
        logger.info("[API] GET /industry/snapshots")
        snaps = self.service.get_snapshots()
        return [s.model_dump() for s in snaps]

    def get_health(self) -> Dict[str, Any]:
        logger.info("[API] GET /industry/health")
        health_status = self.service.health()
        return health_status.model_dump()

    def refresh_industry(self, payload: RefreshRequestPayload) -> RefreshResponse:
        logger.info("[API] Refresh Request (source='%s', dry_run=%s)", payload.source_name, payload.dry_run)
        opts = RefreshRequestOptions(
            source_name=payload.source_name,
            dry_run=payload.dry_run,
            auto_snapshot=payload.auto_snapshot,
        )
        summary = self.service.refresh_industry(options=opts)
        return RefreshResponse(
            run_id=summary.run_id,
            success=summary.success,
            raw_jobs_count=summary.raw_jobs_count,
            clean_jobs_count=summary.clean_jobs_count,
            normalized_count=summary.normalized_count,
            knowledge_created=summary.knowledge_created,
            knowledge_updated=summary.knowledge_updated,
            embeddings_generated=summary.embeddings_generated,
            chroma_synced=summary.chroma_synced,
            snapshot_id=summary.snapshot_id,
            error_message=summary.error_message,
            execution_time_seconds=summary.execution_time_seconds,
        )

    def rollback_snapshot(self, payload: RollbackRequestPayload) -> RollbackResponse:
        logger.info("[API] POST /industry/rollback (%s)", payload.snapshot_id)
        loaded, pre_snap = self.service.rollback_snapshot(payload.snapshot_id)
        return RollbackResponse(
            snapshot_id=payload.snapshot_id,
            records_loaded=loaded,
            success=True,
            message=f"Successfully rolled back state to snapshot '{payload.snapshot_id}' ({loaded} records loaded).",
        )

    @staticmethod
    def _record_to_schema(r: Any) -> TechnologyResponse:
        return TechnologyResponse(
            technology_id=r.technology_id,
            canonical_name=r.canonical_name,
            category=r.category,
            aliases=r.aliases,
            description=r.description,
            frequency=r.frequency,
            demand_score=r.demand_score,
            industry_score=r.industry_score,
            trend=r.trend.value if hasattr(r.trend, "value") else str(r.trend),
            growth=r.growth,
            classification=r.classification.value if hasattr(r.classification, "value") else str(r.classification),
            related_technologies=r.related_technologies,
            role_coverage=r.role_coverage,
            status=r.status.value if hasattr(r.status, "value") else str(r.status),
            version=r.version.to_string() if hasattr(r.version, "to_string") else str(r.version),
            metadata=r.metadata,
        )
