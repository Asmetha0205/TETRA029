"""
Industry Service for the CurricuAlign AI Industry Intelligence Engine.

The single authoritative public interface for the entire Industry Engine.
Academic Engine, Semantic Engine, Recommendation Engine, and REST API
MUST interact with the Industry Engine strictly through this service facade.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.industry_engine.knowledge.knowledge_service import KnowledgeService
from backend.industry_engine.knowledge.knowledge_models import (
    KnowledgeSnapshot,
    KnowledgeStats,
    SnapshotComparison,
    SnapshotMetadata,
    TechnologyKnowledgeRecord,
)
from backend.industry_engine.embeddings.embedding_service import EmbeddingService
from backend.industry_engine.embeddings.embedding_models import EmbeddingRecord, EmbeddingStats
from backend.industry_engine.chromadb.chroma_client import ChromaClientWrapper
from backend.industry_engine.chromadb.collection_manager import CollectionManager
from backend.industry_engine.chromadb.sync_service import ChromaSyncService
from backend.industry_engine.chromadb.query_service import ChromaQueryService
from backend.industry_engine.scheduler.refresh_pipeline import RefreshPipeline, RefreshSummaryReport
from backend.industry_engine.scheduler.refresh_manager import RefreshManager
from backend.industry_engine.scheduler.jobs import RefreshJobConfig
from backend.industry_engine.service.service_models import (
    ComponentHealth,
    IndustryHealthStatus,
    RefreshRequestOptions,
    SimilarSearchResultItem,
)
from backend.industry_engine.service.service_validator import ServiceValidator

logger = logging.getLogger("industry_engine.service.industry_service")


class IndustryService:
    """
    Principal Business Facade for the Industry Intelligence Engine.

    Encapsulates Knowledge Layer, Embedding Engine, ChromaDB Vector Sync,
    Refresh Pipeline, and Background Scheduler.
    """

    def __init__(
        self,
        repository_path: Optional[str] = None,
        snapshot_path: Optional[str] = None,
        embedding_path: Optional[str] = None,
        chroma_path: Optional[str] = None,
        force_fallback_embeddings: bool = False,
    ) -> None:
        """
        Initialize the complete Industry Intelligence Engine.

        Args:
            repository_path: Optional path for Knowledge Repository JSON.
            snapshot_path: Optional path for Snapshot JSON.
            embedding_path: Optional path for Embedding Repository JSON.
            chroma_path: Optional directory for ChromaDB persistence.
            force_fallback_embeddings: Force lightweight mode for testing/no-GPU.
        """
        # 1. Knowledge Layer
        self.knowledge_service = KnowledgeService(
            repository_path=repository_path,
            snapshot_path=snapshot_path,
        )

        # 2. Embedding Engine
        self.embedding_service = EmbeddingService(
            knowledge_service=self.knowledge_service,
            repository_path=embedding_path,
            force_fallback=force_fallback_embeddings,
        )

        # 3. ChromaDB Synchronization Layer
        self.chroma_client_wrapper = ChromaClientWrapper(persist_directory=chroma_path)
        self.collection_manager = CollectionManager(self.chroma_client_wrapper)
        self.chroma_sync_service = ChromaSyncService(self.collection_manager)
        self.chroma_query_service = ChromaQueryService(self.collection_manager)

        # 4. Refresh Pipeline & Scheduler
        self.refresh_pipeline = RefreshPipeline(
            knowledge_service=self.knowledge_service,
            embedding_service=self.embedding_service,
            chroma_sync_service=self.chroma_sync_service,
        )
        self.refresh_manager = RefreshManager(pipeline=self.refresh_pipeline)

        logger.info("[Industry] IndustryService facade initialized successfully.")

    # ------------------------------------------------------------------
    # Technology Discovery & Intelligence API
    # ------------------------------------------------------------------

    def get_all_technologies(self) -> List[TechnologyKnowledgeRecord]:
        """Return all technology records from the Knowledge Layer."""
        return self.knowledge_service.get_all()

    def get_technology(self, technology_id: str) -> TechnologyKnowledgeRecord:
        """
        Retrieve a single technology knowledge record by ID.

        Args:
            technology_id: Technology identifier.

        Returns:
            The matching TechnologyKnowledgeRecord.
        """
        clean_id = ServiceValidator.validate_technology_id(technology_id)
        return self.knowledge_service.get_technology(clean_id)

    def search(self, query: str) -> List[TechnologyKnowledgeRecord]:
        """
        Search technologies by canonical name, ID, or aliases.

        Args:
            query: Search query string.

        Returns:
            List of matching records sorted by industry_score descending.
        """
        clean_query = ServiceValidator.validate_query(query)
        return self.knowledge_service.search(clean_query)

    def search_similar(
        self, query: str, limit: int = 10
    ) -> List[SimilarSearchResultItem]:
        """
        Perform vector similarity search against the ChromaDB vector store.

        Args:
            query: Natural language search string or topic query.
            limit: Maximum results to return.

        Returns:
            List of SimilarSearchResultItem models sorted by similarity score descending.
        """
        clean_query = ServiceValidator.validate_query(query)
        clean_limit = ServiceValidator.validate_limit(limit)

        # 1. First try ChromaDB vector search
        try:
            emb_vector = self.embedding_service._manager.generator._encode_text(clean_query)
            chroma_results = self.chroma_query_service.search_by_vector(emb_vector, limit=clean_limit)

            if chroma_results:
                items = []
                for res in chroma_results:
                    items.append(
                        SimilarSearchResultItem(
                            technology_id=res.get("technology_id", ""),
                            canonical_name=res.get("canonical_name", ""),
                            category=res.get("category", ""),
                            similarity_score=res.get("similarity_score", 0.0),
                            distance=res.get("distance", 0.0),
                            metadata=res.get("metadata", {}),
                        )
                    )
                return items
        except Exception as exc:
            logger.warning("[Industry] ChromaDB vector search fallback to EmbeddingService: %s", exc)

        # 2. Fallback to EmbeddingService similarity search
        emb_results = self.embedding_service.search_similar(query=clean_query, limit=clean_limit)
        items = []
        for emb_rec, score in emb_results:
            tech_rec = self.knowledge_service.get_optional(emb_rec.technology_id) if hasattr(self.knowledge_service, "get_optional") else None
            cname = tech_rec.canonical_name if tech_rec else emb_rec.technology_id
            cat = tech_rec.category if tech_rec else "Unknown"
            items.append(
                SimilarSearchResultItem(
                    technology_id=emb_rec.technology_id,
                    canonical_name=cname,
                    category=cat,
                    similarity_score=score,
                    distance=round(1.0 - score, 4),
                )
            )
        return items

    def get_trending(self, limit: int = 10) -> List[TechnologyKnowledgeRecord]:
        """Get top technologies with rising/emerging trends."""
        clean_limit = ServiceValidator.validate_limit(limit)
        return self.knowledge_service.get_trending(limit=clean_limit)

    def get_emerging(self, limit: int = 10) -> List[TechnologyKnowledgeRecord]:
        """Get top technologies classified as Emerging."""
        clean_limit = ServiceValidator.validate_limit(limit)
        return self.knowledge_service.get_emerging(limit=clean_limit)

    def get_core(self, limit: int = 10) -> List[TechnologyKnowledgeRecord]:
        """Get top technologies classified as Core."""
        clean_limit = ServiceValidator.validate_limit(limit)
        return self.knowledge_service.get_core(limit=clean_limit)

    def get_statistics(self) -> KnowledgeStats:
        """Get aggregate intelligence statistics for the Industry Engine."""
        return self.knowledge_service.get_statistics()

    # ------------------------------------------------------------------
    # Snapshot & Rollback Operations
    # ------------------------------------------------------------------

    def get_snapshots(self) -> List[SnapshotMetadata]:
        """List all stored knowledge snapshots sorted by version descending."""
        return self.knowledge_service.list_snapshots()

    def compare_snapshots(self, snapshot_id_a: str, snapshot_id_b: str) -> SnapshotComparison:
        """Compare two snapshots and return set & field diffs."""
        return self.knowledge_service.compare_snapshots(snapshot_id_a, snapshot_id_b)

    def rollback_snapshot(self, snapshot_id: str) -> Tuple[int, Optional[KnowledgeSnapshot]]:
        """
        Rollback the Knowledge Layer to a previous snapshot and re-sync embeddings & ChromaDB.

        Args:
            snapshot_id: Target snapshot identifier.

        Returns:
            Tuple of (records_loaded_count, pre_rollback_snapshot).
        """
        loaded, pre_snap = self.knowledge_service.rollback_snapshot(snapshot_id)

        # Re-sync embeddings & ChromaDB following rollback
        self.embedding_service.generate_all_from_knowledge(force=True)

        all_techs = self.knowledge_service.get_all()
        pairs = []
        for tech in all_techs:
            emb = self.embedding_service.get_embedding(tech.technology_id)
            if emb:
                pairs.append((tech, emb))

        self.chroma_sync_service.sync_batch(pairs, incremental=False)
        logger.info("[Industry] Rolled back engine state to snapshot '%s' (%d records).", snapshot_id, loaded)
        return loaded, pre_snap

    # ------------------------------------------------------------------
    # Refresh Operations
    # ------------------------------------------------------------------

    def refresh_industry(
        self,
        options: Optional[RefreshRequestOptions] = None,
        raw_jobs: Optional[List[Any]] = None,
    ) -> RefreshSummaryReport:
        """
        Trigger an end-to-end industry pipeline refresh.

        Args:
            options: RefreshRequestOptions parameters.
            raw_jobs: Optional raw job dataset override.

        Returns:
            RefreshSummaryReport with run metrics.
        """
        opts = options or RefreshRequestOptions()
        cfg = RefreshJobConfig(
            source_name=opts.source_name,
            dry_run=opts.dry_run,
            auto_snapshot=opts.auto_snapshot,
        )
        return self.refresh_manager.trigger_refresh(raw_jobs=raw_jobs, config=cfg)

    # ------------------------------------------------------------------
    # Health Monitoring
    # ------------------------------------------------------------------

    def health(self) -> IndustryHealthStatus:
        """
        Evaluate overall health across all Industry Engine components.

        Returns:
            IndustryHealthStatus model detailing overall and component-level health.
        """
        components: Dict[str, ComponentHealth] = {}
        is_healthy = True

        # 1. Knowledge Layer Health
        try:
            k_count = self.knowledge_service.count()
            components["knowledge_layer"] = ComponentHealth(
                status="healthy",
                message=f"Operating normally ({k_count} technologies stored).",
                details={"technology_count": k_count},
            )
        except Exception as exc:
            is_healthy = False
            components["knowledge_layer"] = ComponentHealth(
                status="unhealthy",
                message=f"Knowledge Layer failure: {exc}",
            )

        # 2. Embedding Engine Health
        try:
            emb_stats = self.embedding_service.get_statistics()
            components["embedding_engine"] = ComponentHealth(
                status="healthy",
                message=f"Operating normally ({emb_stats.total_embeddings} vectors stored).",
                details={
                    "total_embeddings": emb_stats.total_embeddings,
                    "model_name": emb_stats.model_name,
                },
            )
        except Exception as exc:
            is_healthy = False
            components["embedding_engine"] = ComponentHealth(
                status="unhealthy",
                message=f"Embedding Engine failure: {exc}",
            )

        # 3. ChromaDB Health
        try:
            c_stats = self.collection_manager.get_stats()
            components["chromadb"] = ComponentHealth(
                status="healthy",
                message=f"Collection 'industry_technologies' active ({c_stats['document_count']} documents).",
                details=c_stats,
            )
        except Exception as exc:
            components["chromadb"] = ComponentHealth(
                status="degraded",
                message=f"ChromaDB component issues: {exc}",
            )

        # 4. Scheduler / Refresh Pipeline Health
        try:
            s_state = self.refresh_manager.get_state()
            components["scheduler"] = ComponentHealth(
                status="healthy" if s_state.status != "failed" else "degraded",
                message=f"Status: {s_state.status.value}",
                details=s_state.model_dump(),
            )
        except Exception as exc:
            components["scheduler"] = ComponentHealth(
                status="degraded",
                message=f"Scheduler check failed: {exc}",
            )

        overall_status = "healthy" if is_healthy else "unhealthy"
        logger.info("[Health] All Systems Operational" if is_healthy else "[Health] Engine Health Issues Detected")

        return IndustryHealthStatus(
            status=overall_status,
            components=components,
        )
