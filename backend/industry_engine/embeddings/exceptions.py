"""
Custom Exceptions for the CurricuAlign AI Embedding Engine.

Provides a structured exception hierarchy for error handling across
embedding generation, validation, caching, repository operations, and model loading.
"""


class EmbeddingError(Exception):
    """Base exception for all Embedding Engine errors."""
    pass


class EmbeddingGenerationError(EmbeddingError):
    """Raised when embedding generation fails."""
    pass


class EmbeddingValidationError(EmbeddingError):
    """Raised when an embedding record fails validation."""
    pass


class EmbeddingRepositoryError(EmbeddingError):
    """Raised when persistence or storage operations fail."""
    pass


class EmbeddingCacheError(EmbeddingError):
    """Raised when cache operations fail."""
    pass


class ModelLoadError(EmbeddingError):
    """Raised when the sentence transformer model cannot be loaded."""
    pass
