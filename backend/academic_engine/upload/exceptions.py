"""
Custom Exceptions for PDF Upload Module.
"""


class UploadError(Exception):
    """Base exception for all PDF Upload errors."""
    pass


class InvalidPDFError(UploadError):
    """Raised when an uploaded file is not a valid PDF."""
    pass


class FileTooLargeError(UploadError):
    """Raised when an uploaded PDF exceeds the maximum file size limit."""
    pass


class DuplicateDocumentError(UploadError):
    """Raised when an uploaded PDF has the same checksum as an existing document."""
    pass
