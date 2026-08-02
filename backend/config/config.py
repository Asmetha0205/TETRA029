"""
System Configuration for CurricuAlign AI Phase 7 Integration.
"""

from typing import Optional
from pydantic import BaseModel, Field


class SystemConfig(BaseModel):
    """Global system configuration settings."""
    app_name: str = Field(default="CurricuAlign AI System Integration")
    environment: str = Field(default="production")
    debug: bool = Field(default=False)

    # Caching
    cache_ttl_seconds: int = Field(default=3600)
    cache_max_entries: int = Field(default=1000)

    # File limits
    max_upload_size_mb: int = Field(default=25)
    allowed_extensions: list = Field(default_factory=lambda: [".pdf"])

    # Fault Tolerance
    enable_retry: bool = Field(default=True)
    max_retries: int = Field(default=3)
    retry_delay_seconds: float = Field(default=1.0)
    allow_partial_results: bool = Field(default=True)

    # Persistence & Storage
    storage_dir: str = Field(default="./data/storage")
    cache_dir: str = Field(default="./data/cache")


# Singleton instance
system_config = SystemConfig()
