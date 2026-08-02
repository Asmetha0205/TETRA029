"""
Data Models for the Industry Service Layer.

Defines response & request models for health status, statistics, search results,
snapshot operations, and refresh requests.
"""

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ComponentHealth(BaseModel):
    """Health status of an individual engine component."""
    status: str = Field(..., description="'healthy', 'degraded', or 'unhealthy'")
    message: str = Field(default="Operational")
    details: Dict[str, Any] = Field(default_factory=dict)


class IndustryHealthStatus(BaseModel):
    """Overall health evaluation of the Industry Intelligence Engine."""
    status: str = Field(..., description="Overall engine health ('healthy', 'degraded', 'unhealthy')")
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    components: Dict[str, ComponentHealth] = Field(default_factory=dict)


class SimilarSearchResultItem(BaseModel):
    """Single item result from vector similarity search."""
    technology_id: str
    canonical_name: str
    category: str
    similarity_score: float = Field(..., ge=-1.0, le=1.0)
    distance: float = Field(default=0.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RefreshRequestOptions(BaseModel):
    """Options for triggering a refresh pipeline run."""
    source_name: str = Field(default="api_request")
    dry_run: bool = Field(default=False)
    auto_snapshot: bool = Field(default=True)
