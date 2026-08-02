"""
Health Monitoring Models for CurricuAlign AI.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SystemHealthStatusEnum(str, Enum):
    """Overall system health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealthDetail(BaseModel):
    """Health check result for an individual component or dependency."""
    status: SystemHealthStatusEnum
    message: str = "Operating normally"
    details: Dict[str, Any] = Field(default_factory=dict)
    response_time_ms: float = 0.0


class OverallHealthReport(BaseModel):
    """Unified system-wide health report."""
    status: SystemHealthStatusEnum
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    academic_engine: ComponentHealthDetail
    industry_engine: ComponentHealthDetail
    semantic_engine: ComponentHealthDetail
    recommendation_engine: ComponentHealthDetail
    neo4j: ComponentHealthDetail
    chromadb: ComponentHealthDetail
    gemini: ComponentHealthDetail
    repository_access: ComponentHealthDetail
    summary: Dict[str, Any] = Field(default_factory=dict)
