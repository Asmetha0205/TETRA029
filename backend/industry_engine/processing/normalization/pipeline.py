"""
Normalization Pipeline for CurricuAlign AI Technology Normalization Engine.

Orchestrates the full normalization flow:
    Technology Profile
        -> Validator
        -> Alias Resolver
        -> Canonicalizer
        -> Category Mapper
        -> Duplicate Merger
        -> Unknown Detector
        -> Normalized Technology Profile (with report)
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from backend.industry_engine.processing.normalization.alias_resolver import AliasResolver
from backend.industry_engine.processing.normalization.canonicalizer import Canonicalizer
from backend.industry_engine.processing.normalization.category_mapper import CategoryMapper
from backend.industry_engine.processing.normalization.config import NormalizationConfig
from backend.industry_engine.processing.normalization.duplicate_merger import DuplicateMerger
from backend.industry_engine.processing.normalization.exceptions import MalformedInputError
from backend.industry_engine.processing.normalization.models import (
    NormalizationReport,
    NormalizationResult,
    NormalizedTechnology,
    TechnologyProfile,
    UnknownTechnology,
)
from backend.industry_engine.processing.normalization.normalizer import TechnologyNormalizer
from backend.industry_engine.processing.normalization.technology_registry import TechnologyRegistry
from backend.industry_engine.processing.normalization.unknown_detector import UnknownDetector
from backend.industry_engine.processing.normalization.validator import TechnologyValidator

logger = logging.getLogger("industry_engine.processing.normalization.pipeline")


class NormalizationPipeline:
    """
    End-to-end Technology Normalization Engine pipeline.
    """

    def __init__(
        self,
        config: Optional[NormalizationConfig] = None,
        registry: Optional[TechnologyRegistry] = None,
    ):
        self.config = config or NormalizationConfig()
        self.normalizer = TechnologyNormalizer()
        self.registry = registry or TechnologyRegistry(config=self.config)
        self.validator = TechnologyValidator(config=self.config)
        self.alias_resolver = AliasResolver(self.registry, self.normalizer)
        self.canonicalizer = Canonicalizer(self.registry, self.normalizer)
        self.category_mapper = CategoryMapper()
        self.duplicate_merger = DuplicateMerger()
        self.unknown_detector = UnknownDetector(self.registry, policy=self.config.unknown_policy)

        self.last_result: Optional[NormalizationResult] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def normalize_raw(self, raw: Any, job_id: Optional[str] = None) -> NormalizationResult:
        """
        Normalize a raw payload (dict or JSON string) into a NormalizationResult.

        Raises:
            MalformedInputError: If a JSON string payload cannot be parsed.
        """
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError as e:
                logger.error(f"[NormalizationPipeline] Malformed JSON input: {e}")
                raise MalformedInputError(f"Malformed JSON technology profile: {e}") from e

        profile = TechnologyProfile.from_raw(raw, job_id=job_id)
        return self.normalize(profile)

    def normalize(self, profile: TechnologyProfile) -> NormalizationResult:
        """
        Execute the full normalization flow over a TechnologyProfile.
        """
        start = time.time()

        # Step 1: Validation
        valid_items, rejected = self.validator.validate_profile(profile)

        # Steps 2-4: Alias resolution, canonicalization, category mapping
        flat: List[NormalizedTechnology] = []
        unknown_records: List[UnknownTechnology] = []
        aliases_resolved = 0

        for category_key, value in valid_items:
            tech, unknown = self.canonicalizer.canonicalize(value, source_category=category_key)

            if unknown is not None:
                unknown_records.append(unknown)
                continue

            if tech is None:
                continue

            # Category mapping (registry category takes precedence)
            display_category = self.category_mapper.assign(
                canonical_name=tech.canonical_name,
                registry_category=self.registry.get_category(tech.canonical_name),
                source_category=category_key,
            )
            tech.category = display_category

            # Track alias matches
            _, match_kind = self.alias_resolver.resolve_with_kind(value)
            if match_kind == "alias":
                aliases_resolved += 1

            flat.append(tech)

        # Step 5: Duplicate merging
        normalized, duplicates_merged = self.duplicate_merger.merge(flat)

        # Step 6: Unknown detection policy
        unknown, _ = self.unknown_detector.apply_policy(unknown_records)

        # Step 7: Report
        report = NormalizationReport(
            total_technologies=sum(len(v) for v in profile.categories.values()),
            known=len(normalized),
            unknown=len(unknown),
            duplicates_merged=duplicates_merged,
            aliases_resolved=aliases_resolved,
            rejected_values=len(rejected),
        )

        result = NormalizationResult(
            normalized=normalized,
            unknown=unknown,
            rejected=rejected,
            report=report,
        )
        self.last_result = result

        elapsed = round((time.time() - start) * 1000, 2)
        logger.info(
            f"[NormalizationPipeline] Normalization complete: {len(normalized)} known, "
            f"{len(unknown)} unknown, {duplicates_merged} duplicates merged, "
            f"{aliases_resolved} aliases resolved, {len(rejected)} rejected "
            f"({elapsed}ms)."
        )

        return result

    def get_report(self) -> NormalizationReport:
        """Return the report from the last normalization run."""
        if self.last_result is None:
            raise ValueError("No normalization run has been executed yet.")
        return self.last_result.report
