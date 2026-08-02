"""
Canonicalizer for CurricuAlign AI Technology Normalization Engine.

Transforms a resolved technology value into its canonical Technology record
(id, canonical_name, category, aliases, normalized_name, status).
"""

import logging
from typing import Optional, Tuple

from backend.industry_engine.processing.normalization.models import (
    NormalizedTechnology,
    TechnologyStatus,
    UnknownTechnology,
)
from backend.industry_engine.processing.normalization.normalizer import TechnologyNormalizer
from backend.industry_engine.processing.normalization.technology_registry import TechnologyEntry, TechnologyRegistry

logger = logging.getLogger("industry_engine.processing.normalization.canonicalizer")


class Canonicalizer:
    """
    Builds canonical Technology records for resolved values and flags
    unresolved values as unknown technologies.
    """

    def __init__(self, registry: TechnologyRegistry, normalizer: Optional[TechnologyNormalizer] = None):
        self._registry = registry
        self._normalizer = normalizer or TechnologyNormalizer()

    def canonicalize(
        self,
        value: str,
        source_category: Optional[str] = None,
    ) -> Tuple[Optional[NormalizedTechnology], Optional[UnknownTechnology]]:
        """
        Convert a single raw value into a canonical record.

        Returns:
            (NormalizedTechnology, None) when the value resolves to a known
            technology, or (None, UnknownTechnology) when it does not.
        """
        cleaned = self._normalizer.normalize(value)
        if not cleaned:
            return None, None

        canonical_name = self._registry.resolve(cleaned)
        if canonical_name is None:
            unknown = UnknownTechnology(
                technology=cleaned,
                category="Unknown",
                source_category=source_category,
            )
            return None, unknown

        entry = self._registry.get_entry(canonical_name)
        if entry is None:
            logger.warning(
                f"[Canonicalizer] Resolved '{cleaned}' to '{canonical_name}' but no entry exists."
            )
            return None, UnknownTechnology(
                technology=cleaned,
                category="Unknown",
                source_category=source_category,
            )

        tech = self._build_technology(entry, cleaned, source_category)
        return tech, None

    def _build_technology(
        self,
        entry: TechnologyEntry,
        normalized_name: str,
        source_category: Optional[str],
    ) -> NormalizedTechnology:
        return NormalizedTechnology(
            id=entry.id,
            canonical_name=entry.canonical_name,
            category=entry.category,
            aliases=list(entry.aliases),
            normalized_name=normalized_name,
            status=TechnologyStatus.KNOWN,
            matched_variants=[normalized_name],
            source_category=source_category,
        )
