"""
Custom Exceptions for Similarity Engine.
"""


class SimilarityError(Exception):
    """Base exception for Similarity Engine errors."""
    pass


class InvalidThresholdError(SimilarityError):
    """Raised when similarity thresholds are invalid or out of range."""
    pass
