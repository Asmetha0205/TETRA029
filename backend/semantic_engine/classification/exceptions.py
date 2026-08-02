"""
Custom Exceptions for Coverage Classification Module.
"""


class ClassificationError(Exception):
    """Base exception for Coverage Classification errors."""
    pass


class RuleEvaluationError(ClassificationError):
    """Raised when classification rule evaluation fails."""
    pass
