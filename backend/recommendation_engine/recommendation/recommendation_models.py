"""
Recommendation Data Models for CurricuAlign AI.
Defines standard output schema matching exact Phase 6 specification.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    """Individual evidence-backed recommendation item."""
    technology: str = Field(..., description="Target technology name, e.g., Redis")
    priority: str = Field(..., description="Urgency priority: Critical, High, Medium, Low")
    industry_score: float = Field(..., ge=0.0, le=100.0, description="Industry demand score 0-100")
    trend: str = Field(default="Rising", description="Market trend: Rapidly Growing, Rising, Stable")
    reason: str = Field(..., description="Explainable justification for recommendation")
    recommended_course: str = Field(..., description="Suggested academic course placement")
    recommended_module: str = Field(..., description="Suggested module placement")
    learning_outcomes: List[str] = Field(default_factory=list, description="Measurable learning outcomes")
    lab: str = Field(..., description="Hands-on laboratory exercise description")
    mini_project: str = Field(..., description="Applied mini-project topic")
    learning_path: List[str] = Field(default_factory=list, description="Ordered dependency technology sequence")
    references: List[str] = Field(default_factory=list, description="Supporting evidence references")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0.0-1.0")


class RecommendationResultSet(BaseModel):
    """Collection container for all generated recommendations."""
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    total_recommendations: int = 0
    generated_at: str = Field(default="")
    summary_metrics: Dict[str, Any] = Field(default_factory=dict)
