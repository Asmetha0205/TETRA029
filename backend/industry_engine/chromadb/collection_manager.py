"""
Collection Manager for the CurricuAlign AI ChromaDB Synchronization Layer.

Manages the lifecycle of the 'industry_technologies' vector collection.
Provides collection initialization, statistics, validation, and reset capabilities.
"""

import logging
from typing import Any, Dict, Optional

from backend.industry_engine.chromadb.exceptions import CollectionNotFoundError
from backend.industry_engine.chromadb.chroma_client import ChromaClientWrapper

logger = logging.getLogger("industry_engine.chromadb.collection_manager")


class CollectionManager:
    """
    Manages the 'industry_technologies' vector collection in ChromaDB.
    """

    COLLECTION_NAME = "industry_technologies"

    def __init__(self, client_wrapper: ChromaClientWrapper) -> None:
        """
        Initialize collection manager with client wrapper.

        Args:
            client_wrapper: ChromaClientWrapper instance.
        """
        self.client_wrapper = client_wrapper
        self._collection: Optional[Any] = None

    def get_or_create_collection(self) -> Any:
        """
        Get or create the 'industry_technologies' collection.

        Returns:
            ChromaDB collection instance.
        """
        if self._collection is None:
            metadata = {"hnsw:space": "cosine", "description": "CurricuAlign AI Industry Technologies Vector Index"}
            self._collection = self.client_wrapper.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata=metadata,
            )
            logger.info("[ChromaDB] Collection '%s' initialized.", self.COLLECTION_NAME)
        return self._collection

    def get_collection(self) -> Any:
        """
        Retrieve existing collection instance.

        Returns:
            ChromaDB collection instance.

        Raises:
            CollectionNotFoundError: If collection has not been created.
        """
        if self._collection is None:
            try:
                self._collection = self.client_wrapper.get_collection(self.COLLECTION_NAME)
            except Exception as exc:
                raise CollectionNotFoundError(f"Collection '{self.COLLECTION_NAME}' not found.") from exc
        return self._collection

    def count(self) -> int:
        """Return total vector documents in collection."""
        collection = self.get_or_create_collection()
        return collection.count()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            Dictionary with name, count, fallback status, and metadata.
        """
        collection = self.get_or_create_collection()
        return {
            "collection_name": self.COLLECTION_NAME,
            "document_count": collection.count(),
            "is_fallback": self.client_wrapper.is_fallback(),
            "metadata": getattr(collection, "metadata", {}),
        }

    def reset(self) -> None:
        """Delete and re-create the collection."""
        self.client_wrapper.delete_collection(self.COLLECTION_NAME)
        self._collection = None
        self.get_or_create_collection()
        logger.info("[ChromaDB] Collection '%s' reset successfully.", self.COLLECTION_NAME)
