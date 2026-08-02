"""
Data Models for the CurricuAlign AI Embedding Engine.

Defines Pydantic v2 data models for embedding records, lifecycle status,
cache statistics, batch processing results, and repository statistics.
"""

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class EmbeddingStatus(str, Enum):
    """Lifecycle status of an embedding record."""
    ACTIVE = "active"
    OUTDATED = "outdated"
    ARCHIVED = "archived"
    FAILED = "failed"


class EmbeddingRecord(BaseModel):
    """
    Authoritative embedding record for a technology.

    Stores the generated dense vector, metadata, model information,
    and SHA-256 content hash for change detection.
    """
    embedding_id: str = Field(
        ...,
        description="Unique identifier for this embedding record (e.g. 'emb-pytorch').",
        min_length=1,
    )
    technology_id: str = Field(
        ...,
        description="Target technology identifier from the Knowledge Layer.",
        min_length=1,
    )
    model_name: str = Field(
        default="all-MiniLM-L6-v2",
        description="Name of the sentence transformer model used.",
    )
    model_version: str = Field(
        default="1.0.0",
        description="Version string of the embedding model.",
    )
    embedding_dimension: int = Field(
        default=384,
        ge=1,
        description="Dimension size of the embedding vector.",
    )
    embedding_vector: List[float] = Field(
        ...,
        description="Dense numerical vector embedding.",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="ISO timestamp when the embedding was generated.",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="ISO timestamp when the embedding was last updated.",
    )
    embedding_hash: str = Field(
        ...,
        description="SHA-256 hash of the input text used to generate the embedding.",
    )
    status: EmbeddingStatus = Field(
        default=EmbeddingStatus.ACTIVE,
        description="Lifecycle status of the embedding.",
    )
    text_content: Optional[str] = Field(
        default=None,
        description="Structured textual prompt used for embedding generation.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary additional metadata (norm, generation time, source, etc.).",
    )

    @field_validator("embedding_vector")
    @classmethod
    def validate_vector_non_empty(cls, value: List[float]) -> List[float]:
        """Ensure vector is non-empty and contains valid floats."""
        if not value:
            raise ValueError("embedding_vector cannot be empty.")
        return value

    def touch(self) -> None:
        """Update last_updated timestamp to current UTC time."""
        self.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()


class CacheStats(BaseModel):
    """Statistics for the Embedding Cache."""
    hits: int = Field(default=0, ge=0)
    misses: int = Field(default=0, ge=0)
    hit_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    total_cached: int = Field(default=0, ge=0)
    max_size: int = Field(default=1000, ge=1)


class BatchGenerationResult(BaseModel):
    """Result summary of a batch embedding generation run."""
    total_processed: int = Field(default=0, ge=0)
    generated_count: int = Field(default=0, ge=0)
    cached_count: int = Field(default=0, ge=0)
    skipped_count: int = Field(default=0, ge=0)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    generation_time_seconds: float = Field(default=0.0, ge=0.0)


class EmbeddingStats(BaseModel):
    """Aggregate statistics for the Embedding Engine."""
    total_embeddings: int = Field(default=0, ge=0)
    active_count: int = Field(default=0, ge=0)
    outdated_count: int = Field(default=0, ge=0)
    archived_count: int = Field(default=0, ge=0)
    model_name: str = Field(default="all-MiniLM-L6-v2")
    embedding_dimension: int = Field(default=384)
    cache_stats: CacheStats = Field(default_factory=CacheStats)
