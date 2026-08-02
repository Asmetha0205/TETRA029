"""
Workflow Manager.
Tracks active and historical analysis executions, providing status queries and cancellation.
"""

import threading
from typing import Any, Dict, List, Optional
from backend.orchestrator.execution_context import ExecutionContext
from backend.workflow.workflow import Workflow
from backend.workflow.workflow_models import WorkflowExecutionState, WorkflowStatus
from backend.utils.logger import get_logger

logger = get_logger("orchestrator.workflow_manager")


class WorkflowManager:
    """Manages lifecycle and status tracking for all analysis jobs."""

    def __init__(self):
        self._contexts: Dict[str, ExecutionContext] = {}
        self._workflows: Dict[str, Workflow] = {}
        self._lock = threading.RLock()

    def register_job(self, context: ExecutionContext, workflow: Workflow) -> None:
        """Register a new active analysis job."""
        with self._lock:
            self._contexts[context.analysis_id] = context
            self._workflows[context.analysis_id] = workflow

    def get_context(self, analysis_id: str) -> Optional[ExecutionContext]:
        """Retrieve context by analysis_id."""
        with self._lock:
            return self._contexts.get(analysis_id)

    def get_workflow_state(self, analysis_id: str) -> Optional[WorkflowExecutionState]:
        """Retrieve workflow state by analysis_id."""
        with self._lock:
            wf = self._workflows.get(analysis_id)
            return wf.state if wf else None

    def cancel_job(self, analysis_id: str) -> bool:
        """Cancel a running analysis job."""
        with self._lock:
            wf = self._workflows.get(analysis_id)
            if wf:
                wf.request_cancellation()
                return True
            return False

    def list_active_jobs(self) -> List[Dict[str, Any]]:
        """List summary of active/recent jobs."""
        with self._lock:
            jobs = []
            for aid, wf in self._workflows.items():
                ctx = self._contexts.get(aid)
                jobs.append({
                    "analysis_id": aid,
                    "filename": ctx.filename if ctx else "unknown",
                    "status": wf.state.status.value,
                    "progress_percentage": wf.state.progress_percentage,
                    "start_time": wf.state.start_time,
                    "execution_time": wf.state.execution_time,
                })
            return jobs
