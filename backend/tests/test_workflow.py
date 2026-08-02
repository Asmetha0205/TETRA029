"""
Unit tests for Workflow Manager and Workflow Engine.
"""

import unittest
from backend.workflow.workflow import Workflow
from backend.workflow.workflow_models import StepStatus, WorkflowStatus
from backend.workflow.workflow_validator import WorkflowValidator, WorkflowValidationError


class TestWorkflowEngine(unittest.TestCase):

    def test_successful_sequential_workflow(self):
        wf = Workflow("wf-1", "Test Workflow")
        execution_order = []

        wf.add_step("step1", "Step 1", lambda s: execution_order.append(1))
        wf.add_step("step2", "Step 2", lambda s: execution_order.append(2), depends_on=["step1"])

        state = wf.execute()
        self.assertEqual(state.status, WorkflowStatus.COMPLETED)
        self.assertEqual(execution_order, [1, 2])
        self.assertEqual(state.progress_percentage, 100.0)

    def test_workflow_retry_mechanism(self):
        wf = Workflow("wf-retry", "Retry Workflow")
        attempts = 0

        def flaky_handler(s):
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise ValueError("Temporary glitch")
            return "ok"

        wf.add_step("step1", "Flaky Step", flaky_handler, max_retries=2)
        state = wf.execute()

        self.assertEqual(state.status, WorkflowStatus.COMPLETED)
        self.assertEqual(attempts, 2)

    def test_cycle_detection_in_validator(self):
        wf = Workflow("wf-cycle", "Cycle Workflow")
        wf.add_step("a", "Step A", lambda s: None, depends_on=["b"])
        wf.add_step("b", "Step B", lambda s: None, depends_on=["a"])

        with self.assertRaises(WorkflowValidationError):
            wf.validate()


if __name__ == "__main__":
    unittest.main()
