"""
Custom Exceptions for Semantic Matching Engine.
"""


class MatchingError(Exception):
    """Base exception for Semantic Matching errors."""
    pass


class CandidateSelectionError(MatchingError):
    """Raised when candidate selection fails."""
    pass


class QueryBuildError(MatchingError):
    """Raised when constructing candidate query fails."""
    pass
