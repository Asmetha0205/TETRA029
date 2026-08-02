"""
Workflow Models for CurricuAlign AI System Integration.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """Workflow execution states."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    DEGRADED = "DEGRADED"


class StepStatus(str, Enum):
    """Workflow step execution states."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class WorkflowStep(BaseModel):
    """Definition of a single step in a workflow pipeline."""
    step_id: str
    name: str
    description: str = ""
    depends_on: List[str] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 2
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    execution_time: float = 0.0
    error: Optional[str] = None
    output: Optional[Dict[str, Any]] = None


class WorkflowExecutionState(BaseModel):
    """Tracks state and progress of an executing workflow."""
    workflow_id: str
    name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: Optional[str] = None
    progress_percentage: float = 0.0
    completed_steps: List[str] = Field(default_factory=list)
    failed_steps: List[str] = Field(default_factory=list)
    steps: Dict[str, WorkflowStep] = Field(default_factory=dict)
    start_time: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    end_time: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    cancellation_requested: bool = False
