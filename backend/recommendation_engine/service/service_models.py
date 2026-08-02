"""
Service Models for Recommendation Intelligence Layer.
Defines Request & Response objects for RecommendationService methods.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.recommendation_engine.learning_path.path_generator import LearningPathPlan
from backend.recommendation_engine.recommendation.recommendation_models import RecommendationResultSet
from backend.recommendation_engine.report.report_builder import ExecutiveReport
from backend.recommendation_engine.retrieval.ranking import RankedEvidence


class GenerateRecommendationsRequest(BaseModel):
    """Request payload to generate curriculum recommendations."""
    gap_analysis_data: Dict[str, Any] = Field(..., description="GapAnalysisResult dictionary")
    target_gaps: Optional[List[str]] = Field(default=None, description="Optional list of gap technology names")
    knowledge_context: Optional[Dict[str, Any]] = Field(default=None, description="Optional academic & industry context")


class ExportReportRequest(BaseModel):
    """Request payload to export recommendation report."""
    recommendation_id: Optional[str] = Field(default=None)
    format: str = Field(default="json", description="json, markdown, or pdf")
    file_path: Optional[str] = Field(default=None)


class ServiceExecutionResponse(BaseModel):
    """Standardized service execution wrapper response."""
    success: bool = True
    message: str = "Execution completed successfully"
    recommendations: Optional[RecommendationResultSet] = None
    learning_path: Optional[LearningPathPlan] = None
    evidence: Optional[List[RankedEvidence]] = None
    report: Optional[ExecutiveReport] = None
    exported_content: Optional[str] = None
