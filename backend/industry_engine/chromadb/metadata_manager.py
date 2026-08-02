"""
Metadata Manager for the CurricuAlign AI ChromaDB Synchronization Layer.

Formats, cleans, and validates metadata dictionaries associated with vector embeddings
stored in the 'industry_technologies' ChromaDB collection.
"""

import logging
from typing import Any, Dict

from backend.industry_engine.chromadb.exceptions import MetadataValidationError
from backend.industry_engine.knowledge.knowledge_models import TechnologyKnowledgeRecord
from backend.industry_engine.embeddings.embedding_models import EmbeddingRecord

logger = logging.getLogger("industry_engine.chromadb.metadata_manager")


class ChromaMetadataManager:
    """
    Manages and validates metadata associated with ChromaDB vector documents.

    Converts TechnologyKnowledgeRecord and EmbeddingRecord metadata into clean,
    flat, type-safe dictionaries compliant with ChromaDB scalar type constraints (str, int, float, bool).
    """

    DEFAULT_COLLECTION_NAME = "industry_technologies"

    @classmethod
    def prepare_metadata(
        cls,
        tech_record: TechnologyKnowledgeRecord,
        emb_record: EmbeddingRecord,
    ) -> Dict[str, Any]:
        """
        Extract and format metadata from TechnologyKnowledgeRecord and EmbeddingRecord.

        Args:
            tech_record: Authoritative TechnologyKnowledgeRecord.
            emb_record: Corresponding EmbeddingRecord.

        Returns:
            Type-safe metadata dictionary ready for ChromaDB insertion.
        """
        metadata: Dict[str, Any] = {
            "technology_id": str(tech_record.technology_id),
            "canonical_name": str(tech_record.canonical_name),
            "category": str(tech_record.category),
            "demand_score": float(tech_record.demand_score),
            "industry_score": float(tech_record.industry_score),
            "frequency": int(tech_record.frequency),
            "trend": str(tech_record.trend.value if hasattr(tech_record.trend, "value") else tech_record.trend),
            "growth": float(tech_record.growth),
            "classification": str(
                tech_record.classification.value if hasattr(tech_record.classification, "value")
                else tech_record.classification
            ),
            "status": str(tech_record.status.value if hasattr(tech_record.status, "value") else tech_record.status),
            "version": str(tech_record.version.to_string() if hasattr(tech_record.version, "to_string") else tech_record.version),
            "embedding_id": str(emb_record.embedding_id),
            "embedding_version": str(emb_record.model_version),
            "embedding_hash": str(emb_record.embedding_hash),
            "model_name": str(emb_record.model_name),
        }

        if tech_record.aliases:
            metadata["aliases"] = ", ".join(sorted(tech_record.aliases))
        if tech_record.related_technologies:
            metadata["related_technologies"] = ", ".join(sorted(tech_record.related_technologies))

        cls.validate_metadata(metadata)
        return metadata

    @classmethod
    def validate_metadata(cls, metadata: Dict[str, Any]) -> None:
        """
        Validate metadata dictionary against ChromaDB payload rules.

        Args:
            metadata: Metadata dictionary to validate.

        Raises:
            MetadataValidationError: If metadata fails validation or contains illegal types.
        """
        required_fields = [
            "technology_id", "category", "demand_score", "industry_score",
            "trend", "classification", "version", "embedding_hash",
        ]
        for field in required_fields:
            if field not in metadata:
                raise MetadataValidationError(f"Missing required metadata field: '{field}'")

        for key, value in metadata.items():
            if not isinstance(value, (str, int, float, bool)):
                raise MetadataValidationError(
                    f"Metadata key '{key}' has illegal type '{type(value).__name__}'. "
                    "ChromaDB requires scalar types (str, int, float, bool)."
                )
