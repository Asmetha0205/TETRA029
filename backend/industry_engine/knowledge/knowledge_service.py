"""
Knowledge Service for the CurricuAlign AI Industry Knowledge Layer.

Provides the primary business facade over the knowledge repository, snapshot
manager, version manager, and knowledge builder. Controllers and API endpoints
MUST interact with the Knowledge Layer exclusively through this service.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.industry_engine.knowledge.exceptions import (
    DuplicateTechnology,
    KnowledgeError,
    RepositoryError,
    SnapshotError,
    SnapshotNotFoundError,
    TechnologyNotFound,
    ValidationError,
)
from backend.industry_engine.knowledge.knowledge_builder import KnowledgeBuilder
from backend.industry_engine.knowledge.knowledge_models import (
    KnowledgeSnapshot,
    KnowledgeStats,
    SnapshotComparison,
    SnapshotMetadata,
    TechnologyClassification,
    TechnologyKnowledgeRecord,
    TechnologyStatus,
    TechnologyTrend,
)
from backend.industry_engine.knowledge.knowledge_repository import KnowledgeRepository
from backend.industry_engine.knowledge.snapshot_manager import SnapshotManager

logger = logging.getLogger("industry_engine.knowledge.knowledge_service")


class KnowledgeService:
    """
    Business facade for the Industry Knowledge Layer.

    Encapsulates all knowledge management operations, ensuring that external callers
    (controllers, APIs, UI layers) never directly touch the underlying repository
    or snapshot manager.
    """

    def __init__(
        self,
        repository_path: Optional[str] = None,
        snapshot_path: Optional[str] = None,
        max_snapshots: int = 52,
    ) -> None:
        """
        Initialize the knowledge service and its components.

        Args:
            repository_path: Optional path for JSON repository persistence.
            snapshot_path: Optional path for JSON snapshot persistence.
            max_snapshots: Maximum number of historical snapshots to retain.
        """
        self._repository = KnowledgeRepository(storage_path=repository_path)
        self._snapshot_manager = SnapshotManager(
            storage_path=snapshot_path,
            max_snapshots=max_snapshots,
        )
        self._builder = KnowledgeBuilder()
        logger.info("[Knowledge] Service initialized.")

    # ------------------------------------------------------------------
    # CRUD Operations
    # ------------------------------------------------------------------

    def create_technology(
        self,
        canonical_name: str,
        category: str,
        aliases: Optional[List[str]] = None,
        description: str = "",
        frequency: int = 0,
        demand_score: float = 0.0,
        industry_score: float = 0.0,
        trend: Union[str, TechnologyTrend] = TechnologyTrend.STABLE,
        growth: float = 0.0,
        classification: Union[str, TechnologyClassification] = TechnologyClassification.SUPPORTING,
        role_coverage: Optional[Dict[str, float]] = None,
        source: str = "manual",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TechnologyKnowledgeRecord:
        """
        Create a new technology knowledge record.

        Args:
            canonical_name: Canonical display name.
            category: Canonical category string.
            aliases: Optional list of aliases.
            description: Optional description.
            frequency: Job mention count.
            demand_score: Demand score (0-100).
            industry_score: Industry score (0-100).
            trend: Trend enum or string.
            growth: Growth percentage.
            classification: Classification enum or string.
            role_coverage: Role to percentage mapping.
            source: Data source identifier.
            metadata: Arbitrary metadata dictionary.

        Returns:
            The created TechnologyKnowledgeRecord.

        Raises:
            ValidationError: If inputs fail validation.
            DuplicateTechnology: If a technology with the same ID already exists.
        """
        if not canonical_name or not canonical_name.strip():
            raise ValidationError("canonical_name must be a non-empty string.")
        if not category or not category.strip():
            raise ValidationError("category must be a non-empty string.")

        record = self._builder.build_single(
            canonical_name=canonical_name,
            category=category,
            aliases=aliases,
            description=description,
            frequency=frequency,
            demand_score=demand_score,
            industry_score=industry_score,
            trend=trend,
            growth=growth,
            classification=classification,
            role_coverage=role_coverage,
            source=source,
            metadata=metadata,
        )
        return self._repository.add(record)

    def update_technology(
        self,
        technology_id: str,
        **updates: Any,
    ) -> TechnologyKnowledgeRecord:
        """
        Update an existing technology record.

        Args:
            technology_id: The unique technology identifier.
            **updates: Fields and new values to apply.

        Returns:
            The updated TechnologyKnowledgeRecord with bumped patch version.

        Raises:
            TechnologyNotFound: If the technology ID does not exist.
            ValidationError: If updated record fields are invalid.
        """
        if not technology_id or not technology_id.strip():
            raise ValidationError("technology_id must be a non-empty string.")

        record = self._repository.get(technology_id)

        for field, value in updates.items():
            if field == "trend":
                value = self._builder._parse_trend(value)
            elif field == "classification":
                value = self._builder._parse_classification(value)
            elif field == "status":
                if isinstance(value, str):
                    for s in TechnologyStatus:
                        if s.value.lower() == value.lower():
                            value = s
                            break

            if hasattr(record, field) and field not in ("technology_id", "version", "first_seen"):
                setattr(record, field, value)

        return self._repository.update(record)

    def delete_technology(self, technology_id: str) -> bool:
        """
        Delete a technology record by ID.

        Args:
            technology_id: The unique technology identifier.

        Returns:
            True if deleted, False if not found.

        Raises:
            ValidationError: If technology_id is invalid.
        """
        if not technology_id or not technology_id.strip():
            raise ValidationError("technology_id must be a non-empty string.")
        return self._repository.delete(technology_id)

    def get_technology(self, technology_id: str) -> TechnologyKnowledgeRecord:
        """
        Retrieve a technology record by ID.

        Args:
            technology_id: The unique technology identifier.

        Returns:
            The matching TechnologyKnowledgeRecord.

        Raises:
            TechnologyNotFound: If no record matches the ID.
        """
        if not technology_id or not technology_id.strip():
            raise ValidationError("technology_id must be a non-empty string.")
        return self._repository.get(technology_id)

    def get_all(self) -> List[TechnologyKnowledgeRecord]:
        """Return all technology records."""
        return self._repository.get_all()

    def get_all_technologies(self) -> List[TechnologyKnowledgeRecord]:
        """Alias for get_all()."""
        return self.get_all()

    def exists(self, technology_id: str) -> bool:
        """Check if a technology exists in the repository."""
        return self._repository.exists(technology_id)

    def count(self) -> int:
        """Return the total number of technology records."""
        return self._repository.count()

    # ------------------------------------------------------------------
    # Search and Filtering
    # ------------------------------------------------------------------

    def search(self, query: str) -> List[TechnologyKnowledgeRecord]:
        """
        Search technologies by canonical name, technology_id, or aliases.

        Args:
            query: Search query string.

        Returns:
            Matching records sorted by industry_score descending.
        """
        return self._repository.search(query)

    def filter_by_category(self, category: str) -> List[TechnologyKnowledgeRecord]:
        """Filter technologies by canonical category string."""
        return self._repository.filter_by_category(category)

    def filter_by_trend(self, trend: Union[str, TechnologyTrend]) -> List[TechnologyKnowledgeRecord]:
        """Filter technologies by trend direction."""
        parsed_trend = self._builder._parse_trend(trend)
        return self._repository.filter_by_trend(parsed_trend)

    def filter_by_classification(
        self, classification: Union[str, TechnologyClassification]
    ) -> List[TechnologyKnowledgeRecord]:
        """Filter technologies by lifecycle classification."""
        parsed_class = self._builder._parse_classification(classification)
        return self._repository.filter_by_classification(parsed_class)

    def filter_by_status(self, status: Union[str, TechnologyStatus]) -> List[TechnologyKnowledgeRecord]:
        """Filter technologies by lifecycle status."""
        parsed_status = TechnologyStatus.ACTIVE
        if isinstance(status, TechnologyStatus):
            parsed_status = status
        elif isinstance(status, str):
            for s in TechnologyStatus:
                if s.value.lower() == status.lower():
                    parsed_status = s
                    break
        return self._repository.filter_by_status(parsed_status)

    def get_trending(self, limit: int = 10) -> List[TechnologyKnowledgeRecord]:
        """Get top technologies with rising or emerging trends."""
        return self._repository.get_trending(limit=limit)

    def get_emerging(self, limit: int = 10) -> List[TechnologyKnowledgeRecord]:
        """Get top technologies classified as Emerging."""
        return self._repository.get_emerging(limit=limit)

    def get_core(self, limit: int = 10) -> List[TechnologyKnowledgeRecord]:
        """Get top technologies classified as Core."""
        return self._repository.get_core(limit=limit)

    # ------------------------------------------------------------------
    # Pipeline Ingestion & Refresh
    # ------------------------------------------------------------------

    def ingest_pipeline_outputs(
        self,
        normalized_techs: Any,
        frequency_data: Optional[Any] = None,
        demand_data: Optional[Any] = None,
        source: str = "pipeline",
        auto_snapshot: bool = True,
    ) -> Tuple[int, int, Optional[KnowledgeSnapshot]]:
        """
        Ingest outputs from previous pipeline stages (Normalization, Frequency, Demand).

        Args:
            normalized_techs: NormalizationResult or list of dicts.
            frequency_data: Optional FrequencyReport or dict.
            demand_data: Optional IndustryReport or dict.
            source: Identifier for data source.
            auto_snapshot: Whether to automatically create a snapshot after ingestion.

        Returns:
            Tuple of (created_count, updated_count, snapshot_or_none).
        """
        records = self._builder.build(
            normalization_result=normalized_techs,
            frequency_report=frequency_data,
            industry_report=demand_data,
            source=source,
        )
        created, updated = self._repository.upsert_batch(records)
        self.refresh()

        snapshot = None
        if auto_snapshot:
            snapshot = self.create_snapshot(
                description=f"Auto-snapshot after pipeline ingestion ({source})",
            )

        logger.info(
            "[Knowledge] Pipeline ingestion complete: %d created, %d updated.",
            created,
            updated,
        )
        return created, updated, snapshot

    def refresh(self) -> int:
        """
        Recompute relationships and cross-field mappings across all records.

        Returns:
            Number of records refreshed.
        """
        all_records = self._repository.get_all()
        self._builder.compute_related_technologies(all_records)
        logger.info("[Knowledge] Refreshed cross-references for %d technologies.", len(all_records))
        return len(all_records)

    # ------------------------------------------------------------------
    # Snapshot Operations
    # ------------------------------------------------------------------

    def create_snapshot(
        self,
        execution_summary: Optional[Dict[str, Any]] = None,
        description: str = "",
    ) -> KnowledgeSnapshot:
        """
        Create a new immutable snapshot of current repository state.

        Args:
            execution_summary: Optional summary of pipeline run.
            description: Human-readable description.

        Returns:
            The created KnowledgeSnapshot.
        """
        records = self._repository.get_records_for_snapshot()
        return self._snapshot_manager.create_snapshot(
            records=records,
            execution_summary=execution_summary,
            description=description,
        )

    def get_snapshot(self, snapshot_id: str) -> KnowledgeSnapshot:
        """Retrieve a snapshot by ID."""
        return self._snapshot_manager.get_snapshot(snapshot_id)

    def get_active_snapshot(self) -> Optional[KnowledgeSnapshot]:
        """Get the current active snapshot, or None if none exist."""
        return self._snapshot_manager.get_active_snapshot()

    def list_snapshots(self) -> List[SnapshotMetadata]:
        """List all stored snapshots (newest first)."""
        return self._snapshot_manager.list_snapshots()

    def compare_snapshots(
        self, snapshot_id_a: str, snapshot_id_b: str
    ) -> SnapshotComparison:
        """Compare two snapshots and return difference metrics."""
        return self._snapshot_manager.compare_snapshots(snapshot_id_a, snapshot_id_b)

    def rollback_snapshot(
        self, snapshot_id: str, auto_snapshot: bool = True
    ) -> Tuple[int, Optional[KnowledgeSnapshot]]:
        """
        Rollback repository state to a historical snapshot.

        Never overwrites snapshot history; returns snapshot records into active
        repository state and optionally snapshots pre-rollback state first.

        Args:
            snapshot_id: Target snapshot identifier.
            auto_snapshot: Whether to take pre-rollback snapshot.

        Returns:
            Tuple of (records_loaded_count, pre_rollback_snapshot_or_none).
        """
        pre_snapshot = None
        if auto_snapshot:
            pre_snapshot = self.create_snapshot(
                description=f"Pre-rollback snapshot before rolling back to {snapshot_id}"
            )

        records = self._snapshot_manager.rollback_records(snapshot_id)
        loaded = self._repository.load_from_snapshot(records)

        logger.info("[Knowledge] Rolled back repository state to %s (%d records loaded).", snapshot_id, loaded)
        return loaded, pre_snapshot

    def rollback_to_snapshot(
        self, snapshot_id: str, auto_snapshot: bool = True
    ) -> Tuple[int, Optional[KnowledgeSnapshot]]:
        """Alias for rollback_snapshot()."""
        return self.rollback_snapshot(snapshot_id, auto_snapshot=auto_snapshot)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_statistics(self) -> KnowledgeStats:
        """Compute aggregate knowledge layer statistics."""
        active_snap = self.get_active_snapshot()
        latest_id = active_snap.metadata.snapshot_id if active_snap else None
        return self._repository.get_stats(
            snapshot_count=self._snapshot_manager.count(),
            latest_snapshot_id=latest_id,
        )

    # ------------------------------------------------------------------
    # Persistence & Maintenance
    # ------------------------------------------------------------------

    def save(
        self, repo_path: Optional[str] = None, snap_path: Optional[str] = None
    ) -> Dict[str, Path]:
        """
        Save repository state and snapshots to disk.

        Args:
            repo_path: Optional repository file path override.
            snap_path: Optional snapshot file path override.

        Returns:
            Dict mapping 'repository' and 'snapshots' to written file paths.
        """
        repo_file = self._repository.save(repo_path)
        snap_file = self._snapshot_manager.save(snap_path)
        return {"repository": repo_file, "snapshots": snap_file}

    def save_all(
        self, repo_path: Optional[str] = None, snap_path: Optional[str] = None
    ) -> Dict[str, Path]:
        """Alias for save()."""
        return self.save(repo_path, snap_path)

    def load(
        self, repo_path: Optional[str] = None, snap_path: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Load repository state and snapshots from disk.

        Args:
            repo_path: Optional repository file path override.
            snap_path: Optional snapshot file path override.

        Returns:
            Dict mapping 'repository' and 'snapshots' to record/snapshot counts.
        """
        repo_count = self._repository.load(repo_path)
        snap_count = self._snapshot_manager.load(snap_path)
        return {"repository": repo_count, "snapshots": snap_count}

    def load_all(
        self, repo_path: Optional[str] = None, snap_path: Optional[str] = None
    ) -> Dict[str, int]:
        """Alias for load()."""
        return self.load(repo_path, snap_path)

    def clear(self) -> int:
        """Clear all records from the repository."""
        return self._repository.clear()
