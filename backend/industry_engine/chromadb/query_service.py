"""
ChromaDB Query Service for CurricuAlign AI.

Provides high-performance vector search, semantic query processing,
category filtering, and technology metadata lookups over the 'industry_technologies' collection.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from backend.industry_engine.chromadb.exceptions import ChromaQueryError
from backend.industry_engine.chromadb.collection_manager import CollectionManager

logger = logging.getLogger("industry_engine.chromadb.query_service")


class ChromaQueryService:
    """
    Query interface for executing similarity search and metadata queries against ChromaDB.
    """

    def __init__(self, collection_manager: CollectionManager) -> None:
        """
        Initialize ChromaQueryService.

        Args:
            collection_manager: CollectionManager instance.
        """
        self.collection_manager = collection_manager

    def search_by_vector(
        self,
        query_vector: List[float],
        limit: int = 10,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for most similar vectors in ChromaDB using a query vector.

        Args:
            query_vector: Numerical query vector (384 float dimensions).
            limit: Maximum number of search results to return.
            where: Optional metadata filter dictionary.

        Returns:
            List of result dictionaries containing technology_id, distance, score, metadata, document.
        """
        collection = self.collection_manager.get_or_create_collection()
        try:
            raw_res = collection.query(
                query_embeddings=[query_vector],
                n_results=limit,
                where=where,
            )

            results: List[Dict[str, Any]] = []
            if not raw_res or not raw_res.get("ids"):
                return results

            ids = raw_res["ids"][0]
            distances = raw_res.get("distances", [[]])[0]
            metadatas = raw_res.get("metadatas", [[]])[0]
            documents = raw_res.get("documents", [[]])[0]

            for i in range(len(ids)):
                dist = float(distances[i]) if i < len(distances) else 0.0
                meta = metadatas[i] if i < len(metadatas) else {}
                doc = documents[i] if i < len(documents) else ""

                # Cosine similarity score derived from distance
                similarity_score = round(max(0.0, 1.0 - dist), 4)

                results.append({
                    "doc_id": ids[i],
                    "technology_id": meta.get("technology_id", ""),
                    "canonical_name": meta.get("canonical_name", ""),
                    "category": meta.get("category", ""),
                    "distance": round(dist, 4),
                    "similarity_score": similarity_score,
                    "metadata": meta,
                    "document": doc,
                })

            logger.info("[ChromaDB] Vector query returned %d results.", len(results))
            return results
        except Exception as exc:
            raise ChromaQueryError(f"Vector search query failed: {exc}") from exc

    def get_by_technology_id(self, technology_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve vector document and metadata by technology_id.

        Args:
            technology_id: Unique technology identifier.

        Returns:
            Result dictionary or None if not found.
        """
        collection = self.collection_manager.get_or_create_collection()
        doc_id = f"vec-{technology_id}"
        try:
            res = collection.get(ids=[doc_id])
            if res and res.get("ids") and len(res["ids"]) > 0:
                meta = res["metadatas"][0] if res.get("metadatas") else {}
                doc = res["documents"][0] if res.get("documents") else ""
                emb = res["embeddings"][0] if res.get("embeddings") else []
                return {
                    "doc_id": doc_id,
                    "technology_id": technology_id,
                    "metadata": meta,
                    "document": doc,
                    "embedding": emb,
                }
            return None
        except Exception as exc:
            logger.warning("[ChromaDB] Lookup by technology_id '%s' failed: %s", technology_id, exc)
            return None

    def search_by_category(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search technologies within a specific category.

        Args:
            category: Canonical category string.
            limit: Maximum results.

        Returns:
            List of matching technology result dicts.
        """
        collection = self.collection_manager.get_or_create_collection()
        try:
            res = collection.get(where={"category": category}, limit=limit)
            results = []
            if res and res.get("ids"):
                for i in range(len(res["ids"])):
                    meta = res["metadatas"][i] if res.get("metadatas") else {}
                    results.append({
                        "technology_id": meta.get("technology_id", ""),
                        "canonical_name": meta.get("canonical_name", ""),
                        "category": meta.get("category", ""),
                        "industry_score": meta.get("industry_score", 0.0),
                        "metadata": meta,
                    })
            results.sort(key=lambda item: item.get("industry_score", 0.0), reverse=True)
            return results
        except Exception as exc:
            raise ChromaQueryError(f"Category search failed for '{category}': {exc}") from exc
