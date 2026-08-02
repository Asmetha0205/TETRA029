"""
Custom Exceptions for Academic Service Layer.
"""


class AcademicServiceError(Exception):
    """Base exception for Academic Service Layer errors."""
    pass


class DocumentNotFoundError(AcademicServiceError):
    """Raised when document is not found in catalog."""
    pass


class CourseNotFoundError(AcademicServiceError):
    """Raised when course is not found."""
    pass


class PipelineExecutionError(AcademicServiceError):
    """Raised when processing pipeline fails."""
    pass
