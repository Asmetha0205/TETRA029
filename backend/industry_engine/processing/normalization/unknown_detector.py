"""
Unknown Technology Detector for CurricuAlign AI Technology Normalization Engine.

Detects technologies that are not present in the registry. Unknowns are never
silently discarded; they are flagged, stored, and surfaced for future approval
according to the configured unknown policy.
"""

import logging
from typing import List, Optional, Tuple

from backend.industry_engine.processing.normalization.config import UnknownPolicy
from backend.industry_engine.processing.normalization.models import UnknownTechnology
from backend.industry_engine.processing.normalization.technology_registry import TechnologyRegistry

logger = logging.getLogger("industry_engine.processing.normalization.unknown_detector")


class UnknownDetector:
    """
    Flags and stores technologies that cannot be resolved to a canonical entry.
    """

    def __init__(self, registry: TechnologyRegistry, policy: UnknownPolicy = UnknownPolicy.FLAG):
        self._registry = registry
        self._policy = policy

    def is_unknown(self, value: str) -> bool:
        """Return True if the value is not registered."""
        return not self._registry.is_known(value)

    def detect(self, value: str, source_category: Optional[str] = None) -> Optional[UnknownTechnology]:
        """
        Detect whether a value is unknown.

        Returns an UnknownTechnology record when the value is unregistered,
        otherwise None.
        """
        if not isinstance(value, str) or not value.strip():
            return None
        if self.is_unknown(value):
            return UnknownTechnology(
                technology=value.strip(),
                category="Unknown",
                source_category=source_category,
            )
        return None

    def apply_policy(self, unknowns: List[UnknownTechnology]) -> Tuple[List[UnknownTechnology], int]:
        """
        Apply the configured unknown policy to a list of unknown records.

        Returns:
            (surfaced_unknowns, dropped_count)
        """
        if self._policy == UnknownPolicy.DISCARD:
            logger.info(f"[UnknownDetector] Policy={self._policy.value}: discarding {len(unknowns)} unknown technologies.")
            return [], len(unknowns)

        if unknowns:
            logger.info(
                f"[UnknownDetector] {len(unknowns)} unknown technology(ies) flagged: "
                f"{[u.technology for u in unknowns]}"
            )

        return list(unknowns), 0
