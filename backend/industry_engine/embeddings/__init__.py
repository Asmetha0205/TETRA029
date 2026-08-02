"""
Embedding Engine for CurricuAlign AI Industry Intelligence Engine.

Provides vector generation, caching, semantic versioning, repository persistence,
validation, and similarity search for technology records from the Industry Knowledge Layer.
Independent of ChromaDB (Phase 3.8.2).
"""

from backend.industry_engine.embeddings.exceptions import (
    EmbeddingCacheError,
    EmbeddingError,
    EmbeddingGenerationError,
    EmbeddingRepositoryError,
    EmbeddingValidationError,
    ModelLoadError,
)
from backend.industry_engine.embeddings.embedding_cache import EmbeddingCache
from backend.industry_engine.embeddings.embedding_generator import EmbeddingGenerator
from backend.industry_engine.embeddings.embedding_manager import EmbeddingManager
from backend.industry_engine.embeddings.embedding_models import (
    BatchGenerationResult,
    CacheStats,
    EmbeddingRecord,
    EmbeddingStats,
    EmbeddingStatus,
)
from backend.industry_engine.embeddings.embedding_repository import EmbeddingRepository
from backend.industry_engine.embeddings.embedding_service import EmbeddingService
from backend.industry_engine.embeddings.embedding_validator import EmbeddingValidator

__all__ = [
    # Exceptions
    "EmbeddingError",
    "EmbeddingGenerationError",
    "EmbeddingValidationError",
    "EmbeddingRepositoryError",
    "EmbeddingCacheError",
    "ModelLoadError",
    # Enums
    "EmbeddingStatus",
    # Models
    "EmbeddingRecord",
    "CacheStats",
    "BatchGenerationResult",
    "EmbeddingStats",
    # Components
    "EmbeddingValidator",
    "EmbeddingCache",
    "EmbeddingRepository",
    "EmbeddingGenerator",
    "EmbeddingManager",
    # Facade Service
    "EmbeddingService",
]
