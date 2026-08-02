"""
Workflow Engine & State Management.
Supports sequential, conditional execution, retries, cancellation, and progress tracking.
"""

import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from backend.workflow.workflow_models import (
    StepStatus,
    WorkflowExecutionState,
    WorkflowStatus,
    WorkflowStep,
)
from backend.workflow.workflow_validator import WorkflowValidator
from backend.utils.logger import get_logger

logger = get_logger("workflow.engine")


class Workflow:
    """
    Workflow instance tracking steps, state, retry policies, and progress.
    """

    def __init__(self, workflow_id: str, name: str):
        self.workflow_id = workflow_id
        self.name = name
        self.steps: Dict[str, WorkflowStep] = {}
        self.step_handlers: Dict[str, Callable[[WorkflowExecutionState], Any]] = {}
        self.state = WorkflowExecutionState(
            workflow_id=workflow_id,
            name=name,
            status=WorkflowStatus.PENDING,
        )

    def add_step(
        self,
        step_id: str,
        name: str,
        handler: Callable[[WorkflowExecutionState], Any],
        depends_on: Optional[List[str]] = None,
        max_retries: int = 2,
    ) -> "Workflow":
        """Add a step to the workflow."""
        step = WorkflowStep(
            step_id=step_id,
            name=name,
            depends_on=depends_on or [],
            max_retries=max_retries,
        )
        self.steps[step_id] = step
        self.step_handlers[step_id] = handler
        self.state.steps[step_id] = step
        return self

    def validate(self) -> bool:
        """Validate workflow configuration."""
        return WorkflowValidator.validate_steps(self.steps)

    def request_cancellation(self) -> None:
        """Signal cancellation request."""
        logger.warning("[Workflow %s] Cancellation requested.", self.workflow_id)
        self.state.cancellation_requested = True
        self.state.status = WorkflowStatus.CANCELLED

    def execute(self) -> WorkflowExecutionState:
        """
        Execute workflow steps according to dependencies.
        Supports retries, conditional skipping, and cancellation.
        """
        self.validate()
        self.state.status = WorkflowStatus.RUNNING
        self.state.start_time = datetime.utcnow().isoformat()
        start_ts = time.time()

        logger.info("[Workflow %s] Execution started.", self.workflow_id)

        total_steps = len(self.steps)

        for step_id, step in self.steps.items():
            if self.state.cancellation_requested:
                logger.warning("[Workflow %s] Halting execution due to cancellation.", self.workflow_id)
                step.status = StepStatus.SKIPPED
                continue

            # Check dependencies
            deps_ok = all(
                self.steps[dep].status == StepStatus.COMPLETED
                for dep in step.depends_on
            )
            if not deps_ok:
                logger.warning(
                    "[Workflow %s] Step '%s' skipped due to unfulfilled dependencies.",
                    self.workflow_id,
                    step_id,
                )
                step.status = StepStatus.SKIPPED
                continue

            # Execute step with retries
            self.state.current_step = step_id
            step.status = StepStatus.RUNNING
            step.start_time = datetime.utcnow().isoformat()
            step_start_ts = time.time()

            success = False
            last_error = None

            for attempt in range(step.max_retries + 1):
                step.retry_count = attempt
                try:
                    logger.info(
                        "[Workflow %s] Executing step '%s' (Attempt %d/%d)...",
                        self.workflow_id,
                        step_id,
                        attempt + 1,
                        step.max_retries + 1,
                    )
                    handler = self.step_handlers[step_id]
                    result = handler(self.state)
                    step.output = result if isinstance(result, dict) else {"result": str(result)}
                    step.status = StepStatus.COMPLETED
                    self.state.completed_steps.append(step_id)
                    success = True
                    break
                except Exception as exc:
                    last_error = str(exc)
                    logger.error(
                        "[Workflow %s] Step '%s' failed on attempt %d: %s",
                        self.workflow_id,
                        step_id,
                        attempt + 1,
                        exc,
                    )
                    time.sleep(0.5)

            step.execution_time = round(time.time() - step_start_ts, 3)
            step.end_time = datetime.utcnow().isoformat()

            if not success:
                step.status = StepStatus.FAILED
                step.error = last_error
                self.state.failed_steps.append(step_id)
                logger.error("[Workflow %s] Step '%s' permanently failed.", self.workflow_id, step_id)

            # Update progress
            completed_count = len(self.state.completed_steps)
            self.state.progress_percentage = round((completed_count / total_steps) * 100.0, 1)

        self.state.execution_time = round(time.time() - start_ts, 3)
        self.state.end_time = datetime.utcnow().isoformat()

        if self.state.cancellation_requested:
            self.state.status = WorkflowStatus.CANCELLED
        elif len(self.state.failed_steps) == 0:
            self.state.status = WorkflowStatus.COMPLETED
        elif len(self.state.completed_steps) > 0:
            self.state.status = WorkflowStatus.DEGRADED
        else:
            self.state.status = WorkflowStatus.FAILED

        logger.info(
            "[Workflow %s] Workflow finished with status %s in %.2fs",
            self.workflow_id,
            self.state.status,
            self.state.execution_time,
        )
        return self.state
