"""
Custom Exceptions for the Industry Service Layer.
"""


class IndustryServiceError(Exception):
    """Base exception for all Industry Service Layer errors."""
    pass


class RefreshError(IndustryServiceError):
    """Raised when an industry refresh pipeline execution fails."""
    pass


class HealthCheckError(IndustryServiceError):
    """Raised when a component health check fails."""
    pass


class RollbackError(IndustryServiceError):
    """Raised when a snapshot rollback operation fails."""
    pass
