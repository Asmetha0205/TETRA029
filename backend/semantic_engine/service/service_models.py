"""
Service Models for Semantic Service Layer.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SemanticEngineHealthStatus(BaseModel):
    """Health status of the Semantic Intelligence Engine."""
    status: str = Field(..., description="'healthy', 'degraded', or 'unhealthy'")
    timestamp: str = Field(...)
    components: Dict[str, Any] = Field(default_factory=dict)
