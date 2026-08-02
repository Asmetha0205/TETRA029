"""
Embedding Service for the CurricuAlign AI Embedding Engine.

Provides the primary business facade connecting the Knowledge Layer (KnowledgeService)
with the Embedding Engine (EmbeddingManager).

Controllers, pipelines, and downstream vector sync modules MUST interact with the
embedding engine exclusively through this service.
"""

import math
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.industry_engine.knowledge.knowledge_models import TechnologyKnowledgeRecord
from backend.industry_engine.knowledge.knowledge_service import KnowledgeService
from backend.industry_engine.embeddings.exceptions import EmbeddingError, EmbeddingValidationError
from backend.industry_engine.embeddings.embedding_manager import EmbeddingManager
from backend.industry_engine.embeddings.embedding_models import (
    BatchGenerationResult,
    EmbeddingRecord,
    EmbeddingStats,
    EmbeddingStatus,
)

logger = logging.getLogger("industry_engine.embeddings.embedding_service")


class EmbeddingService:
    """
    Business facade for the Embedding Engine.

    Bridge between Knowledge Layer records and vector embeddings.
    Provides vector creation, batch sync, similarity search, and persistence.
    """

    def __init__(
        self,
        knowledge_service: Optional[KnowledgeService] = None,
        repository_path: Optional[str] = None,
        model_name: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        force_fallback: bool = False,
    ) -> None:
        """
        Initialize the Embedding Service.

        Args:
            knowledge_service: Optional KnowledgeService instance for data integration.
            repository_path: Optional file path for embedding repository JSON persistence.
            model_name: Name of SentenceTransformer model.
            dimension: Expected vector dimension.
            force_fallback: Force fallback mode (for lightweight testing).
        """
        self._knowledge_service = knowledge_service
        self._manager = EmbeddingManager(
            repository_path=repository_path,
            model_name=model_name,
            dimension=dimension,
            force_fallback=force_fallback,
        )
        logger.info("[Embedding] Service initialized.")

    def set_knowledge_service(self, knowledge_service: KnowledgeService) -> None:
        """Assign or update the connected KnowledgeService instance."""
        self._knowledge_service = knowledge_service

    # ------------------------------------------------------------------
    # Core Embedding Operations
    # ------------------------------------------------------------------

    def generate_for_technology(
        self,
        technology_id: str,
        force: bool = False,
    ) -> EmbeddingRecord:
        """
        Generate (or retrieve) embedding for a technology ID using Knowledge Layer data.

        Args:
            technology_id: Unique technology identifier.
            force: Force regeneration even if cached.

        Returns:
            The generated EmbeddingRecord.

        Raises:
            EmbeddingError: If technology is not found in Knowledge Layer.
        """
        if not self._knowledge_service:
            raise EmbeddingError("KnowledgeService not connected to EmbeddingService.")

        tech_record = self._knowledge_service.get_technology(technology_id)
        return self._manager.generate_embedding(tech_record, force=force)

    def generate_all_from_knowledge(
        self,
        force: bool = False,
    ) -> BatchGenerationResult:
        """
        Fetch all records from Knowledge Layer and generate embeddings for them.

        Args:
            force: Force regeneration for all records.

        Returns:
            BatchGenerationResult with execution statistics.
        """
        if not self._knowledge_service:
            raise EmbeddingError("KnowledgeService not connected to EmbeddingService.")

        tech_records = self._knowledge_service.get_all()
        logger.info(
            "[Embedding] Syncing embeddings for %d Knowledge Layer technologies...",
            len(tech_records),
        )
        return self._manager.generate_all(tech_records, force=force)

    def generate_embedding_for_record(
        self,
        record: Union[TechnologyKnowledgeRecord, Dict[str, Any]],
        force: bool = False,
    ) -> EmbeddingRecord:
        """Generate embedding directly for a TechnologyKnowledgeRecord or dict."""
        return self._manager.generate_embedding(record, force=force)

    def regenerate_changed(self) -> BatchGenerationResult:
        """
        Check Knowledge Layer records and incrementally regenerate ONLY modified ones.

        Returns:
            BatchGenerationResult detailing generated vs skipped counts.
        """
        if not self._knowledge_service:
            raise EmbeddingError("KnowledgeService not connected to EmbeddingService.")

        tech_records = self._knowledge_service.get_all()
        return self._manager.regenerate_changed(tech_records)

    def get_embedding(self, technology_id: str) -> Optional[EmbeddingRecord]:
        """Retrieve embedding record for a technology_id."""
        return self._manager.get_embedding(technology_id)

    def get_all_embeddings(self) -> List[EmbeddingRecord]:
        """Retrieve all stored embedding records."""
        return self._manager.get_all_embeddings()

    def delete_embedding(self, technology_id: str) -> bool:
        """Delete embedding record for a technology_id."""
        return self._manager.delete_embedding(technology_id)

    # ------------------------------------------------------------------
    # Vector Similarity Search
    # ------------------------------------------------------------------

    def search_similar(
        self,
        query: Union[str, List[float]],
        limit: int = 10,
        min_similarity: float = 0.0,
    ) -> List[Tuple[EmbeddingRecord, float]]:
        """
        Search for most similar embeddings using cosine similarity.

        Args:
            query: Either a raw query text string or a float query vector.
            limit: Maximum number of results to return.
            min_similarity: Minimum cosine similarity threshold (0.0 to 1.0).

        Returns:
            List of (EmbeddingRecord, similarity_score) tuples sorted descending.
        """
        if isinstance(query, str):
            query_vector = self._manager.generator._encode_text(query)
        else:
            query_vector = query

        all_embeddings = self._manager.get_all_embeddings()
        scored: List[Tuple[EmbeddingRecord, float]] = []

        for emb in all_embeddings:
            if emb.status != EmbeddingStatus.ACTIVE:
                continue
            sim = self._cosine_similarity(query_vector, emb.embedding_vector)
            if sim >= min_similarity:
                scored.append((emb, round(sim, 4)))

        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:limit]

    # ------------------------------------------------------------------
    # Statistics & Maintenance
    # ------------------------------------------------------------------

    def get_statistics(self) -> EmbeddingStats:
        """Compute aggregate statistics for the Embedding Engine."""
        return self._manager.get_stats()

    def validate_engine(self) -> Tuple[bool, List[str]]:
        """Validate repository and vector consistency."""
        return self._manager.validate_repository()

    def save(self, path: Optional[str] = None) -> Path:
        """Save embedding repository to disk."""
        return self._manager.save(path)

    def load(self, path: Optional[str] = None) -> int:
        """Load embedding repository from disk."""
        return self._manager.load(path)

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two float vectors."""
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a ** 2 for a in vec_a))
        norm_b = math.sqrt(sum(b ** 2 for b in vec_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return max(-1.0, min(1.0, dot_product / (norm_a * norm_b)))
