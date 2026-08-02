"""
Event Models for CurricuAlign AI.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """System Event Types."""
    PDF_UPLOADED = "PDF_UPLOADED"
    ACADEMIC_ANALYSIS_STARTED = "ACADEMIC_ANALYSIS_STARTED"
    ACADEMIC_ANALYSIS_COMPLETED = "ACADEMIC_ANALYSIS_COMPLETED"
    SEMANTIC_ANALYSIS_STARTED = "SEMANTIC_ANALYSIS_STARTED"
    SEMANTIC_ANALYSIS_COMPLETED = "SEMANTIC_ANALYSIS_COMPLETED"
    RECOMMENDATION_STARTED = "RECOMMENDATION_STARTED"
    RECOMMENDATION_COMPLETED = "RECOMMENDATION_COMPLETED"
    REPORT_GENERATED = "REPORT_GENERATED"
    ANALYSIS_COMPLETED = "ANALYSIS_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    STEP_FAILED = "STEP_FAILED"


class Event(BaseModel):
    """Event representation passed across system event bus."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    source: str = "system"
    analysis_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
