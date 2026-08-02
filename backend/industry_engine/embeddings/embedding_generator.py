"""
Embedding Generator for the CurricuAlign AI Embedding Engine.

Converts TechnologyKnowledgeRecord instances into dense vector embeddings using
SentenceTransformers (all-MiniLM-L6-v2 by default).

Supports lazy loading, singleton model caching, batch vector generation,
deterministic text prompt construction, and SHA-256 content hashing.
"""

import hashlib
import logging
import math
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.industry_engine.knowledge.knowledge_models import TechnologyKnowledgeRecord
from backend.industry_engine.embeddings.exceptions import EmbeddingGenerationError, ModelLoadError
from backend.industry_engine.embeddings.embedding_models import EmbeddingRecord, EmbeddingStatus

logger = logging.getLogger("industry_engine.embeddings.embedding_generator")

# Optional import for sentence_transformers
_SENTENCE_TRANSFORMERS_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    _SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    _SENTENCE_TRANSFORMERS_AVAILABLE = False


class EmbeddingGenerator:
    """
    Generates dense vector embeddings for technology records.

    Uses lazy loading for the underlying SentenceTransformer model to minimize startup overhead.
    Constructs standardized, text-only prompts from TechnologyKnowledgeRecord data, excluding
    dynamic intelligence metrics (scores, trends, versions).
    """

    _model_instance: Optional[Any] = None
    _loaded_model_name: Optional[str] = None

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        force_fallback: bool = False,
    ) -> None:
        """
        Initialize the embedding generator configuration.

        Args:
            model_name: Name or path of the SentenceTransformer model.
            dimension: Dimension size expected from the embedding model.
            force_fallback: If True, forces deterministic fallback vector generation (for testing/lightweight mode).
        """
        self.model_name = model_name
        self.dimension = dimension
        self.force_fallback = force_fallback
        logger.info(
            "[Embedding] Generator configured with model='%s', dimension=%d.",
            self.model_name,
            self.dimension,
        )

    def generate(self, record: Union[TechnologyKnowledgeRecord, Dict[str, Any]]) -> EmbeddingRecord:
        """
        Generate an embedding record for a single technology record.

        Args:
            record: TechnologyKnowledgeRecord or dictionary representation.

        Returns:
            Populated EmbeddingRecord containing the vector and SHA-256 content hash.
        """
        prompt, content_hash = self.format_text_prompt(record)
        tech_id = self._extract_tech_id(record)

        vector = self._encode_text(prompt)

        embedding_id = f"emb-{tech_id}"
        return EmbeddingRecord(
            embedding_id=embedding_id,
            technology_id=tech_id,
            model_name=self.model_name,
            model_version="1.0.0",
            embedding_dimension=len(vector),
            embedding_vector=vector,
            embedding_hash=content_hash,
            status=EmbeddingStatus.ACTIVE,
            text_content=prompt,
            metadata={
                "vector_norm": round(math.sqrt(sum(x ** 2 for x in vector)), 4),
                "prompt_length": len(prompt),
                "generator_engine": "sentence_transformers" if (
                    _SENTENCE_TRANSFORMERS_AVAILABLE and not self.force_fallback
                ) else "deterministic_fallback",
            },
        )

    def generate_batch(
        self, records: List[Union[TechnologyKnowledgeRecord, Dict[str, Any]]]
    ) -> List[EmbeddingRecord]:
        """
        Generate embedding records for a batch of technology records.

        Args:
            records: List of TechnologyKnowledgeRecord or dict objects.

        Returns:
            List of generated EmbeddingRecord objects.
        """
        if not records:
            return []

        prompts_and_hashes = [self.format_text_prompt(r) for r in records]
        prompts = [p for p, _ in prompts_and_hashes]
        hashes = [h for _, h in prompts_and_hashes]
        tech_ids = [self._extract_tech_id(r) for r in records]

        vectors = self._encode_batch(prompts)

        results: List[EmbeddingRecord] = []
        for i in range(len(records)):
            tech_id = tech_ids[i]
            vector = vectors[i]
            content_hash = hashes[i]
            prompt = prompts[i]
            emb_rec = EmbeddingRecord(
                embedding_id=f"emb-{tech_id}",
                technology_id=tech_id,
                model_name=self.model_name,
                model_version="1.0.0",
                embedding_dimension=len(vector),
                embedding_vector=vector,
                embedding_hash=content_hash,
                status=EmbeddingStatus.ACTIVE,
                text_content=prompt,
                metadata={
                    "vector_norm": round(math.sqrt(sum(x ** 2 for x in vector)), 4),
                    "prompt_length": len(prompt),
                    "generator_engine": "sentence_transformers" if (
                        _SENTENCE_TRANSFORMERS_AVAILABLE and not self.force_fallback
                    ) else "deterministic_fallback",
                },
            )
            results.append(emb_rec)

        logger.info("[Embedding] Batch Generated %d embeddings using '%s'.", len(results), self.model_name)
        return results

    @classmethod
    def format_text_prompt(
        cls, record: Union[TechnologyKnowledgeRecord, Dict[str, Any]]
    ) -> Tuple[str, str]:
        """
        Format a technology record into a standardized, text-only prompt for embedding.

        EXCLUDES dynamic scores, rankings, trends, growth, and version information.
        INCLUDES canonical name, category, aliases, description, and related technologies.

        Args:
            record: TechnologyKnowledgeRecord or dictionary representation.

        Returns:
            Tuple of (formatted_text_prompt, sha256_content_hash).
        """
        rec_dict = record.model_dump() if hasattr(record, "model_dump") else dict(record)

        canonical_name = str(rec_dict.get("canonical_name", "")).strip()
        category = str(rec_dict.get("category", "")).strip()
        aliases = sorted(list(set(rec_dict.get("aliases", []))))
        description = str(rec_dict.get("description", "")).strip()
        related = sorted(list(set(rec_dict.get("related_technologies", []))))

        lines = [
            f"Technology: {canonical_name}",
            f"Category: {category}",
        ]
        if aliases:
            lines.append(f"Aliases: {', '.join(aliases)}")
        if description:
            lines.append(f"Description: {description}")
        if related:
            lines.append(f"Related Technologies: {', '.join(related)}")

        prompt_text = "\n".join(lines).strip()
        content_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()

        return prompt_text, content_hash

    # ------------------------------------------------------------------
    # Model Management & Encoding
    # ------------------------------------------------------------------

    def _get_model(self) -> Optional[Any]:
        """Lazy loader for SentenceTransformer model instance (Singleton)."""
        if self.force_fallback or not _SENTENCE_TRANSFORMERS_AVAILABLE:
            return None

        if (
            EmbeddingGenerator._model_instance is not None
            and EmbeddingGenerator._loaded_model_name == self.model_name
        ):
            return EmbeddingGenerator._model_instance

        try:
            logger.info("[Embedding] Loading SentenceTransformer model '%s'...", self.model_name)
            model = SentenceTransformer(self.model_name)
            EmbeddingGenerator._model_instance = model
            EmbeddingGenerator._loaded_model_name = self.model_name
            logger.info("[Embedding] Model '%s' loaded successfully.", self.model_name)
            return model
        except Exception as exc:
            logger.warning(
                "[Embedding] Failed to load SentenceTransformer '%s': %s. Falling back to deterministic vector projection.",
                self.model_name,
                exc,
            )
            return None

    def _encode_text(self, text: str) -> List[float]:
        """Encode a single text prompt into a unit-normalized float vector."""
        model = self._get_model()
        if model is not None:
            try:
                raw_vec = model.encode(text, convert_to_numpy=True)
                vec = [float(x) for x in raw_vec]
                return self._normalize_vector(vec)
            except Exception as exc:
                logger.error("[Embedding] Error during model encoding: %s", exc)

        return self._generate_fallback_vector(text)

    def _encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Encode a list of text prompts into unit-normalized float vectors."""
        model = self._get_model()
        if model is not None:
            try:
                raw_vecs = model.encode(texts, convert_to_numpy=True)
                results = []
                for rv in raw_vecs:
                    vec = [float(x) for x in rv]
                    results.append(self._normalize_vector(vec))
                return results
            except Exception as exc:
                logger.error("[Embedding] Error during batch model encoding: %s", exc)

        return [self._generate_fallback_vector(t) for t in texts]

    def _generate_fallback_vector(self, text: str) -> List[float]:
        """
        Generate a deterministic, pseudo-random unit vector derived from text SHA-256 hash.

        Used when sentence_transformers is unavailable or in test environments.
        Guarantees:
        1. Dimension == self.dimension (384).
        2. Unit norm (length == 1.0).
        3. Deterministic: Identical text always yields identical vector.
        """
        vector = []
        # Generate dimension float values deterministically from iterated hashes
        seed_bytes = hashlib.sha256(text.encode("utf-8")).digest()
        curr_bytes = seed_bytes

        for i in range(self.dimension):
            if i > 0 and i % 16 == 0:
                curr_bytes = hashlib.sha256(curr_bytes + i.to_bytes(4, "big")).digest()
            byte_val = curr_bytes[i % len(curr_bytes)]
            # Map byte [0, 255] to [-1.0, 1.0]
            val = ((byte_val / 255.0) * 2.0) - 1.0
            vector.append(val)

        return self._normalize_vector(vector)

    @staticmethod
    def _normalize_vector(vector: List[float]) -> List[float]:
        """Normalize a vector to unit L2 norm."""
        norm_sq = sum(x ** 2 for x in vector)
        if norm_sq == 0:
            return vector
        norm = math.sqrt(norm_sq)
        return [round(x / norm, 6) for x in vector]

    @staticmethod
    def _extract_tech_id(record: Union[TechnologyKnowledgeRecord, Dict[str, Any]]) -> str:
        """Extract technology_id from record object or dict."""
        if hasattr(record, "technology_id"):
            return getattr(record, "technology_id")
        if isinstance(record, dict):
            tid = record.get("technology_id") or record.get("id") or ""
            if tid:
                return str(tid)
            cname = record.get("canonical_name", "")
            return re.sub(r"[^a-z0-9]+", "-", str(cname).lower().strip()).strip("-") or "unknown"
        return "unknown"
