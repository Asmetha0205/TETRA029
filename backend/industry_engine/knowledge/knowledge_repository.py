"""
Knowledge Repository for the CurricuAlign AI Industry Knowledge Layer.

Provides in-memory storage with JSON file persistence for technology
knowledge records. Designed with the Repository pattern so it can be
replaced with PostgreSQL or any other backing store without changing
the service layer above it.
"""

import json
import logging
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from backend.industry_engine.knowledge.exceptions import (
    DuplicateTechnology,
    RepositoryError,
    TechnologyNotFound,
    ValidationError,
)
from backend.industry_engine.knowledge.knowledge_models import (
    KnowledgeStats,
    KnowledgeSnapshot,
    SnapshotMetadata,
    SnapshotStatus,
    TechnologyClassification,
    TechnologyKnowledgeRecord,
    TechnologyStatus,
    TechnologyTrend,
)
from backend.industry_engine.knowledge.version_manager import VersionManager

logger = logging.getLogger("industry_engine.knowledge.knowledge_repository")


class KnowledgeRepository:
    """
    In-memory repository for technology knowledge records with JSON persistence.

    Thread-safe via a reentrant lock. All mutations go through the lock.
    The public API exposes only domain operations; the storage mechanism
    can be swapped without touching callers.
    """

    def __init__(self, storage_path: Optional[str] = None) -> None:
        """
        Initialize the repository.

        Args:
            storage_path: Optional file path for JSON persistence.
                          If None, operates in memory-only mode.
        """
        self._records: Dict[str, TechnologyKnowledgeRecord] = {}
        self._lock = threading.RLock()
        self._storage_path = Path(storage_path) if storage_path else None
        self._version_manager = VersionManager()

        if self._storage_path and self._storage_path.exists():
            self._load_from_disk()

        logger.info(
            "[Knowledge] Repository initialized with %d records%s.",
            len(self._records),
            f" (storage: {self._storage_path})" if self._storage_path else "",
        )

    # ------------------------------------------------------------------
    # CRUD Operations
    # ------------------------------------------------------------------

    def add(self, record: TechnologyKnowledgeRecord) -> TechnologyKnowledgeRecord:
        """
        Add a new technology record to the repository.

        Args:
            record: The TechnologyKnowledgeRecord to add.

        Returns:
            The added record.

        Raises:
            DuplicateTechnology: If a record with the same technology_id already exists.
            ValidationError: If the record fails validation.
        """
        self._validate_record(record)
        with self._lock:
            if record.technology_id in self._records:
                raise DuplicateTechnology(
                    f"Technology '{record.canonical_name}' (id='{record.technology_id}') "
                    f"already exists in the repository."
                )
            self._records[record.technology_id] = record
            self._version_manager.set_version(record.technology_id, record.version)
            logger.info(
                "[Knowledge] Created Technology: %s (%s) in category '%s'.",
                record.canonical_name,
                record.technology_id,
                record.category,
            )
        return record

    def add_batch(self, records: List[TechnologyKnowledgeRecord]) -> Tuple[List[TechnologyKnowledgeRecord], int]:
        """
        Add multiple records, skipping duplicates.

        Args:
            records: List of TechnologyKnowledgeRecord objects.

        Returns:
            Tuple of (added_records, duplicate_count).
        """
        added = []
        dup_count = 0
        for record in records:
            try:
                self.add(record)
                added.append(record)
            except DuplicateTechnology:
                dup_count += 1
        if dup_count:
            logger.info("[Knowledge] Batch add: %d added, %d duplicates skipped.", len(added), dup_count)
        return added, dup_count

    def get(self, technology_id: str) -> TechnologyKnowledgeRecord:
        """
        Get a technology record by ID.

        Args:
            technology_id: The unique technology identifier.

        Returns:
            The matching TechnologyKnowledgeRecord.

        Raises:
            TechnologyNotFound: If no record matches the ID.
        """
        with self._lock:
            record = self._records.get(technology_id)
            if record is None:
                raise TechnologyNotFound(f"Technology with id '{technology_id}' not found.")
            return record

    def get_optional(self, technology_id: str) -> Optional[TechnologyKnowledgeRecord]:
        """
        Get a technology record by ID, returning None if not found.

        Args:
            technology_id: The unique technology identifier.

        Returns:
            The matching record, or None.
        """
        with self._lock:
            return self._records.get(technology_id)

    def update(self, record: TechnologyKnowledgeRecord) -> TechnologyKnowledgeRecord:
        """
        Update an existing technology record.

        The record must already exist. The version is automatically incremented.

        Args:
            record: The updated TechnologyKnowledgeRecord.

        Returns:
            The updated record with incremented version.

        Raises:
            TechnologyNotFound: If no record with the given ID exists.
            ValidationError: If the record fails validation.
        """
        self._validate_record(record)
        with self._lock:
            existing = self._records.get(record.technology_id)
            if existing is None:
                raise TechnologyNotFound(
                    f"Cannot update: technology '{record.technology_id}' not found."
                )
            record.version = self._version_manager.increment(record.technology_id, bump="patch")
            record.touch()
            self._records[record.technology_id] = record
            logger.info(
                "[Knowledge] Updated %s to version %s.",
                record.canonical_name,
                record.version.to_string(),
            )
        return record

    def upsert(self, record: TechnologyKnowledgeRecord) -> Tuple[TechnologyKnowledgeRecord, bool]:
        """
        Insert or update a technology record.

        Args:
            record: The TechnologyKnowledgeRecord to upsert.

        Returns:
            Tuple of (record, was_created).
        """
        with self._lock:
            existing = self._records.get(record.technology_id)
            if existing is not None:
                record.version = self._version_manager.increment(record.technology_id, bump="patch")
                record.touch()
                self._records[record.technology_id] = record
                logger.debug("[Knowledge] Upserted (updated) %s.", record.canonical_name)
                return record, False
            self._validate_record(record)
            self._records[record.technology_id] = record
            self._version_manager.set_version(record.technology_id, record.version)
            logger.info("[Knowledge] Upserted (created) %s.", record.canonical_name)
            return record, True

    def upsert_batch(self, records: List[TechnologyKnowledgeRecord]) -> Tuple[int, int]:
        """
        Upsert a batch of records.

        Args:
            records: List of TechnologyKnowledgeRecord objects.

        Returns:
            Tuple of (created_count, updated_count).
        """
        created = 0
        updated = 0
        for record in records:
            _, was_created = self.upsert(record)
            if was_created:
                created += 1
            else:
                updated += 1
        logger.info("[Knowledge] Batch upsert: %d created, %d updated.", created, updated)
        return created, updated

    def delete(self, technology_id: str) -> bool:
        """
        Delete a technology record by ID.

        Args:
            technology_id: The unique technology identifier.

        Returns:
            True if deleted, False if not found.
        """
        with self._lock:
            removed = self._records.pop(technology_id, None)
            if removed:
                self._version_manager.remove(technology_id)
                logger.info("[Knowledge] Deleted Technology: %s.", technology_id)
                return True
            logger.debug("[Knowledge] Delete skipped: '%s' not found.", technology_id)
            return False

    def count(self) -> int:
        """Return the total number of records in the repository."""
        with self._lock:
            return len(self._records)

    def exists(self, technology_id: str) -> bool:
        """Check if a technology exists in the repository."""
        with self._lock:
            return technology_id in self._records

    # ------------------------------------------------------------------
    # Search and Filtering
    # ------------------------------------------------------------------

    def get_all(self) -> List[TechnologyKnowledgeRecord]:
        """Return all technology records."""
        with self._lock:
            return list(self._records.values())

    def search(self, query: str) -> List[TechnologyKnowledgeRecord]:
        """
        Search technologies by name or alias (case-insensitive substring match).

        Args:
            query: The search string.

        Returns:
            List of matching records, sorted by industry_score descending.
        """
        query_lower = query.lower().strip()
        if not query_lower:
            return self.get_all()
        with self._lock:
            results = []
            for record in self._records.values():
                if (
                    query_lower in record.canonical_name.lower()
                    or query_lower in record.technology_id.lower()
                    or any(query_lower in alias.lower() for alias in record.aliases)
                ):
                    results.append(record)
            results.sort(key=lambda r: r.industry_score, reverse=True)
            return results

    def filter_by_category(self, category: str) -> List[TechnologyKnowledgeRecord]:
        """
        Filter technologies by category.

        Args:
            category: The category label to filter by.

        Returns:
            List of matching records.
        """
        with self._lock:
            return [
                r for r in self._records.values()
                if r.category.lower() == category.lower()
            ]

    def filter_by_trend(self, trend: TechnologyTrend) -> List[TechnologyKnowledgeRecord]:
        """
        Filter technologies by trend direction.

        Args:
            trend: The TechnologyTrend enum value.

        Returns:
            List of matching records.
        """
        with self._lock:
            return [r for r in self._records.values() if r.trend == trend]

    def filter_by_classification(self, classification: TechnologyClassification) -> List[TechnologyKnowledgeRecord]:
        """
        Filter technologies by classification.

        Args:
            classification: The TechnologyClassification enum value.

        Returns:
            List of matching records.
        """
        with self._lock:
            return [r for r in self._records.values() if r.classification == classification]

    def filter_by_status(self, status: TechnologyStatus) -> List[TechnologyKnowledgeRecord]:
        """
        Filter technologies by status.

        Args:
            status: The TechnologyStatus enum value.

        Returns:
            List of matching records.
        """
        with self._lock:
            return [r for r in self._records.values() if r.status == status]

    def get_trending(self, limit: int = 10) -> List[TechnologyKnowledgeRecord]:
        """
        Get technologies with rising or rapidly rising trends, sorted by score.

        Args:
            limit: Maximum number of results.

        Returns:
            List of trending technology records.
        """
        with self._lock:
            trending = [
                r for r in self._records.values()
                if r.trend in (TechnologyTrend.EMERGING, TechnologyTrend.RAPIDLY_RISING, TechnologyTrend.RISING)
                and r.status == TechnologyStatus.ACTIVE
            ]
            trending.sort(key=lambda r: r.industry_score, reverse=True)
            return trending[:limit]

    def get_emerging(self, limit: int = 10) -> List[TechnologyKnowledgeRecord]:
        """
        Get technologies classified as Emerging, sorted by score.

        Args:
            limit: Maximum number of results.

        Returns:
            List of emerging technology records.
        """
        with self._lock:
            emerging = [
                r for r in self._records.values()
                if r.classification == TechnologyClassification.EMERGING
                and r.status == TechnologyStatus.ACTIVE
            ]
            emerging.sort(key=lambda r: r.industry_score, reverse=True)
            return emerging[:limit]

    def get_core(self, limit: int = 10) -> List[TechnologyKnowledgeRecord]:
        """
        Get technologies classified as Core, sorted by score.

        Args:
            limit: Maximum number of results.

        Returns:
            List of core technology records.
        """
        with self._lock:
            core = [
                r for r in self._records.values()
                if r.classification == TechnologyClassification.CORE
                and r.status == TechnologyStatus.ACTIVE
            ]
            core.sort(key=lambda r: r.industry_score, reverse=True)
            return core[:limit]

    def get_by_ids(self, technology_ids: List[str]) -> List[TechnologyKnowledgeRecord]:
        """
        Retrieve multiple records by their IDs.

        Args:
            technology_ids: List of technology identifiers.

        Returns:
            List of matching records (skips IDs not found).
        """
        with self._lock:
            return [self._records[tid] for tid in technology_ids if tid in self._records]

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_stats(self, snapshot_count: int = 0, latest_snapshot_id: Optional[str] = None) -> KnowledgeStats:
        """
        Compute aggregate statistics over all records.

        Args:
            snapshot_count: Number of available snapshots.
            latest_snapshot_id: ID of the most recent snapshot.

        Returns:
            A populated KnowledgeStats model.
        """
        with self._lock:
            records = list(self._records.values())
            total = len(records)
            if total == 0:
                return KnowledgeStats(snapshot_count=snapshot_count, latest_snapshot_id=latest_snapshot_id)

            active = sum(1 for r in records if r.status == TechnologyStatus.ACTIVE)
            deprecated = sum(1 for r in records if r.status == TechnologyStatus.DEPRECATED)
            archived = sum(1 for r in records if r.status == TechnologyStatus.ARCHIVED)

            categories: Dict[str, int] = {}
            trends: Dict[str, int] = {}
            classifications: Dict[str, int] = {}
            total_demand = 0.0
            total_industry = 0.0
            total_frequency = 0

            for r in records:
                categories[r.category] = categories.get(r.category, 0) + 1
                trends[r.trend.value] = trends.get(r.trend.value, 0) + 1
                classifications[r.classification.value] = classifications.get(r.classification.value, 0) + 1
                total_demand += r.demand_score
                total_industry += r.industry_score
                total_frequency += r.frequency

            return KnowledgeStats(
                total_technologies=total,
                active_count=active,
                deprecated_count=deprecated,
                archived_count=archived,
                categories=categories,
                avg_demand_score=round(total_demand / total, 2),
                avg_industry_score=round(total_industry / total, 2),
                avg_frequency=round(total_frequency / total, 2),
                snapshot_count=snapshot_count,
                latest_snapshot_id=latest_snapshot_id,
                trend_distribution=trends,
                classification_distribution=classifications,
            )

    # ------------------------------------------------------------------
    # Snapshot Support
    # ------------------------------------------------------------------

    def get_records_for_snapshot(self) -> List[TechnologyKnowledgeRecord]:
        """Return a deep copy of all records for snapshot creation."""
        with self._lock:
            return [r.model_copy(deep=True) for r in self._records.values()]

    def load_from_snapshot(self, records: List[TechnologyKnowledgeRecord]) -> int:
        """
        Replace all current records with those from a snapshot.

        Args:
            records: The records to load.

        Returns:
            Number of records loaded.
        """
        with self._lock:
            self._records.clear()
            for record in records:
                self._records[record.technology_id] = record.model_copy(deep=True)
                self._version_manager.set_version(record.technology_id, record.version)
            logger.info(
                "[Knowledge] Loaded %d records from snapshot.",
                len(self._records),
            )
            return len(self._records)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: Optional[str] = None) -> Path:
        """
        Save all records to a JSON file.

        Args:
            path: Optional override for the storage path.

        Returns:
            Path to the written file.

        Raises:
            RepositoryError: If the save operation fails.
        """
        save_path = Path(path) if path else self._storage_path
        if save_path is None:
            raise RepositoryError("No storage path configured. Pass a path or set storage_path in constructor.")

        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            data = self._serialize()
            save_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
            logger.info("[Knowledge] Saved %d records to %s.", len(self._records), save_path)
            return save_path
        except Exception as exc:
            raise RepositoryError(f"Failed to save knowledge repository: {exc}") from exc

    def load(self, path: Optional[str] = None) -> int:
        """
        Load records from a JSON file, replacing current state.

        Args:
            path: Optional override for the storage path.

        Returns:
            Number of records loaded.

        Raises:
            RepositoryError: If the load operation fails.
        """
        load_path = Path(path) if path else self._storage_path
        if load_path is None:
            raise RepositoryError("No storage path configured.")
        if not load_path.exists():
            logger.warning("[Knowledge] Load requested but file does not exist: %s", load_path)
            return 0
        self._load_from_disk(load_path)
        return len(self._records)

    def _load_from_disk(self, path: Optional[Path] = None) -> None:
        """Internal method to load records from disk."""
        load_path = path or self._storage_path
        if load_path is None or not load_path.exists():
            return
        try:
            raw = json.loads(load_path.read_text(encoding="utf-8"))
            records = [
                TechnologyKnowledgeRecord(**r) for r in raw.get("records", [])
            ]
            with self._lock:
                self._records.clear()
                for record in records:
                    self._records[record.technology_id] = record
                    self._version_manager.set_version(record.technology_id, record.version)
            logger.info("[Knowledge] Loaded %d records from %s.", len(records), load_path)
        except Exception as exc:
            logger.error("[Knowledge] Failed to load from %s: %s", load_path, exc)
            raise RepositoryError(f"Failed to load knowledge repository: {exc}") from exc

    def _serialize(self) -> Dict[str, Any]:
        """Serialize the repository state to a dictionary."""
        return {
            "records": [r.model_dump() for r in self._records.values()],
            "version_manager": self._version_manager.to_dict(),
        }

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_record(self, record: TechnologyKnowledgeRecord) -> None:
        """
        Validate a record before insertion or update.

        Args:
            record: The record to validate.

        Raises:
            ValidationError: If validation fails.
        """
        if not record.technology_id or not record.technology_id.strip():
            raise ValidationError("technology_id must be a non-empty string.")
        if not record.canonical_name or not record.canonical_name.strip():
            raise ValidationError("canonical_name must be a non-empty string.")
        if not record.category or not record.category.strip():
            raise ValidationError("category must be a non-empty string.")
        if not (0 <= record.demand_score <= 100):
            raise ValidationError(f"demand_score must be between 0 and 100, got {record.demand_score}.")
        if not (0 <= record.industry_score <= 100):
            raise ValidationError(f"industry_score must be between 0 and 100, got {record.industry_score}.")
        if record.frequency < 0:
            raise ValidationError(f"frequency must be non-negative, got {record.frequency}.")

        seen_aliases = set()
        for alias in record.aliases:
            alias_lower = alias.lower().strip()
            if alias_lower in seen_aliases:
                raise ValidationError(f"Duplicate alias detected: '{alias}'.")
            seen_aliases.add(alias_lower)

    def clear(self) -> int:
        """
        Remove all records from the repository.

        Returns:
            Number of records removed.
        """
        with self._lock:
            count = len(self._records)
            self._records.clear()
            logger.info("[Knowledge] Cleared %d records.", count)
            return count
