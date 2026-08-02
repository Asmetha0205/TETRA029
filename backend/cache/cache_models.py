"""
Cache Layer Models.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class CacheEntry(BaseModel):
    """Represents a cached item with expiry and metadata."""
    key: str
    value: Any
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    ttl_seconds: int = 3600
    hits: int = 0

    def is_expired(self) -> bool:
        """Check if entry is expired based on TTL."""
        created_dt = datetime.fromisoformat(self.created_at)
        return (datetime.utcnow() - created_dt).total_seconds() > self.ttl_seconds


class CacheStats(BaseModel):
    """Cache performance and usage statistics."""
    total_entries: int = 0
    total_hits: int = 0
    total_misses: int = 0
    hit_ratio: float = 0.0
    evictions: int = 0
    invalidations: int = 0
