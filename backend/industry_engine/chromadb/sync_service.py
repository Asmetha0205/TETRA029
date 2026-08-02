"""
ChromaDB Synchronization Service for CurricuAlign AI.

Synchronizes TechnologyKnowledgeRecord (Knowledge Layer) and EmbeddingRecord (Embedding Engine)
data into the ChromaDB 'industry_technologies' vector collection.

Supports single item upsert, batch sync, incremental sync (hash matching), and deletion.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.industry_engine.chromadb.exceptions import ChromaSyncError
from backend.industry_engine.chromadb.collection_manager import CollectionManager
from backend.industry_engine.chromadb.metadata_manager import ChromaMetadataManager
from backend.industry_engine.knowledge.knowledge_models import TechnologyKnowledgeRecord
from backend.industry_engine.embeddings.embedding_models import EmbeddingRecord

logger = logging.getLogger("industry_engine.chromadb.sync_service")


class ChromaSyncResult:
    """Result envelope for ChromaDB synchronization operations."""

    def __init__(
        self,
        total_processed: int = 0,
        inserted_count: int = 0,
        updated_count: int = 0,
        skipped_count: int = 0,
        deleted_count: int = 0,
        errors: Optional[List[Dict[str, Any]]] = None,
        elapsed_seconds: float = 0.0,
    ) -> None:
        self.total_processed = total_processed
        self.inserted_count = inserted_count
        self.updated_count = updated_count
        self.skipped_count = skipped_count
        self.deleted_count = deleted_count
        self.errors = errors or []
        self.elapsed_seconds = elapsed_seconds

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_processed": self.total_processed,
            "inserted_count": self.inserted_count,
            "updated_count": self.updated_count,
            "skipped_count": self.skipped_count,
            "deleted_count": self.deleted_count,
            "errors": self.errors,
            "elapsed_seconds": self.elapsed_seconds,
        }


class ChromaSyncService:
    """
    Service responsible for vector data synchronization between Knowledge/Embedding Layers and ChromaDB.
    """

    def __init__(self, collection_manager: CollectionManager) -> None:
        """
        Initialize ChromaSyncService.

        Args:
            collection_manager: CollectionManager instance.
        """
        self.collection_manager = collection_manager

    def sync_single(
        self,
        tech_record: TechnologyKnowledgeRecord,
        emb_record: EmbeddingRecord,
    ) -> None:
        """
        Synchronize a single technology and its embedding vector into ChromaDB.

        Args:
            tech_record: Authoritative TechnologyKnowledgeRecord.
            emb_record: Corresponding EmbeddingRecord.
        """
        collection = self.collection_manager.get_or_create_collection()
        doc_id = f"vec-{tech_record.technology_id}"
        metadata = ChromaMetadataManager.prepare_metadata(tech_record, emb_record)
        document_text = emb_record.text_content or f"{tech_record.canonical_name}: {tech_record.category}"

        collection.upsert(
            ids=[doc_id],
            embeddings=[emb_record.embedding_vector],
            metadatas=[metadata],
            documents=[document_text],
        )
        logger.info("[ChromaDB] Synced vector for technology '%s'.", tech_record.technology_id)

    def sync_batch(
        self,
        pairs: List[Tuple[TechnologyKnowledgeRecord, EmbeddingRecord]],
        incremental: bool = True,
    ) -> ChromaSyncResult:
        """
        Batch synchronize multiple (technology, embedding) record pairs.

        Args:
            pairs: List of (TechnologyKnowledgeRecord, EmbeddingRecord) tuples.
            incremental: If True, skips items whose content hash already matches in ChromaDB.

        Returns:
            ChromaSyncResult containing detailed synchronization counts.
        """
        start_time = time.time()
        if not pairs:
            return ChromaSyncResult()

        collection = self.collection_manager.get_or_create_collection()
        total_processed = len(pairs)

        existing_hash_map: Dict[str, str] = {}
        if incremental and collection.count() > 0:
            try:
                # Fetch existing metadatas to check embedding_hash
                existing_data = collection.get(limit=10000)
                for idx, doc_id in enumerate(existing_data.get("ids", [])):
                    meta = existing_data.get("metadatas", [])[idx] or {}
                    tech_id = meta.get("technology_id")
                    h = meta.get("embedding_hash")
                    if tech_id and h:
                        existing_hash_map[tech_id] = h
            except Exception as exc:
                logger.warning("[ChromaDB] Unable to fetch existing collection metadata: %s", exc)

        ids_to_upsert = []
        vectors_to_upsert = []
        metadatas_to_upsert = []
        documents_to_upsert = []

        inserted = 0
        updated = 0
        skipped = 0
        errors = []

        for tech_rec, emb_rec in pairs:
            tech_id = tech_rec.technology_id
            target_hash = emb_rec.embedding_hash

            if incremental and tech_id in existing_hash_map:
                if existing_hash_map[tech_id] == target_hash:
                    skipped += 1
                    continue
                else:
                    updated += 1
            else:
                inserted += 1

            try:
                doc_id = f"vec-{tech_id}"
                meta = ChromaMetadataManager.prepare_metadata(tech_rec, emb_rec)
                doc_text = emb_rec.text_content or f"{tech_rec.canonical_name}: {tech_rec.category}"

                ids_to_upsert.append(doc_id)
                vectors_to_upsert.append(emb_rec.embedding_vector)
                metadatas_to_upsert.append(meta)
                documents_to_upsert.append(doc_text)
            except Exception as exc:
                errors.append({"technology_id": tech_id, "error": str(exc)})

        if ids_to_upsert:
            collection.upsert(
                ids=ids_to_upsert,
                embeddings=vectors_to_upsert,
                metadatas=metadatas_to_upsert,
                documents=documents_to_upsert,
            )
            logger.info(
                "[ChromaDB] Updated Collection 'industry_technologies': %d vectors upserted (%d inserted, %d updated, %d skipped).",
                len(ids_to_upsert),
                inserted,
                updated,
                skipped,
            )

        elapsed = round(time.time() - start_time, 4)
        return ChromaSyncResult(
            total_processed=total_processed,
            inserted_count=inserted,
            updated_count=updated,
            skipped_count=skipped,
            deleted_count=0,
            errors=errors,
            elapsed_seconds=elapsed,
        )

    def delete_technology(self, technology_id: str) -> bool:
        """
        Delete a technology vector document from ChromaDB by technology_id.

        Args:
            technology_id: Target technology identifier.

        Returns:
            True if deleted, False otherwise.
        """
        collection = self.collection_manager.get_or_create_collection()
        doc_id = f"vec-{technology_id}"
        try:
            collection.delete(ids=[doc_id])
            logger.info("[ChromaDB] Deleted vector for '%s' from collection.", technology_id)
            return True
        except Exception as exc:
            logger.warning("[ChromaDB] Delete vector '%s' failed: %s", technology_id, exc)
            return False

    def clear(self) -> None:
        """Clear all vectors from the collection."""
        self.collection_manager.reset()
