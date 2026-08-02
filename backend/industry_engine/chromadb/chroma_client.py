"""
ChromaDB Client Wrapper for CurricuAlign AI.

Provides a thread-safe connection to ChromaDB vector database.
Includes an in-memory vector storage fallback when the native 'chromadb' library
is not installed or when running in lightweight mode.
"""

import math
import logging
import threading
from typing import Any, Dict, List, Optional, Union

from backend.industry_engine.chromadb.exceptions import ChromaClientError

logger = logging.getLogger("industry_engine.chromadb.chroma_client")

_CHROMADB_AVAILABLE = False
try:
    import chromadb
    _CHROMADB_AVAILABLE = True
except ImportError:
    _CHROMADB_AVAILABLE = False


class InMemoryChromaCollection:
    """
    In-memory fallback vector collection implementing the ChromaDB Collection interface.
    """

    def __init__(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.name = name
        self.metadata = metadata or {}
        self._ids: List[str] = []
        self._embeddings: List[List[float]] = []
        self._metadatas: List[Dict[str, Any]] = []
        self._documents: List[str] = []
        self._lock = threading.RLock()

    def count(self) -> int:
        with self._lock:
            return len(self._ids)

    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        documents: Optional[List[str]] = None,
    ) -> None:
        with self._lock:
            metadatas = metadatas or [{} for _ in ids]
            documents = documents or ["" for _ in ids]

            for i, doc_id in enumerate(ids):
                if doc_id in self._ids:
                    # Replace existing
                    idx = self._ids.index(doc_id)
                    self._embeddings[idx] = embeddings[i]
                    self._metadatas[idx] = metadatas[i]
                    self._documents[idx] = documents[i]
                else:
                    self._ids.append(doc_id)
                    self._embeddings.append(embeddings[i])
                    self._metadatas.append(metadatas[i])
                    self._documents.append(documents[i])

    def upsert(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        documents: Optional[List[str]] = None,
    ) -> None:
        self.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    def get(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        with self._lock:
            result_ids = []
            result_embeddings = []
            result_metadatas = []
            result_documents = []

            for idx, doc_id in enumerate(self._ids):
                if ids and doc_id not in ids:
                    continue
                meta = self._metadatas[idx]
                if where:
                    match = True
                    for k, v in where.items():
                        if meta.get(k) != v:
                            match = False
                            break
                    if not match:
                        continue

                result_ids.append(doc_id)
                result_embeddings.append(self._embeddings[idx])
                result_metadatas.append(meta)
                result_documents.append(self._documents[idx])

                if limit and len(result_ids) >= limit:
                    break

            return {
                "ids": result_ids,
                "embeddings": result_embeddings,
                "metadatas": result_metadatas,
                "documents": result_documents,
            }

    def delete(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._lock:
            to_delete = set()
            if ids:
                to_delete.update(ids)
            if where:
                for idx, meta in enumerate(self._metadatas):
                    match = True
                    for k, v in where.items():
                        if meta.get(k) != v:
                            match = False
                            break
                    if match:
                        to_delete.add(self._ids[idx])

            new_ids, new_emb, new_meta, new_doc = [], [], [], []
            for idx, doc_id in enumerate(self._ids):
                if doc_id not in to_delete:
                    new_ids.append(self._ids[idx])
                    new_emb.append(self._embeddings[idx])
                    new_meta.append(self._metadatas[idx])
                    new_doc.append(self._documents[idx])

            self._ids = new_ids
            self._embeddings = new_emb
            self._metadatas = new_meta
            self._documents = new_doc

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        with self._lock:
            res_ids = []
            res_distances = []
            res_metadatas = []
            res_documents = []

            for q_emb in query_embeddings:
                scored = []
                for idx, doc_id in enumerate(self._ids):
                    meta = self._metadatas[idx]
                    if where:
                        match = True
                        for k, v in where.items():
                            if meta.get(k) != v:
                                match = False
                                break
                        if not match:
                            continue

                    dist = self._cosine_distance(q_emb, self._embeddings[idx])
                    scored.append((dist, doc_id, meta, self._documents[idx]))

                scored.sort(key=lambda item: item[0])
                top = scored[:n_results]

                res_ids.append([item[1] for item in top])
                res_distances.append([item[0] for item in top])
                res_metadatas.append([item[2] for item in top])
                res_documents.append([item[3] for item in top])

            return {
                "ids": res_ids,
                "distances": res_distances,
                "metadatas": res_metadatas,
                "documents": res_documents,
            }

    @staticmethod
    def _cosine_distance(vec_a: List[float], vec_b: List[float]) -> float:
        if len(vec_a) != len(vec_b) or not vec_a:
            return 1.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a ** 2 for a in vec_a))
        norm_b = math.sqrt(sum(b ** 2 for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 1.0
        sim = max(-1.0, min(1.0, dot / (norm_a * norm_b)))
        return round(1.0 - sim, 6)


class InMemoryChromaClient:
    """In-memory fallback client mimicking chromadb.Client."""

    def __init__(self) -> None:
        self._collections: Dict[str, InMemoryChromaCollection] = {}
        self._lock = threading.RLock()

    def get_or_create_collection(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> InMemoryChromaCollection:
        with self._lock:
            if name not in self._collections:
                self._collections[name] = InMemoryChromaCollection(name=name, metadata=metadata)
            return self._collections[name]

    def get_collection(self, name: str) -> InMemoryChromaCollection:
        with self._lock:
            if name not in self._collections:
                raise ValueError(f"Collection '{name}' does not exist.")
            return self._collections[name]

    def delete_collection(self, name: str) -> None:
        with self._lock:
            self._collections.pop(name, None)

    def list_collections(self) -> List[Any]:
        with self._lock:
            return list(self._collections.values())


class ChromaClientWrapper:
    """
    Thread-safe client wrapper for ChromaDB.

    Automatically uses native chromadb client if available and path provided,
    otherwise uses InMemoryChromaClient fallback.
    """

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        force_in_memory: bool = False,
    ) -> None:
        self.persist_directory = persist_directory
        self.force_in_memory = force_in_memory
        self._client: Any = None
        self._lock = threading.RLock()

        self._initialize_client()

    def _initialize_client(self) -> None:
        with self._lock:
            if not self.force_in_memory and _CHROMADB_AVAILABLE:
                try:
                    if self.persist_directory:
                        self._client = chromadb.PersistentClient(path=self.persist_directory)
                        logger.info("[ChromaDB] Initialized PersistentClient at '%s'.", self.persist_directory)
                    else:
                        self._client = chromadb.Client()
                        logger.info("[ChromaDB] Initialized ephemeral in-memory ChromaDB client.")
                    return
                except Exception as exc:
                    logger.warning("[ChromaDB] Failed native client creation: %s. Using fallback.", exc)

            self._client = InMemoryChromaClient()
            logger.info("[ChromaDB] Initialized thread-safe fallback vector store client.")

    def get_or_create_collection(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Any:
        try:
            return self._client.get_or_create_collection(name=name, metadata=metadata)
        except Exception as exc:
            raise ChromaClientError(f"Failed to get_or_create_collection '{name}': {exc}") from exc

    def get_collection(self, name: str) -> Any:
        try:
            return self._client.get_collection(name=name)
        except Exception as exc:
            raise ChromaClientError(f"Collection '{name}' lookup failed: {exc}") from exc

    def delete_collection(self, name: str) -> None:
        try:
            self._client.delete_collection(name=name)
            logger.info("[ChromaDB] Deleted collection '%s'.", name)
        except Exception as exc:
            logger.warning("[ChromaDB] Delete collection '%s' failed: %s", name, exc)

    def is_fallback(self) -> bool:
        """Check if running in fallback mode."""
        return isinstance(self._client, InMemoryChromaClient)
