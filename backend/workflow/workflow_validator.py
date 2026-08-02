"""
Workflow Validator.
Validates workflow graph structure and step dependencies.
"""

from typing import Dict, List
from backend.workflow.workflow_models import WorkflowStep


class WorkflowValidationError(Exception):
    """Raised when workflow validation fails."""
    pass


class WorkflowValidator:
    """Validates workflow definitions against cyclic dependencies and missing steps."""

    @staticmethod
    def validate_steps(steps: Dict[str, WorkflowStep]) -> bool:
        """Validate step definitions and dependency graph."""
        if not steps:
            raise WorkflowValidationError("Workflow must contain at least one step.")

        step_ids = set(steps.keys())

        # Check for missing dependency targets
        for step_id, step in steps.items():
            for dep in step.depends_on:
                if dep not in step_ids:
                    raise WorkflowValidationError(
                        f"Step '{step_id}' depends on non-existent step '{dep}'."
                    )

        # Check for cycle (topological sort test)
        visited = set()
        rec_stack = set()

        def dfs(curr: str):
            visited.add(curr)
            rec_stack.add(curr)
            for dep in steps[curr].depends_on:
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    return True
            rec_stack.remove(curr)
            return False

        for step_id in steps:
            if step_id not in visited:
                if dfs(step_id):
                    raise WorkflowValidationError("Cyclic dependency detected in workflow steps.")

        return True
