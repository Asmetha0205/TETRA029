"""
Analysis Orchestrator Exceptions.
"""

class OrchestratorError(Exception):
    """Base exception for Orchestrator errors."""
    pass


class PipelineExecutionError(OrchestratorError):
    """Raised when pipeline execution fails unrecoverably."""
    pass


class SubsystemFailureError(OrchestratorError):
    """Raised when an engine subsystem fails."""
    pass


class CancellationError(OrchestratorError):
    """Raised when workflow execution is cancelled."""
    pass
