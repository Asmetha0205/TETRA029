"""
Snapshot Manager for the CurricuAlign AI Industry Knowledge Layer.

Manages immutable snapshots of the knowledge layer state. Snapshots are
never modified after creation. Rollback creates a new active state derived
from a snapshot's data, preserving the full history.
"""

import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.industry_engine.knowledge.exceptions import (
    SnapshotComparisonError,
    SnapshotError,
    SnapshotNotFoundError,
)
from backend.industry_engine.knowledge.knowledge_models import (
    KnowledgeSnapshot,
    SnapshotComparison,
    SnapshotMetadata,
    SnapshotStatus,
    TechnologyKnowledgeRecord,
)

logger = logging.getLogger("industry_engine.knowledge.snapshot_manager")


class SnapshotManager:
    """
    Manages immutable knowledge snapshots.

    Snapshots capture the full state of the knowledge layer at a point in time.
    They support comparison, rollback (via new state creation), and persistence.
    """

    def __init__(self, storage_path: Optional[str] = None, max_snapshots: int = 52) -> None:
        """
        Initialize the snapshot manager.

        Args:
            storage_path: Optional file path for snapshot persistence.
            max_snapshots: Maximum number of snapshots to retain before pruning.
        """
        self._snapshots: Dict[str, KnowledgeSnapshot] = {}
        self._snapshot_counter: int = 0
        self._storage_path = Path(storage_path) if storage_path else None
        self._max_snapshots = max_snapshots

        if self._storage_path and self._storage_path.exists():
            self._load_from_disk()

        logger.info(
            "[Snapshot] Snapshot Manager initialized with %d existing snapshots.",
            len(self._snapshots),
        )

    def create_snapshot(
        self,
        records: List[TechnologyKnowledgeRecord],
        execution_summary: Optional[Dict[str, Any]] = None,
        description: str = "",
    ) -> KnowledgeSnapshot:
        """
        Create a new immutable snapshot from the current set of records.

        Args:
            records: The complete list of technology records to snapshot.
            execution_summary: Optional summary of the pipeline execution.
            description: Optional human-readable description.

        Returns:
            The newly created KnowledgeSnapshot.
        """
        self._snapshot_counter += 1
        snapshot_id = f"snapshot-{self._snapshot_counter:06d}"

        metadata = SnapshotMetadata(
            snapshot_id=snapshot_id,
            version=self._snapshot_counter,
            technology_count=len(records),
            status=SnapshotStatus.ACTIVE,
            execution_summary=execution_summary or {},
            description=description,
        )

        snapshot = KnowledgeSnapshot(
            metadata=metadata,
            records=[r.model_copy(deep=True) for r in records],
        )

        self._mark_previous_snapshots_superseded()
        self._snapshots[snapshot_id] = snapshot

        logger.info(
            "[Snapshot] Created Snapshot: %s with %d technologies (v%d).",
            snapshot_id,
            len(records),
            self._snapshot_counter,
        )
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> KnowledgeSnapshot:
        """
        Retrieve a snapshot by ID.

        Args:
            snapshot_id: The unique snapshot identifier.

        Returns:
            The matching KnowledgeSnapshot.

        Raises:
            SnapshotNotFoundError: If no snapshot with the given ID exists.
        """
        snapshot = self._snapshots.get(snapshot_id)
        if snapshot is None:
            raise SnapshotNotFoundError(f"Snapshot '{snapshot_id}' not found.")
        return snapshot

    def get_active_snapshot(self) -> Optional[KnowledgeSnapshot]:
        """
        Get the most recent active snapshot.

        Returns:
            The active KnowledgeSnapshot, or None if no snapshots exist.
        """
        for snapshot in reversed(list(self._snapshots.values())):
            if snapshot.metadata.status == SnapshotStatus.ACTIVE:
                return snapshot
        return None

    def list_snapshots(self) -> List[SnapshotMetadata]:
        """
        List all snapshots sorted by version (newest first).

        Returns:
            List of SnapshotMetadata for all stored snapshots.
        """
        snapshots = sorted(
            self._snapshots.values(),
            key=lambda s: s.metadata.version,
            reverse=True,
        )
        return [s.metadata for s in snapshots]

    def compare_snapshots(self, snapshot_id_a: str, snapshot_id_b: str) -> SnapshotComparison:
        """
        Compare two snapshots and identify differences.

        Args:
            snapshot_id_a: ID of the first (older) snapshot.
            snapshot_id_b: ID of the second (newer) snapshot.

        Returns:
            A SnapshotComparison with added, removed, and changed technologies.

        Raises:
            SnapshotNotFoundError: If either snapshot ID is not found.
            SnapshotComparisonError: If comparison cannot be performed.
        """
        snap_a = self.get_snapshot(snapshot_id_a)
        snap_b = self.get_snapshot(snapshot_id_b)

        ids_a = {r.technology_id for r in snap_a.records}
        ids_b = {r.technology_id for r in snap_b.records}

        added_ids = ids_b - ids_a
        removed_ids = ids_a - ids_b
        common_ids = ids_a & ids_b

        records_a_map = {r.technology_id: r for r in snap_a.records}
        records_b_map = {r.technology_id: r for r in snap_b.records}

        changed: List[Dict[str, Any]] = []
        unchanged_count = 0

        for tech_id in common_ids:
            rec_a = records_a_map[tech_id]
            rec_b = records_b_map[tech_id]
            diffs = self._compute_diff(rec_a, rec_b)
            if diffs:
                changed.append({
                    "technology_id": tech_id,
                    "canonical_name": rec_b.canonical_name,
                    "changes": diffs,
                })
            else:
                unchanged_count += 1

        comparison = SnapshotComparison(
            snapshot_a_id=snapshot_id_a,
            snapshot_b_id=snapshot_id_b,
            added=sorted(added_ids),
            removed=sorted(removed_ids),
            changed=changed,
            unchanged=unchanged_count,
            summary={
                "total_a": len(ids_a),
                "total_b": len(ids_b),
                "added": len(added_ids),
                "removed": len(removed_ids),
                "changed": len(changed),
                "unchanged": unchanged_count,
            },
        )

        logger.info(
            "[Snapshot] Compared %s vs %s: +%d, -%d, ~%d, =%d.",
            snapshot_id_a,
            snapshot_id_b,
            len(added_ids),
            len(removed_ids),
            len(changed),
            unchanged_count,
        )
        return comparison

    def rollback_records(self, snapshot_id: str) -> List[TechnologyKnowledgeRecord]:
        """
        Get the records from a snapshot for rollback purposes.

        This does NOT overwrite history; it returns the records so the caller
        can create a new active state from them.

        Args:
            snapshot_id: The snapshot to rollback to.

        Returns:
            Deep copy of the records from the snapshot.

        Raises:
            SnapshotNotFoundError: If the snapshot ID is not found.
        """
        snapshot = self.get_snapshot(snapshot_id)
        records = [r.model_copy(deep=True) for r in snapshot.records]

        logger.info(
            "[Snapshot] Rollback requested to %s: returning %d records.",
            snapshot_id,
            len(records),
        )
        return records

    def prune(self, keep: Optional[int] = None) -> int:
        """
        Remove old snapshots beyond the retention limit.

        Args:
            keep: Number of most recent snapshots to keep. Defaults to max_snapshots.

        Returns:
            Number of snapshots removed.
        """
        max_keep = keep or self._max_snapshots
        all_snapshots = sorted(
            self._snapshots.values(),
            key=lambda s: s.metadata.version,
            reverse=True,
        )
        if len(all_snapshots) <= max_keep:
            return 0

        to_remove = all_snapshots[max_keep:]
        removed_count = 0
        for snap in to_remove:
            if snap.metadata.snapshot_id in self._snapshots:
                del self._snapshots[snap.metadata.snapshot_id]
                removed_count += 1

        if removed_count:
            logger.info("[Snapshot] Pruned %d old snapshots.", removed_count)
        return removed_count

    def count(self) -> int:
        """Return the number of stored snapshots."""
        return len(self._snapshots)

    def save(self, path: Optional[str] = None) -> Path:
        """
        Save all snapshots to a JSON file.

        Args:
            path: Optional override for the storage path.

        Returns:
            Path to the written file.

        Raises:
            SnapshotError: If the save operation fails.
        """
        save_path = Path(path) if path else self._storage_path
        if save_path is None:
            raise SnapshotError("No storage path configured.")

        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "snapshot_counter": self._snapshot_counter,
                "snapshots": {
                    sid: snap.to_dict() for sid, snap in self._snapshots.items()
                },
            }
            save_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
            logger.info("[Snapshot] Saved %d snapshots to %s.", len(self._snapshots), save_path)
            return save_path
        except Exception as exc:
            raise SnapshotError(f"Failed to save snapshots: {exc}") from exc

    def load(self, path: Optional[str] = None) -> int:
        """
        Load snapshots from a JSON file.

        Args:
            path: Optional override for the storage path.

        Returns:
            Number of snapshots loaded.

        Raises:
            SnapshotError: If the load operation fails.
        """
        load_path = Path(path) if path else self._storage_path
        if load_path is None:
            raise SnapshotError("No storage path configured.")
        if not load_path.exists():
            return 0
        self._load_from_disk(load_path)
        return len(self._snapshots)

    def _load_from_disk(self, path: Optional[Path] = None) -> None:
        """Internal method to load snapshots from disk."""
        load_path = path or self._storage_path
        if load_path is None or not load_path.exists():
            return
        try:
            raw = json.loads(load_path.read_text(encoding="utf-8"))
            self._snapshot_counter = raw.get("snapshot_counter", 0)
            self._snapshots.clear()
            for sid, snap_data in raw.get("snapshots", {}).items():
                self._snapshots[sid] = KnowledgeSnapshot.from_dict(snap_data)
            logger.info("[Snapshot] Loaded %d snapshots from %s.", len(self._snapshots), load_path)
        except Exception as exc:
            logger.error("[Snapshot] Failed to load from %s: %s", load_path, exc)
            raise SnapshotError(f"Failed to load snapshots: {exc}") from exc

    def _mark_previous_snapshots_superseded(self) -> None:
        """Mark all active snapshots as superseded when a new one is created."""
        for snap in self._snapshots.values():
            if snap.metadata.status == SnapshotStatus.ACTIVE:
                snap.metadata.status = SnapshotStatus.SUPERSEDED

    @staticmethod
    def _compute_diff(
        record_a: TechnologyKnowledgeRecord,
        record_b: TechnologyKnowledgeRecord,
    ) -> Dict[str, Any]:
        """
        Compute differences between two versions of a record.

        Returns:
            Dictionary of changed fields with their old and new values.
        """
        fields_to_compare = [
            "canonical_name", "category", "description", "frequency",
            "demand_score", "industry_score", "trend", "growth",
            "classification", "status",
        ]
        diffs: Dict[str, Any] = {}
        for field in fields_to_compare:
            val_a = getattr(record_a, field)
            val_b = getattr(record_b, field)
            if val_a != val_b:
                diffs[field] = {"old": val_a, "new": val_b}

        if set(record_a.aliases) != set(record_b.aliases):
            diffs["aliases"] = {"old": sorted(record_a.aliases), "new": sorted(record_b.aliases)}

        if set(record_a.related_technologies) != set(record_b.related_technologies):
            diffs["related_technologies"] = {
                "old": sorted(record_a.related_technologies),
                "new": sorted(record_b.related_technologies),
            }

        if record_a.role_coverage != record_b.role_coverage:
            diffs["role_coverage"] = {"old": record_a.role_coverage, "new": record_b.role_coverage}

        if record_a.version.to_string() != record_b.version.to_string():
            diffs["version"] = {"old": record_a.version.to_string(), "new": record_b.version.to_string()}

        return diffs
