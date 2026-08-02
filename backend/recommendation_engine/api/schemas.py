"""
API Pydantic Schemas for Recommendation Intelligence Layer.
Defines REST API HTTP request and response structures.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GenerateRecommendationsApiRequest(BaseModel):
    """Payload for POST /recommendations/generate."""
    gap_analysis_data: Dict[str, Any] = Field(..., description="Semantic engine GapAnalysisResult dictionary")
    target_gaps: Optional[List[str]] = Field(default=None, description="Optional targeted gap skill names")
    knowledge_context: Optional[Dict[str, Any]] = Field(default=None, description="Optional academic & industry metadata")


class ApiResponse(BaseModel):
    """Generic API wrapper response."""
    status: str = "success"
    message: str = ""
    data: Optional[Any] = None
