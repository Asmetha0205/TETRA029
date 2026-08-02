"""
Custom Exceptions for Technology Extraction Module.
"""


class ExtractionError(Exception):
    """Base exception for Technology Extraction errors."""
    pass


class GeminiAPIError(ExtractionError):
    """Raised when Gemini API fails or returns an error."""
    pass


class MalformedExtractionJSONError(ExtractionError):
    """Raised when LLM extraction output cannot be parsed as valid JSON."""
    pass
