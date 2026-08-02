"""
API Schemas for CurricuAlign AI System Integration.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """Standard unified API envelope."""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class UnifiedAnalysisResultSchema(BaseModel):
    """Unified AnalysisResult output schema."""
    analysis_id: str
    document_id: str
    alignment_score: float
    covered_skills: List[Dict[str, Any]] = Field(default_factory=list)
    partial_skills: List[Dict[str, Any]] = Field(default_factory=list)
    gap_skills: List[Dict[str, Any]] = Field(default_factory=list)
    priority_summary: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    learning_paths: Dict[str, Any] = Field(default_factory=dict)
    industry_statistics: Dict[str, Any] = Field(default_factory=dict)
    academic_statistics: Dict[str, Any] = Field(default_factory=dict)
    processing_metrics: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float
    generated_at: str
    warnings_or_errors: List[str] = Field(default_factory=list)


class DashboardSummarySchema(BaseModel):
    """Dashboard summary analytics."""
    total_analyses: int
    avg_alignment_score: float
    total_skills_mapped: int
    top_industry_gaps: List[str]
    system_health_status: str
    cache_hit_ratio: float


class StatusSummarySchema(BaseModel):
    """System operational status and active jobs."""
    status: str
    active_jobs_count: int
    active_jobs: List[Dict[str, Any]]
    uptime_seconds: float
