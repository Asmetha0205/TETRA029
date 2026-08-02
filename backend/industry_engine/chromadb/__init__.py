"""
ChromaDB Synchronization Package for CurricuAlign AI Industry Intelligence Engine.

Provides vector storage synchronization, metadata management, collection lifecycle,
and similarity query processing for the 'industry_technologies' vector index.
"""

from backend.industry_engine.chromadb.exceptions import (
    ChromaClientError,
    ChromaQueryError,
    ChromaSyncError,
    CollectionNotFoundError,
    MetadataValidationError,
)
from backend.industry_engine.chromadb.chroma_client import ChromaClientWrapper, InMemoryChromaClient
from backend.industry_engine.chromadb.collection_manager import CollectionManager
from backend.industry_engine.chromadb.metadata_manager import ChromaMetadataManager
from backend.industry_engine.chromadb.query_service import ChromaQueryService
from backend.industry_engine.chromadb.sync_service import ChromaSyncResult, ChromaSyncService

__all__ = [
    # Exceptions
    "ChromaSyncError",
    "ChromaClientError",
    "CollectionNotFoundError",
    "MetadataValidationError",
    "ChromaQueryError",
    # Components & Clients
    "ChromaClientWrapper",
    "InMemoryChromaClient",
    "CollectionManager",
    "ChromaMetadataManager",
    # Services
    "ChromaSyncService",
    "ChromaSyncResult",
    "ChromaQueryService",
]
