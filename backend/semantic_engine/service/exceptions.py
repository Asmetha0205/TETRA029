"""
Custom Exceptions for Semantic Service Layer.
"""


class SemanticServiceError(Exception):
    """Base exception for Semantic Service Layer errors."""
    pass


class ComparisonExecutionError(SemanticServiceError):
    """Raised when curriculum comparison execution fails."""
    pass


class EmptyCurriculumError(SemanticServiceError):
    """Raised when comparison is requested for an empty curriculum dataset."""
    pass
