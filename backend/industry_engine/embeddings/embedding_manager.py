"""
Embedding Manager for the CurricuAlign AI Embedding Engine.

High-level orchestrator coordinating the EmbeddingGenerator, EmbeddingRepository,
EmbeddingCache, and EmbeddingValidator.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.industry_engine.knowledge.knowledge_models import TechnologyKnowledgeRecord
from backend.industry_engine.embeddings.exceptions import (
    EmbeddingError,
    EmbeddingRepositoryError,
    EmbeddingValidationError,
)
from backend.industry_engine.embeddings.embedding_cache import EmbeddingCache
from backend.industry_engine.embeddings.embedding_generator import EmbeddingGenerator
from backend.industry_engine.embeddings.embedding_models import (
    BatchGenerationResult,
    EmbeddingRecord,
    EmbeddingStats,
    EmbeddingStatus,
)
from backend.industry_engine.embeddings.embedding_repository import EmbeddingRepository
from backend.industry_engine.embeddings.embedding_validator import EmbeddingValidator

logger = logging.getLogger("industry_engine.embeddings.embedding_manager")


class EmbeddingManager:
    """
    Orchestrates embedding generation, caching, storage, validation, and incremental updates.

    Cache-first strategy: checks in-memory cache and content hashes before generating new vectors.
    """

    def __init__(
        self,
        repository_path: Optional[str] = None,
        model_name: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        cache_max_size: int = 1000,
        force_fallback: bool = False,
    ) -> None:
        """
        Initialize the Embedding Manager.

        Args:
            repository_path: Optional file path for repository persistence.
            model_name: Name of sentence transformer model.
            dimension: Expected vector dimension.
            cache_max_size: Maximum cache entries.
            force_fallback: Force fallback generator for lightweight execution/testing.
        """
        self.validator = EmbeddingValidator(expected_dimension=dimension, expected_model=model_name)
        self.repository = EmbeddingRepository(storage_path=repository_path, validator=self.validator)
        self.cache = EmbeddingCache(max_size=cache_max_size)
        self.generator = EmbeddingGenerator(
            model_name=model_name,
            dimension=dimension,
            force_fallback=force_fallback,
        )

        logger.info("[Embedding] Manager initialized with model='%s', dim=%d.", model_name, dimension)

    def generate_embedding(
        self,
        record: Union[TechnologyKnowledgeRecord, Dict[str, Any]],
        force: bool = False,
    ) -> EmbeddingRecord:
        """
        Generate (or retrieve cached/existing) embedding for a technology record.

        Args:
            record: TechnologyKnowledgeRecord or dictionary representation.
            force: If True, bypasses cache and regenerates vector.

        Returns:
            Populated EmbeddingRecord.
        """
        tech_id = EmbeddingGenerator._extract_tech_id(record)
        prompt, content_hash = EmbeddingGenerator.format_text_prompt(record)

        if not force:
            # 1. Check in-memory cache by hash
            cached = self.cache.get_by_hash(content_hash)
            if cached:
                logger.info("[Embedding] Cache Hit for '%s'", tech_id)
                return cached

            # 2. Check repository by tech_id and content_hash
            existing = self.repository.get(tech_id)
            if existing and existing.embedding_hash == content_hash and existing.status == EmbeddingStatus.ACTIVE:
                logger.info("[Embedding] Skipped unchanged '%s' (hash match)", tech_id)
                self.cache.put(existing)
                return existing

        # 3. Generate new embedding
        emb_rec = self.generator.generate(record)
        self.validator.validate_record(emb_rec)

        # 4. Save to repository & cache
        self.repository.upsert(emb_rec)
        self.cache.put(emb_rec)

        logger.info("[Embedding] Generated embedding for '%s'", tech_id)
        return emb_rec

    def generate_all(
        self,
        records: List[Union[TechnologyKnowledgeRecord, Dict[str, Any]]],
        force: bool = False,
    ) -> BatchGenerationResult:
        """
        Generate embeddings for a batch of technology records.

        Args:
            records: List of TechnologyKnowledgeRecord or dict objects.
            force: If True, forces regeneration for all records.

        Returns:
            BatchGenerationResult with stats and counts.
        """
        start_time = time.time()
        to_generate: List[Tuple[int, Union[TechnologyKnowledgeRecord, Dict[str, Any]]]] = []

        total_processed = len(records)
        cached_count = 0
        skipped_count = 0
        generated_count = 0
        errors: List[Dict[str, Any]] = []

        for idx, rec in enumerate(records):
            tech_id = EmbeddingGenerator._extract_tech_id(rec)
            prompt, content_hash = EmbeddingGenerator.format_text_prompt(rec)

            if not force:
                cached = self.cache.get_by_hash(content_hash)
                if cached:
                    cached_count += 1
                    continue

                existing = self.repository.get(tech_id)
                if existing and existing.embedding_hash == content_hash and existing.status == EmbeddingStatus.ACTIVE:
                    self.cache.put(existing)
                    skipped_count += 1
                    continue

            to_generate.append((idx, rec))

        if to_generate:
            gen_records_input = [r for _, r in to_generate]
            try:
                gen_results = self.generator.generate_batch(gen_records_input)
                for emb_rec in gen_results:
                    try:
                        self.validator.validate_record(emb_rec)
                        self.repository.upsert(emb_rec)
                        self.cache.put(emb_rec)
                        generated_count += 1
                    except Exception as exc:
                        errors.append({"technology_id": emb_rec.technology_id, "error": str(exc)})
            except Exception as exc:
                errors.append({"batch_error": str(exc)})

        elapsed = round(time.time() - start_time, 4)
        logger.info(
            "[Embedding] Batch Generated: %d total, %d generated, %d cached, %d skipped in %.2fs.",
            total_processed,
            generated_count,
            cached_count,
            skipped_count,
            elapsed,
        )

        return BatchGenerationResult(
            total_processed=total_processed,
            generated_count=generated_count,
            cached_count=cached_count,
            skipped_count=skipped_count,
            errors=errors,
            generation_time_seconds=elapsed,
        )

    def regenerate_changed(
        self,
        records: List[Union[TechnologyKnowledgeRecord, Dict[str, Any]]]
    ) -> BatchGenerationResult:
        """
        Incrementally regenerate embeddings ONLY for records whose content has changed.

        Args:
            records: List of TechnologyKnowledgeRecord objects.

        Returns:
            BatchGenerationResult detailing updated vs skipped records.
        """
        return self.generate_all(records, force=False)

    def update_embedding(
        self,
        record: Union[TechnologyKnowledgeRecord, Dict[str, Any]]
    ) -> EmbeddingRecord:
        """
        Update an embedding record by re-generating it and updating repository.

        Args:
            record: TechnologyKnowledgeRecord or dict.

        Returns:
            Updated EmbeddingRecord.
        """
        return self.generate_embedding(record, force=True)

    def delete_embedding(self, technology_id: str) -> bool:
        """
        Delete an embedding record for a technology_id.

        Args:
            technology_id: Target technology identifier.

        Returns:
            True if deleted from repository/cache, False if not found.
        """
        self.cache.evict(technology_id)
        return self.repository.delete(technology_id)

    def get_embedding(self, technology_id: str) -> Optional[EmbeddingRecord]:
        """
        Retrieve an embedding record for a technology_id (cache-first).

        Args:
            technology_id: Target technology identifier.

        Returns:
            Matching EmbeddingRecord, or None.
        """
        cached = self.cache.get(technology_id)
        if cached:
            return cached

        existing = self.repository.get(technology_id)
        if existing:
            self.cache.put(existing)
            return existing

        return None

    def get_all_embeddings(self) -> List[EmbeddingRecord]:
        """Return all embedding records from the repository."""
        return self.repository.get_all()

    def validate_repository(self) -> Tuple[bool, List[str]]:
        """
        Validate all records stored in the repository.

        Returns:
            Tuple of (is_valid_bool, list_of_error_strings).
        """
        all_records = self.repository.get_all()
        errors: List[str] = []

        try:
            self.validator.validate_batch(all_records)
        except EmbeddingValidationError as exc:
            errors.append(str(exc))

        is_valid = len(errors) == 0
        logger.info(
            "[Embedding] Repository validation completed: %s (%d errors).",
            "Valid" if is_valid else "Invalid",
            len(errors),
        )
        return is_valid, errors

    def get_stats(self) -> EmbeddingStats:
        """Get aggregate engine statistics including repository and cache stats."""
        stats = self.repository.get_stats()
        stats.cache_stats = self.cache.get_stats()
        return stats

    def save(self, path: Optional[str] = None) -> Any:
        """Save repository state to disk."""
        return self.repository.save(path)

    def load(self, path: Optional[str] = None) -> int:
        """Load repository state from disk."""
        count = self.repository.load(path)
        self.cache.clear()
        return count
