"""
Execution Context.
State object passed through the analysis execution pipeline.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class ExecutionContext(BaseModel):
    """Encapsulates transient and cumulative state for an analysis run."""
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = "curriculum.pdf"
    file_bytes: Optional[bytes] = None
    document_id: Optional[str] = None
    university_name: str = "Unknown University"
    curriculum_year: str = "2025-2026"
    department: str = "Computer Science"

    # Pipeline output stages
    academic_output: Dict[str, Any] = Field(default_factory=dict)
    industry_output: Dict[str, Any] = Field(default_factory=dict)
    semantic_report: Optional[Dict[str, Any]] = None
    recommendation_output: Optional[Dict[str, Any]] = None

    # Error recovery & warning accumulators
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

    # Timings
    timings: Dict[str, float] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
