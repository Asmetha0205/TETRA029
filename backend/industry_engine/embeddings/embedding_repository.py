"""
Embedding Repository for the CurricuAlign AI Embedding Engine.

Provides thread-safe in-memory storage with optional JSON file persistence
for EmbeddingRecord objects. Designed with the Repository pattern to decouple
business logic from the backing store (ready for future PostgreSQL migration).
"""

import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from backend.industry_engine.embeddings.exceptions import (
    EmbeddingRepositoryError,
    EmbeddingValidationError,
)
from backend.industry_engine.embeddings.embedding_models import (
    EmbeddingRecord,
    EmbeddingStats,
    EmbeddingStatus,
)
from backend.industry_engine.embeddings.embedding_validator import EmbeddingValidator

logger = logging.getLogger("industry_engine.embeddings.embedding_repository")


class EmbeddingRepository:
    """
    In-memory repository for technology embedding records with JSON file persistence.

    Thread-safe via reentrant lock. Exposes CRUD operations, batch methods,
    filtering, searching, and disk serialization.
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        validator: Optional[EmbeddingValidator] = None,
    ) -> None:
        """
        Initialize the embedding repository.

        Args:
            storage_path: Optional path for JSON disk persistence.
            validator: Optional EmbeddingValidator instance.
        """
        self._records_by_tech_id: Dict[str, EmbeddingRecord] = {}
        self._records_by_emb_id: Dict[str, EmbeddingRecord] = {}
        self._lock = threading.RLock()
        self._storage_path = Path(storage_path) if storage_path else None
        self._validator = validator or EmbeddingValidator()

        if self._storage_path and self._storage_path.exists():
            self.load()

        logger.info(
            "[Embedding] Repository initialized with %d records%s.",
            len(self._records_by_tech_id),
            f" (storage: {self._storage_path})" if self._storage_path else "",
        )

    # ------------------------------------------------------------------
    # CRUD Operations
    # ------------------------------------------------------------------

    def add(self, record: EmbeddingRecord) -> EmbeddingRecord:
        """
        Add a new embedding record to the repository.

        Args:
            record: The EmbeddingRecord to add.

        Returns:
            The added EmbeddingRecord.

        Raises:
            EmbeddingValidationError: If validation fails.
            EmbeddingRepositoryError: If a record with the same ID already exists.
        """
        self._validator.validate_record(record)
        with self._lock:
            if record.technology_id in self._records_by_tech_id:
                raise EmbeddingRepositoryError(
                    f"Embedding for technology_id '{record.technology_id}' already exists."
                )
            rec_copy = record.model_copy(deep=True)
            self._records_by_tech_id[record.technology_id] = rec_copy
            self._records_by_emb_id[record.embedding_id] = rec_copy

            logger.info("[Embedding] Repository added embedding for '%s'.", record.technology_id)
            return rec_copy

    def add_batch(self, records: List[EmbeddingRecord]) -> Tuple[List[EmbeddingRecord], int]:
        """
        Add multiple records in batch, skipping duplicates.

        Args:
            records: List of EmbeddingRecord objects.

        Returns:
            Tuple of (added_records, duplicate_count).
        """
        added = []
        dup_count = 0
        for rec in records:
            try:
                added_rec = self.add(rec)
                added.append(added_rec)
            except EmbeddingRepositoryError:
                dup_count += 1
            except EmbeddingValidationError as exc:
                logger.warning("[Embedding] Skipping invalid record in batch: %s", exc)

        logger.info("[Embedding] Batch add: %d added, %d duplicates skipped.", len(added), dup_count)
        return added, dup_count

    def get(self, technology_id: str) -> Optional[EmbeddingRecord]:
        """
        Retrieve an embedding record by technology_id.

        Args:
            technology_id: Target technology identifier.

        Returns:
            Deep copy of matching EmbeddingRecord, or None if not found.
        """
        with self._lock:
            rec = self._records_by_tech_id.get(technology_id)
            return rec.model_copy(deep=True) if rec else None

    def get_by_embedding_id(self, embedding_id: str) -> Optional[EmbeddingRecord]:
        """
        Retrieve an embedding record by embedding_id.

        Args:
            embedding_id: Target embedding record identifier.

        Returns:
            Deep copy of matching EmbeddingRecord, or None.
        """
        with self._lock:
            rec = self._records_by_emb_id.get(embedding_id)
            return rec.model_copy(deep=True) if rec else None

    def update(self, record: EmbeddingRecord) -> EmbeddingRecord:
        """
        Update an existing embedding record.

        Args:
            record: The updated EmbeddingRecord.

        Returns:
            The updated EmbeddingRecord.

        Raises:
            EmbeddingRepositoryError: If record does not exist.
        """
        self._validator.validate_record(record)
        with self._lock:
            if record.technology_id not in self._records_by_tech_id:
                raise EmbeddingRepositoryError(
                    f"Cannot update: embedding for technology_id '{record.technology_id}' not found."
                )
            rec_copy = record.model_copy(deep=True)
            rec_copy.touch()
            self._records_by_tech_id[record.technology_id] = rec_copy
            self._records_by_emb_id[record.embedding_id] = rec_copy

            logger.info("[Embedding] Updated repository record for '%s'.", record.technology_id)
            return rec_copy

    def upsert(self, record: EmbeddingRecord) -> Tuple[EmbeddingRecord, bool]:
        """
        Insert or update an embedding record.

        Args:
            record: The EmbeddingRecord to insert or update.

        Returns:
            Tuple of (record, was_created).
        """
        self._validator.validate_record(record)
        with self._lock:
            existing = self._records_by_tech_id.get(record.technology_id)
            rec_copy = record.model_copy(deep=True)
            if existing is not None:
                rec_copy.touch()
                self._records_by_tech_id[record.technology_id] = rec_copy
                self._records_by_emb_id[record.embedding_id] = rec_copy
                logger.debug("[Embedding] Upserted (updated) '%s'.", record.technology_id)
                return rec_copy, False
            else:
                self._records_by_tech_id[record.technology_id] = rec_copy
                self._records_by_emb_id[record.embedding_id] = rec_copy
                logger.info("[Embedding] Upserted (created) '%s'.", record.technology_id)
                return rec_copy, True

    def delete(self, technology_id: str) -> bool:
        """
        Delete an embedding record by technology_id.

        Args:
            technology_id: Target technology identifier.

        Returns:
            True if deleted, False if not found.
        """
        with self._lock:
            rec = self._records_by_tech_id.pop(technology_id, None)
            if rec:
                self._records_by_emb_id.pop(rec.embedding_id, None)
                logger.info("[Embedding] Deleted embedding for '%s'.", technology_id)
                return True
            return False

    def exists(self, technology_id: str) -> bool:
        """Check if an embedding exists for technology_id."""
        with self._lock:
            return technology_id in self._records_by_tech_id

    def count(self) -> int:
        """Return total number of embedding records."""
        with self._lock:
            return len(self._records_by_tech_id)

    def get_all(self) -> List[EmbeddingRecord]:
        """Return deep copies of all stored embedding records."""
        with self._lock:
            return [r.model_copy(deep=True) for r in self._records_by_tech_id.values()]

    def search_by_technology_id(self, query: str) -> List[EmbeddingRecord]:
        """
        Search embedding records by partial technology_id or embedding_id.

        Args:
            query: Search query string.

        Returns:
            Matching EmbeddingRecord list.
        """
        query_lower = query.strip().lower()
        if not query_lower:
            return self.get_all()

        with self._lock:
            results = []
            for rec in self._records_by_tech_id.values():
                if (
                    query_lower in rec.technology_id.lower()
                    or query_lower in rec.embedding_id.lower()
                ):
                    results.append(rec.model_copy(deep=True))
            return results

    def filter_by_status(self, status: EmbeddingStatus) -> List[EmbeddingRecord]:
        """Filter embedding records by status enum."""
        with self._lock:
            return [
                r.model_copy(deep=True)
                for r in self._records_by_tech_id.values()
                if r.status == status
            ]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: Optional[str] = None) -> Path:
        """
        Save all embedding records to a JSON file.

        Args:
            path: Optional file path override.

        Returns:
            Path to written file.

        Raises:
            EmbeddingRepositoryError: If save fails.
        """
        save_path = Path(path) if path else self._storage_path
        if save_path is None:
            raise EmbeddingRepositoryError("No storage path configured for repository save.")

        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with self._lock:
                data = {
                    "records": [r.model_dump() for r in self._records_by_tech_id.values()]
                }
            save_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
            logger.info("[Embedding] Saved %d embedding records to %s.", len(data["records"]), save_path)
            return save_path
        except Exception as exc:
            raise EmbeddingRepositoryError(f"Failed to save embedding repository: {exc}") from exc

    def load(self, path: Optional[str] = None) -> int:
        """
        Load embedding records from a JSON file.

        Args:
            path: Optional file path override.

        Returns:
            Number of records loaded.

        Raises:
            EmbeddingRepositoryError: If load fails.
        """
        load_path = Path(path) if path else self._storage_path
        if load_path is None:
            raise EmbeddingRepositoryError("No storage path configured for repository load.")

        if not load_path.exists():
            logger.warning("[Embedding] Load requested but file does not exist: %s", load_path)
            return 0

        try:
            raw = json.loads(load_path.read_text(encoding="utf-8"))
            records = [EmbeddingRecord(**r) for r in raw.get("records", [])]
            with self._lock:
                self._records_by_tech_id.clear()
                self._records_by_emb_id.clear()
                for rec in records:
                    self._records_by_tech_id[rec.technology_id] = rec
                    self._records_by_emb_id[rec.embedding_id] = rec
            logger.info("[Embedding] Loaded %d embedding records from %s.", len(records), load_path)
            return len(records)
        except Exception as exc:
            raise EmbeddingRepositoryError(f"Failed to load embedding repository: {exc}") from exc

    def clear(self) -> int:
        """Clear all records from the repository."""
        with self._lock:
            count = len(self._records_by_tech_id)
            self._records_by_tech_id.clear()
            self._records_by_emb_id.clear()
            logger.info("[Embedding] Cleared %d repository records.", count)
            return count

    def get_stats(self) -> EmbeddingStats:
        """Get aggregate repository statistics."""
        with self._lock:
            records = list(self._records_by_tech_id.values())
            active = sum(1 for r in records if r.status == EmbeddingStatus.ACTIVE)
            outdated = sum(1 for r in records if r.status == EmbeddingStatus.OUTDATED)
            archived = sum(1 for r in records if r.status == EmbeddingStatus.ARCHIVED)

            dim = records[0].embedding_dimension if records else 384
            model = records[0].model_name if records else "all-MiniLM-L6-v2"

            return EmbeddingStats(
                total_embeddings=len(records),
                active_count=active,
                outdated_count=outdated,
                archived_count=archived,
                model_name=model,
                embedding_dimension=dim,
            )
