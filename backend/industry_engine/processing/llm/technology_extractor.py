"""
Technology Extractor for CurricuAlign AI LLM Technology Intelligence Engine.
Main orchestrator: Cache → Prompt → Gemini → Parse → Validate → Result.
"""

import logging
import time
from typing import Optional, Callable, Dict, Any

from backend.industry_engine.models.clean_job import CleanJob
from backend.industry_engine.processing.llm.models import (
    TechnologyExtraction,
    TechnologyCategories,
    LLMConfig,
    LLMExecutionStats,
)
from backend.industry_engine.processing.llm.cache import TechnologyExtractionCache
from backend.industry_engine.processing.llm.prompt_builder import PromptBuilder
from backend.industry_engine.processing.llm.gemini_client import GeminiClient, GeminiAPIError
from backend.industry_engine.processing.llm.response_parser import ResponseParser

logger = logging.getLogger("industry_engine.processing.llm.technology_extractor")


class TechnologyExtractor:
    """
    Orchestrates the full technology extraction pipeline:
    1. Check cache for existing extraction.
    2. Build structured prompt from job details.
    3. Call Gemini LLM via GeminiClient.
    4. Parse and validate the response.
    5. Cache the validated result.
    6. Return TechnologyExtraction with execution stats.
    """

    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        cache: Optional[TechnologyExtractionCache] = None,
        mock_response_fn: Optional[Callable] = None,
        strict_presence_check: bool = True,
    ):
        """
        Initialize the Technology Extractor.

        Args:
            config: LLM configuration. Uses defaults if None.
            cache: Technology extraction cache instance. Creates in-memory cache if None.
            mock_response_fn: Optional mock callable for testing without live API.
            strict_presence_check: If True, prune any technology not explicitly found in source text.
        """
        self._config = config or LLMConfig()
        self._cache = cache or TechnologyExtractionCache()
        self._prompt_builder = PromptBuilder()
        self._gemini_client = GeminiClient(config=self._config, mock_response_fn=mock_response_fn)
        self._response_parser = ResponseParser(strict_presence_check=strict_presence_check)

        logger.info(
            f"[TechnologyExtractor] Initialized with model={self._config.model_name}, "
            f"temperature={self._config.temperature}, max_tokens={self._config.max_tokens}, "
            f"retries={self._config.retry_count}, timeout={self._config.timeout}s"
        )

    def extract_from_clean_job(self, clean_job: CleanJob) -> TechnologyExtraction:
        """
        Extract technologies from a CleanJob instance.

        Args:
            clean_job: Cleaned and normalized job posting.

        Returns:
            Validated TechnologyExtraction result.
        """
        return self.extract(
            job_id=clean_job.job_id,
            title=clean_job.title,
            company=clean_job.company,
            location=clean_job.location,
            clean_description=clean_job.clean_description,
        )

    def extract(
        self,
        job_id: str,
        title: str,
        company: str,
        location: str,
        clean_description: str,
    ) -> TechnologyExtraction:
        """
        Full extraction pipeline for a single job posting.

        Args:
            job_id: Unique job identifier.
            title: Normalized job title.
            company: Hiring company name.
            location: Job location.
            clean_description: Cleaned job description text.

        Returns:
            Validated TechnologyExtraction result with execution stats.

        Raises:
            GeminiAPIError: If the Gemini API fails after all retries.
            ValueError: If parsing or validation fails irrecoverably.
        """
        pipeline_start = time.time()

        # --- Step 1: Cache Check ---
        cached = self._cache.get(job_id, clean_description)
        if cached is not None:
            # Update stats to reflect cache hit
            if cached.stats:
                cached.stats.cache_hit = True
            else:
                cached.stats = LLMExecutionStats(cache_hit=True)

            elapsed = round((time.time() - pipeline_start) * 1000, 2)
            logger.info(
                f"[TechnologyExtractor] Cache HIT for job_id='{job_id}' — "
                f"skipping LLM call ({elapsed}ms)"
            )
            return cached

        # --- Step 2: Build Prompt ---
        prompt_payload = self._prompt_builder.build_full_prompt(
            job_id=job_id,
            title=title,
            company=company,
            location=location,
            clean_description=clean_description,
        )

        logger.info(f"[TechnologyExtractor] Sending extraction request for job_id='{job_id}'")

        # --- Step 3: Call Gemini ---
        try:
            result = self._gemini_client.generate(
                system_prompt=prompt_payload["system_prompt"],
                user_prompt=prompt_payload["user_prompt"],
            )
        except GeminiAPIError as e:
            logger.error(f"[TechnologyExtractor] Gemini API call failed for job_id='{job_id}': {e}")
            raise

        raw_text = result["text"]
        stats: LLMExecutionStats = result["stats"]

        # --- Step 4: Parse and Validate ---
        try:
            extraction = self._response_parser.parse_response(
                raw_text=raw_text,
                job_id=job_id,
                source_text=clean_description,
                stats=stats,
            )
        except ValueError as e:
            logger.error(
                f"[TechnologyExtractor] Response parsing failed for job_id='{job_id}': {e}"
            )
            raise

        # --- Step 5: Cache Result ---
        self._cache.set(job_id, clean_description, extraction)

        elapsed = round((time.time() - pipeline_start) * 1000, 2)
        total_techs = sum(
            len(getattr(extraction.technologies, field))
            for field in TechnologyCategories.model_fields
        )

        logger.info(
            f"[TechnologyExtractor] Extraction complete for job_id='{job_id}': "
            f"{total_techs} technologies extracted, "
            f"latency={elapsed}ms, "
            f"prompt_tokens={stats.prompt_tokens}, "
            f"completion_tokens={stats.completion_tokens}"
        )

        return extraction

    def get_cache_stats(self) -> Dict[str, Any]:
        """Return cache performance statistics."""
        return self._cache.get_stats()

    def clear_cache(self) -> None:
        """Clear the extraction cache."""
        self._cache.clear()
