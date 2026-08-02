"""
Technology Extraction Cache for CurricuAlign AI LLM Technology Intelligence Engine.
SHA-256 content-based caching to prevent redundant LLM calls for identical job descriptions.
"""

import hashlib
import json
import logging
import os
import threading
from typing import Optional, Dict, Any

from backend.industry_engine.processing.llm.models import TechnologyExtraction

logger = logging.getLogger("industry_engine.processing.llm.cache")


class TechnologyExtractionCache:
    """
    Thread-safe in-memory cache with optional file-backed persistence.
    Keys are SHA-256 hashes computed from (job_id, clean_description).
    """

    def __init__(self, persist_path: Optional[str] = None):
        """
        Initialize cache.

        Args:
            persist_path: Optional filesystem path for JSON-based cache persistence.
                          If None, cache is in-memory only.
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._persist_path = persist_path
        self._hits: int = 0
        self._misses: int = 0

        if self._persist_path:
            self._load_from_disk()

    @staticmethod
    def _compute_key(job_id: str, clean_description: str) -> str:
        """
        Compute a deterministic SHA-256 cache key from job_id and clean_description.
        """
        raw = f"{job_id}||{clean_description}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def has(self, job_id: str, clean_description: str) -> bool:
        """
        Check if a cache entry exists for the given job.
        """
        key = self._compute_key(job_id, clean_description)
        with self._lock:
            return key in self._cache

    def get(self, job_id: str, clean_description: str) -> Optional[TechnologyExtraction]:
        """
        Retrieve a cached TechnologyExtraction result.
        Returns None on cache miss.
        """
        key = self._compute_key(job_id, clean_description)
        with self._lock:
            if key in self._cache:
                self._hits += 1
                logger.info(f"[Cache] HIT for job_id='{job_id}' (key={key[:12]}...)")
                return TechnologyExtraction(**self._cache[key])
            else:
                self._misses += 1
                logger.info(f"[Cache] MISS for job_id='{job_id}' (key={key[:12]}...)")
                return None

    def set(self, job_id: str, clean_description: str, extraction: TechnologyExtraction) -> None:
        """
        Store a TechnologyExtraction result into the cache.
        """
        key = self._compute_key(job_id, clean_description)
        with self._lock:
            self._cache[key] = extraction.model_dump()
            logger.info(f"[Cache] STORED extraction for job_id='{job_id}' (key={key[:12]}...)")

        if self._persist_path:
            self._save_to_disk()

    def clear(self) -> None:
        """
        Clear all cached entries and reset stats.
        """
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info("[Cache] Cache cleared.")

        if self._persist_path and os.path.exists(self._persist_path):
            try:
                os.remove(self._persist_path)
            except OSError as e:
                logger.warning(f"[Cache] Failed to remove persistence file: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Return cache performance statistics.
        """
        with self._lock:
            total = self._hits + self._misses
            return {
                "total_entries": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(self._hits / total, 4) if total > 0 else 0.0
            }

    def _load_from_disk(self) -> None:
        """
        Load cached entries from the persistence file.
        """
        if not self._persist_path or not os.path.exists(self._persist_path):
            return
        try:
            with open(self._persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self._cache = data
                logger.info(f"[Cache] Loaded {len(self._cache)} entries from disk.")
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"[Cache] Failed to load persistence file: {e}")
            self._cache = {}

    def _save_to_disk(self) -> None:
        """
        Persist cached entries to the filesystem.
        """
        if not self._persist_path:
            return
        try:
            persist_dir = os.path.dirname(self._persist_path)
            if persist_dir:
                os.makedirs(persist_dir, exist_ok=True)
            with self._lock:
                with open(self._persist_path, "w", encoding="utf-8") as f:
                    json.dump(self._cache, f, indent=2, ensure_ascii=False)
            logger.debug(f"[Cache] Persisted {len(self._cache)} entries to disk.")
        except OSError as e:
            logger.warning(f"[Cache] Failed to persist cache to disk: {e}")
