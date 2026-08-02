"""
Custom Exceptions for Evidence Engine.
"""


class EvidenceError(Exception):
    """Base exception for Evidence Engine errors."""
    pass


class ExplanationGenerationError(EvidenceError):
    """Raised when explanation text generation fails."""
    pass
