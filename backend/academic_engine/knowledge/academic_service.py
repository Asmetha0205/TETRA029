"""
Academic Knowledge Service for CurricuAlign AI Academic Engine.

Business facade providing CRUD, snapshot, search, and statistics for Academic Knowledge.
"""

import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from backend.academic_engine.config.config import AcademicEngineConfig
from backend.academic_engine.knowledge.academic_builder import AcademicKnowledgeBuilder
from backend.academic_engine.knowledge.academic_models import (
    AcademicKnowledgeStats,
    AcademicSnapshot,
    AcademicSnapshotMetadata,
    AcademicTechnologyRecord,
)
from backend.academic_engine.knowledge.academic_repository import AcademicKnowledgeRepository
from backend.academic_engine.models.academic_document import ParsedAcademicDocument
from backend.industry_engine.processing.normalization.models import NormalizationResult

logger = logging.getLogger("academic_engine.knowledge.academic_service")


class AcademicKnowledgeService:
    """
    Business service facade for the Academic Knowledge Layer.
    """

    def __init__(
        self,
        repository_path: Optional[str] = None,
        snapshot_path: Optional[str] = None,
    ) -> None:
        cfg = AcademicEngineConfig()
        self.repository = AcademicKnowledgeRepository(storage_path=repository_path or cfg.repository_path)
        self.snapshot_path = Path(snapshot_path or cfg.snapshot_path)
        self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        self.builder = AcademicKnowledgeBuilder()
        self._lock = threading.RLock()

    def ingest_document_extractions(
        self,
        normalization_result: NormalizationResult,
        document: ParsedAcademicDocument,
        auto_snapshot: bool = True,
    ) -> Tuple[int, Optional[AcademicSnapshot]]:
        """
        Build and persist academic technology records from a document extraction.

        Returns:
            Tuple of (records_added_count, optional_snapshot).
        """
        records = self.builder.build_records(normalization_result, document)
        with self._lock:
            for r in records:
                self.repository.add(r)

            snapshot = None
            if auto_snapshot:
                snapshot = self.create_snapshot()

            logger.info("[Academic] Knowledge Updated: %d records ingested into repository.", len(records))
            return len(records), snapshot

    def get_all(self) -> List[AcademicTechnologyRecord]:
        return self.repository.get_all()

    def get_technology(self, technology_id: str) -> AcademicTechnologyRecord:
        return self.repository.get(technology_id)

    def search(self, query: str) -> List[AcademicTechnologyRecord]:
        return self.repository.search(query)

    def count(self) -> int:
        return self.repository.count()

    def get_statistics(self) -> AcademicKnowledgeStats:
        all_records = self.repository.get_all()
        categories: Dict[str, int] = {}
        courses: set = set()
        universities: set = set()

        for r in all_records:
            categories[r.category] = categories.get(r.category, 0) + 1
            courses.add(r.course_code)
            universities.add(r.university)

        top_techs = [
            {"technology_id": r.technology_id, "canonical_name": r.canonical_name, "frequency": r.frequency}
            for r in sorted(all_records, key=lambda x: x.frequency, reverse=True)[:10]
        ]

        return AcademicKnowledgeStats(
            total_technologies=len(all_records),
            total_courses=len(courses),
            total_universities=len(universities),
            categories=categories,
            top_technologies=top_techs,
        )

    def create_snapshot(self, description: str = "Academic Knowledge Snapshot") -> AcademicSnapshot:
        with self._lock:
            records = self.repository.get_all()
            snap_id = f"academic-snap-{len(records)}-{int(Path(self.snapshot_path).stat().st_mtime if self.snapshot_path.exists() else 0)}"
            meta = AcademicSnapshotMetadata(
                snapshot_id=snap_id,
                record_count=len(records),
                description=description,
            )
            snapshot = AcademicSnapshot(metadata=meta, records=records)

            try:
                self.snapshot_path.write_text(json.dumps(snapshot.model_dump(), indent=2), encoding="utf-8")
                logger.info("[Academic] Created snapshot '%s' (%d records).", snap_id, len(records))
            except Exception as exc:
                logger.error("[Academic] Failed to write snapshot: %s", exc)

            return snapshot
