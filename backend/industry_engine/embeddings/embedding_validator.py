"""
Embedding Validator for the CurricuAlign AI Embedding Engine.

Provides comprehensive validation of embedding vectors, records, and repositories
to ensure numerical stability, dimension consistency, and structural integrity.
"""

import math
import logging
from typing import List, Optional, Set

from backend.industry_engine.embeddings.exceptions import EmbeddingValidationError
from backend.industry_engine.embeddings.embedding_models import EmbeddingRecord, EmbeddingStatus

logger = logging.getLogger("industry_engine.embeddings.embedding_validator")


class EmbeddingValidator:
    """
    Validates vector embeddings and EmbeddingRecord objects.

    Ensures vectors meet numerical constraints, expected dimensionality,
    non-null criteria, and uniqueness rules.
    """

    def __init__(self, expected_dimension: int = 384, expected_model: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize the validator.

        Args:
            expected_dimension: Dimension size expected from the embedding model.
            expected_model: Model name expected for consistency.
        """
        self._expected_dimension = expected_dimension
        self._expected_model = expected_model

    def validate_vector(
        self,
        vector: List[float],
        expected_dim: Optional[int] = None,
    ) -> None:
        """
        Validate a raw float vector.

        Args:
            vector: List of floating-point values.
            expected_dim: Expected dimension override.

        Raises:
            EmbeddingValidationError: If validation fails.
        """
        target_dim = expected_dim or self._expected_dimension

        if not isinstance(vector, list) or len(vector) == 0:
            raise EmbeddingValidationError("Embedding vector must be a non-empty list of floats.")

        if len(vector) != target_dim:
            raise EmbeddingValidationError(
                f"Embedding dimension mismatch: expected {target_dim}, got {len(vector)}."
            )

        norm_sq = 0.0
        for i, val in enumerate(vector):
            if not isinstance(val, (int, float)):
                raise EmbeddingValidationError(f"Invalid non-numeric value at index {i}: {val}")
            if math.isnan(val):
                raise EmbeddingValidationError(f"NaN detected in embedding vector at index {i}.")
            if math.isinf(val):
                raise EmbeddingValidationError(f"Infinity detected in embedding vector at index {i}.")
            norm_sq += float(val) ** 2

        if norm_sq == 0.0:
            raise EmbeddingValidationError("Zero-vector detected (vector norm is 0).")

    def validate_record(self, record: EmbeddingRecord) -> None:
        """
        Validate a complete EmbeddingRecord object.

        Args:
            record: The EmbeddingRecord to validate.

        Raises:
            EmbeddingValidationError: If validation fails.
        """
        if not record:
            raise EmbeddingValidationError("EmbeddingRecord cannot be None.")

        if not record.embedding_id or not record.embedding_id.strip():
            raise EmbeddingValidationError("embedding_id must be a non-empty string.")

        if not record.technology_id or not record.technology_id.strip():
            raise EmbeddingValidationError("technology_id must be a non-empty string.")

        if not record.embedding_hash or not record.embedding_hash.strip():
            raise EmbeddingValidationError("embedding_hash must be a non-empty string.")

        if record.embedding_dimension != self._expected_dimension:
            logger.warning(
                "[Embedding] Record dimension %d differs from validator default %d.",
                record.embedding_dimension,
                self._expected_dimension,
            )

        self.validate_vector(record.embedding_vector, expected_dim=record.embedding_dimension)

    def validate_batch(self, records: List[EmbeddingRecord]) -> None:
        """
        Validate a batch of records, checking for internal duplicate IDs.

        Args:
            records: List of EmbeddingRecord objects.

        Raises:
            EmbeddingValidationError: If any record fails or duplicate IDs exist.
        """
        seen_emb_ids: Set[str] = set()
        seen_tech_ids: Set[str] = set()

        for idx, rec in enumerate(records):
            try:
                self.validate_record(rec)
            except EmbeddingValidationError as exc:
                raise EmbeddingValidationError(f"Record at batch index {idx} invalid: {exc}") from exc

            if rec.embedding_id in seen_emb_ids:
                raise EmbeddingValidationError(f"Duplicate embedding_id '{rec.embedding_id}' in batch.")
            seen_emb_ids.add(rec.embedding_id)

            if rec.technology_id in seen_tech_ids:
                raise EmbeddingValidationError(f"Duplicate technology_id '{rec.technology_id}' in batch.")
            seen_tech_ids.add(rec.technology_id)
