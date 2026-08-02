"""
Embedding Cache for the CurricuAlign AI Embedding Engine.

Provides thread-safe in-memory caching for generated embedding records.
Avoids redundant vector generation by checking SHA-256 content hashes.
"""

import logging
import threading
from collections import OrderedDict
from typing import Dict, Optional

from backend.industry_engine.embeddings.exceptions import EmbeddingCacheError
from backend.industry_engine.embeddings.embedding_models import CacheStats, EmbeddingRecord

logger = logging.getLogger("industry_engine.embeddings.embedding_cache")


class EmbeddingCache:
    """
    In-memory LRU cache for technology embedding records.

    Thread-safe via reentrant lock. Enables rapid lookup by technology ID
    or content hash to prevent redundant vector generation.
    """

    def __init__(self, max_size: int = 1000) -> None:
        """
        Initialize the embedding cache.

        Args:
            max_size: Maximum number of records to store in memory.
        """
        self._max_size = max_size
        self._cache_by_tech_id: OrderedDict[str, EmbeddingRecord] = OrderedDict()
        self._cache_by_hash: Dict[str, EmbeddingRecord] = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

        logger.info("[Embedding] Cache initialized with max_size=%d.", max_size)

    def get(self, technology_id: str) -> Optional[EmbeddingRecord]:
        """
        Retrieve an embedding record by technology ID.

        Args:
            technology_id: Target technology identifier.

        Returns:
            The cached EmbeddingRecord, or None on cache miss.
        """
        with self._lock:
            record = self._cache_by_tech_id.get(technology_id)
            if record is not None:
                self._cache_by_tech_id.move_to_end(technology_id)
                self._hits += 1
                logger.debug("[Embedding] Cache Hit for technology_id '%s'.", technology_id)
                return record.model_copy(deep=True)
            self._misses += 1
            logger.debug("[Embedding] Cache Miss for technology_id '%s'.", technology_id)
            return None

    def get_by_hash(self, content_hash: str) -> Optional[EmbeddingRecord]:
        """
        Retrieve an embedding record by input text content hash.

        Args:
            content_hash: SHA-256 content hash.

        Returns:
            The cached EmbeddingRecord, or None on cache miss.
        """
        with self._lock:
            record = self._cache_by_hash.get(content_hash)
            if record is not None:
                self._hits += 1
                logger.debug("[Embedding] Cache Hit for hash '%s...'.", content_hash[:8])
                return record.model_copy(deep=True)
            self._misses += 1
            logger.debug("[Embedding] Cache Miss for hash '%s...'.", content_hash[:8])
            return None

    def put(self, record: EmbeddingRecord) -> None:
        """
        Store an embedding record in the cache.

        Args:
            record: The EmbeddingRecord to cache.
        """
        if not record or not record.technology_id:
            raise EmbeddingCacheError("Cannot cache empty record or record without technology_id.")

        with self._lock:
            tech_id = record.technology_id
            content_hash = record.embedding_hash

            # Evict if full and inserting new key
            if tech_id not in self._cache_by_tech_id and len(self._cache_by_tech_id) >= self._max_size:
                oldest_id, oldest_rec = self._cache_by_tech_id.popitem(last=False)
                self._cache_by_hash.pop(oldest_rec.embedding_hash, None)
                logger.debug("[Embedding] Evicted oldest cache entry '%s'.", oldest_id)

            record_copy = record.model_copy(deep=True)
            self._cache_by_tech_id[tech_id] = record_copy
            self._cache_by_tech_id.move_to_end(tech_id)
            if content_hash:
                self._cache_by_hash[content_hash] = record_copy

            logger.debug("[Embedding] Cached record for '%s'.", tech_id)

    def evict(self, technology_id: str) -> bool:
        """
        Evict an embedding record from the cache.

        Args:
            technology_id: Target technology identifier.

        Returns:
            True if evicted, False if not present.
        """
        with self._lock:
            record = self._cache_by_tech_id.pop(technology_id, None)
            if record:
                self._cache_by_hash.pop(record.embedding_hash, None)
                logger.debug("[Embedding] Evicted '%s' from cache.", technology_id)
                return True
            return False

    def clear(self) -> int:
        """
        Clear all entries from the cache.

        Returns:
            Number of entries cleared.
        """
        with self._lock:
            count = len(self._cache_by_tech_id)
            self._cache_by_tech_id.clear()
            self._cache_by_hash.clear()
            self._hits = 0
            self._misses = 0
            logger.info("[Embedding] Cleared %d entries from cache.", count)
            return count

    def get_stats(self) -> CacheStats:
        """
        Get current cache statistics.

        Returns:
            CacheStats model containing hits, misses, hit_ratio, total_cached.
        """
        with self._lock:
            total_ops = self._hits + self._misses
            ratio = round(self._hits / total_ops, 4) if total_ops > 0 else 0.0
            return CacheStats(
                hits=self._hits,
                misses=self._misses,
                hit_ratio=ratio,
                total_cached=len(self._cache_by_tech_id),
                max_size=self._max_size,
            )
