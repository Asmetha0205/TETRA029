"""
Academic Technology Normalizer Wrapper for CurricuAlign AI.

Reuses the Industry Intelligence Engine's NormalizationPipeline, TechnologyRegistry,
and AliasResolver. Converts extracted academic technology dictionary payloads into
canonical normalized technology profiles.
"""

import logging
from typing import Dict, List, Optional

from backend.industry_engine.processing.normalization.pipeline import NormalizationPipeline
from backend.industry_engine.processing.normalization.models import (
    NormalizationResult,
    NormalizedTechnology,
    TechnologyProfile,
    UnknownTechnology,
)

logger = logging.getLogger("academic_engine.normalization.academic_normalizer")


class AcademicTechnologyNormalizer:
    """
    Academic wrapper over Industry Engine's NormalizationPipeline.
    """

    def __init__(
        self,
        normalization_pipeline: Optional[NormalizationPipeline] = None,
    ) -> None:
        """Initialize Academic Technology Normalizer using Industry Engine pipeline."""
        self.pipeline = normalization_pipeline or NormalizationPipeline()

    def normalize_academic_extractions(
        self,
        extracted_categories: Dict[str, List[str]],
        job_id: str = "academic-curriculum",
    ) -> NormalizationResult:
        """
        Normalize extracted academic categories using Industry Engine TechnologyRegistry and AliasResolver.

        Args:
            extracted_categories: Dict mapping category names to lists of extracted technologies.
            job_id: Document or curriculum identifier tag.

        Returns:
            NormalizationResult containing normalized technologies, unknowns, rejected, and report.
        """
        profile = TechnologyProfile(job_id=job_id, categories=extracted_categories)
        result = self.pipeline.normalize(profile)

        logger.info(
            "[Academic] Normalization Complete: %d normalized, %d unknown technologies.",
            len(result.normalized), len(result.unknown)
        )
        return result
