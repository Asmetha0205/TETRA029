"""
API Schemas for the Industry REST API.

Defines Pydantic v2 request and response schemas.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TechnologyResponse(BaseModel):
    """API response model for a single technology knowledge record."""
    technology_id: str
    canonical_name: str
    category: str
    aliases: List[str] = Field(default_factory=list)
    description: str = Field(default="")
    frequency: int = Field(default=0)
    demand_score: float = Field(default=0.0)
    industry_score: float = Field(default=0.0)
    trend: str = Field(default="Stable")
    growth: float = Field(default=0.0)
    classification: str = Field(default="Supporting Technology")
    related_technologies: List[str] = Field(default_factory=list)
    role_coverage: Dict[str, float] = Field(default_factory=dict)
    status: str = Field(default="active")
    version: str = Field(default="1.0.0")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TechnologyListResponse(BaseModel):
    """API response model for a list of technologies."""
    total: int
    technologies: List[TechnologyResponse]


class SimilarSearchResponseItem(BaseModel):
    """API response model for a similarity search result."""
    technology_id: str
    canonical_name: str
    category: str
    similarity_score: float
    distance: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimilarSearchResponse(BaseModel):
    """API response model for vector similarity search."""
    query: str
    total: int
    results: List[SimilarSearchResponseItem]


class RefreshRequestPayload(BaseModel):
    """API request payload for triggering a refresh run."""
    source_name: str = Field(default="api_request")
    dry_run: bool = Field(default=False)
    auto_snapshot: bool = Field(default=True)


class RefreshResponse(BaseModel):
    """API response model for refresh pipeline execution."""
    run_id: str
    success: bool
    raw_jobs_count: int
    clean_jobs_count: int
    normalized_count: int
    knowledge_created: int
    knowledge_updated: int
    embeddings_generated: int
    chroma_synced: int
    snapshot_id: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_seconds: float


class RollbackRequestPayload(BaseModel):
    """API request payload for snapshot rollback."""
    snapshot_id: str = Field(..., min_length=1)


class RollbackResponse(BaseModel):
    """API response model for snapshot rollback."""
    snapshot_id: str
    records_loaded: int
    success: bool
    message: str
