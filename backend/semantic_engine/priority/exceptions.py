"""
Custom Exceptions for Priority Engine.
"""


class PriorityError(Exception):
    """Base exception for Priority Engine errors."""
    pass


class PriorityCalculationError(PriorityError):
    """Raised when priority score calculation fails."""
    pass
