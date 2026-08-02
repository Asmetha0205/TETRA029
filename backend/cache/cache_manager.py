"""
Cache Manager.
In-memory LRU key-value cache store with TTL and stats.
"""

import threading
from typing import Any, Dict, Optional
from backend.cache.cache_models import CacheEntry, CacheStats
from backend.utils.logger import get_logger

logger = get_logger("cache.manager")


class CacheManager:
    """Thread-safe in-memory cache manager."""

    def __init__(self, default_ttl: int = 3600, max_entries: int = 1000):
        self.default_ttl = default_ttl
        self.max_entries = max_entries
        self._store: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._invalidations = 0

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache if present and not expired."""
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                self._misses += 1
                return None

            if entry.is_expired():
                logger.info("[Cache] Entry for key '%s' expired.", key)
                del self._store[key]
                self._misses += 1
                return None

            entry.hits += 1
            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Store value in cache."""
        with self._lock:
            if len(self._store) >= self.max_entries and key not in self._store:
                # Evict oldest entry
                oldest_key = min(
                    self._store.keys(),
                    key=lambda k: self._store[k].created_at
                )
                del self._store[oldest_key]
                self._evictions += 1

            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
            self._store[key] = CacheEntry(key=key, value=value, ttl_seconds=ttl)

    def invalidate(self, key: str) -> bool:
        """Explicitly invalidate a key."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                self._invalidations += 1
                return True
            return False

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            count = len(self._store)
            self._store.clear()
            self._invalidations += count

    def get_stats(self) -> CacheStats:
        """Return cache statistics."""
        with self._lock:
            total_reqs = self._hits + self._misses
            ratio = (self._hits / total_reqs) if total_reqs > 0 else 0.0
            return CacheStats(
                total_entries=len(self._store),
                total_hits=self._hits,
                total_misses=self._misses,
                hit_ratio=round(ratio, 4),
                evictions=self._evictions,
                invalidations=self._invalidations,
            )
