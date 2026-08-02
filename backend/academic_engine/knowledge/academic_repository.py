"""
Academic Knowledge Repository for CurricuAlign AI Academic Engine.

Thread-safe in-memory store with JSON persistence for AcademicTechnologyRecords.
"""

import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional

from backend.academic_engine.config.config import AcademicEngineConfig
from backend.academic_engine.knowledge.academic_models import AcademicTechnologyRecord
from backend.academic_engine.knowledge.exceptions import AcademicRecordNotFoundError

logger = logging.getLogger("academic_engine.knowledge.academic_repository")


class AcademicKnowledgeRepository:
    """
    Thread-safe repository pattern storing AcademicTechnologyRecord models.
    """

    def __init__(self, storage_path: Optional[str] = None) -> None:
        cfg = AcademicEngineConfig()
        self.storage_path = Path(storage_path or cfg.repository_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self._records: Dict[str, AcademicTechnologyRecord] = {}
        self._lock = threading.RLock()

        self.load()

    def add(self, record: AcademicTechnologyRecord) -> None:
        with self._lock:
            if record.technology_id in self._records:
                existing = self._records[record.technology_id]
                existing.frequency += record.frequency
                existing.touch()
            else:
                self._records[record.technology_id] = record
            self.save()

    def get(self, technology_id: str) -> AcademicTechnologyRecord:
        with self._lock:
            if technology_id not in self._records:
                raise AcademicRecordNotFoundError(f"Academic technology '{technology_id}' not found.")
            return self._records[technology_id].model_copy(deep=True)

    def get_optional(self, technology_id: str) -> Optional[AcademicTechnologyRecord]:
        with self._lock:
            rec = self._records.get(technology_id)
            return rec.model_copy(deep=True) if rec else None

    def get_all(self) -> List[AcademicTechnologyRecord]:
        with self._lock:
            return [r.model_copy(deep=True) for r in self._records.values()]

    def search(self, query: str) -> List[AcademicTechnologyRecord]:
        with self._lock:
            q = query.lower().strip()
            results = []
            for r in self._records.values():
                if (q in r.technology_id.lower() or
                    q in r.canonical_name.lower() or
                    q in r.category.lower() or
                    any(q in alias.lower() for alias in r.aliases)):
                    results.append(r.model_copy(deep=True))
            results.sort(key=lambda item: item.frequency, reverse=True)
            return results

    def count(self) -> int:
        with self._lock:
            return len(self._records)

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
            self.save()

    def save(self) -> None:
        with self._lock:
            try:
                data = {tid: rec.model_dump() for tid, rec in self._records.items()}
                self.storage_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except Exception as exc:
                logger.error("[Academic] Failed to save academic repository: %s", exc)

    def load(self) -> None:
        with self._lock:
            if self.storage_path.exists():
                try:
                    raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
                    for tid, d in raw.items():
                        self._records[tid] = AcademicTechnologyRecord.model_validate(d)
                    logger.info("[Academic] Loaded %d records from repository file.", len(self._records))
                except Exception as exc:
                    logger.warning("[Academic] Failed to load academic repository: %s", exc)
