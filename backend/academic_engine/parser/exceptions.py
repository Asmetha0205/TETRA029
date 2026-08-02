"""
Custom Exceptions for PDF Parsing Engine.
"""


class PDFParsingError(Exception):
    """Base exception for all PDF Parsing errors."""
    pass


class CorruptPDFError(PDFParsingError):
    """Raised when PDF file is corrupt or unreadable."""
    pass


class EncryptedPDFError(PDFParsingError):
    """Raised when PDF file is password protected or encrypted."""
    pass


class TextExtractionError(PDFParsingError):
    """Raised when text extraction yields no readable content."""
    pass
