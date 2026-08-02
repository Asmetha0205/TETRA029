"""
Exceptions for the CurricuAlign AI Technology Frequency Analysis Engine.

Provides a typed exception hierarchy so callers can distinguish between
input validation failures, processing failures, and data integrity issues.
"""

class FrequencyAnalysisError(Exception):
    """Base exception for all frequency analysis failures."""


class EmptyDatasetError(FrequencyAnalysisError):
    """Raised when frequency analysis is attempted on an empty job dataset."""


class DuplicateJobError(FrequencyAnalysisError):
    """Raised when a duplicate job ID is detected in an incremental batch."""


class InvalidTechnologyError(FrequencyAnalysisError):
    """Raised when a technology record is malformed or missing required fields."""


class MissingCategoryError(FrequencyAnalysisError):
    """Raised when a technology has no associated category."""


class MalformedRecordError(FrequencyAnalysisError):
    """Raised when a job record cannot be interpreted."""


class NegativeCountError(FrequencyAnalysisError):
    """Raised when calculated counts or metrics produce negative values."""


class InvalidPercentageError(FrequencyAnalysisError):
    """Raised when a computed percentage falls outside the valid [0.0, 100.0] range."""


class InvalidInputError(FrequencyAnalysisError):
    """Raised when the input payload to the frequency engine is structurally invalid."""