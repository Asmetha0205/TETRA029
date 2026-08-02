"""
Data Models for Academic Service Layer.
"""

import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AcademicPipelineSummary(BaseModel):
    """
    Summary output returned following an end-to-end curriculum processing run.
    """
    documents_processed: int = Field(default=1)
    courses_detected: int = Field(default=0)
    technologies_extracted: int = Field(default=0)
    new_technologies: int = Field(default=0)
    normalized: int = Field(default=0)
    unknown: int = Field(default=0)
    snapshot_created: bool = Field(default=True)
    execution_time: str = Field(default="0.0s")


class ComponentHealth(BaseModel):
    """Component health status."""
    status: str = Field(..., description="'healthy', 'degraded', or 'unhealthy'")
    message: str = Field(default="Operational")
    details: Dict[str, Any] = Field(default_factory=dict)


class AcademicHealthStatus(BaseModel):
    """Overall health status of the Academic Intelligence Engine."""
    status: str = Field(...)
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    components: Dict[str, ComponentHealth] = Field(default_factory=dict)
