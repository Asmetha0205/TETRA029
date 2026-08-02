"""
High-Level Cache Service.
Provides domain-specific caching for lookups, similarity, recommendations, reports, and search.
"""

from typing import Any, Dict, List, Optional
from backend.cache.cache_manager import CacheManager
from backend.cache.cache_models import CacheStats
from backend.utils.logger import get_logger

logger = get_logger("cache.service")


class CacheService:
    """High-level service wrapping CacheManager for domain entities."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.manager = cache_manager or CacheManager()

    def get_knowledge(self, key: str) -> Optional[Any]:
        """Get cached knowledge lookup result."""
        return self.manager.get(f"knowledge:{key}")

    def set_knowledge(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Cache knowledge lookup result."""
        self.manager.set(f"knowledge:{key}", value, ttl)

    def get_similarity(self, query: str) -> Optional[Any]:
        """Get cached similarity search result."""
        return self.manager.get(f"similarity:{query.lower().strip()}")

    def set_similarity(self, query: str, value: Any, ttl: Optional[int] = None) -> None:
        """Cache similarity search result."""
        self.manager.set(f"similarity:{query.lower().strip()}", value, ttl)

    def get_recommendation(self, gap_hash: str) -> Optional[Any]:
        """Get cached recommendation output."""
        return self.manager.get(f"rec:{gap_hash}")

    def set_recommendation(self, gap_hash: str, value: Any, ttl: Optional[int] = None) -> None:
        """Cache recommendation output."""
        self.manager.set(f"rec:{gap_hash}", value, ttl)

    def get_report(self, analysis_id: str) -> Optional[Any]:
        """Get cached alignment report."""
        return self.manager.get(f"report:{analysis_id}")

    def set_report(self, analysis_id: str, value: Any, ttl: Optional[int] = None) -> None:
        """Cache alignment report."""
        self.manager.set(f"report:{analysis_id}", value, ttl)

    def invalidate_analysis(self, analysis_id: str) -> None:
        """Invalidate all cached items for an analysis_id."""
        self.manager.invalidate(f"report:{analysis_id}")
        self.manager.invalidate(f"analysis:{analysis_id}")

    def clear_all(self) -> None:
        """Clear all cached entries."""
        self.manager.clear()

    def get_statistics(self) -> CacheStats:
        """Get cache performance stats."""
        return self.manager.get_stats()
