"""
Custom Exceptions for the CurricuAlign AI ChromaDB Synchronization Layer.

Provides a structured exception hierarchy for error handling across
ChromaDB client connection, collection management, metadata formatting,
vector synchronization, and similarity query operations.
"""


class ChromaSyncError(Exception):
    """Base exception for all ChromaDB Synchronization Layer errors."""
    pass


class ChromaClientError(ChromaSyncError):
    """Raised when ChromaDB client initialization or connection fails."""
    pass


class CollectionNotFoundError(ChromaSyncError):
    """Raised when a requested ChromaDB collection is not found."""
    pass


class MetadataValidationError(ChromaSyncError):
    """Raised when metadata formatting or validation fails."""
    pass


class ChromaQueryError(ChromaSyncError):
    """Raised when a vector query or similarity search operation fails."""
    pass
