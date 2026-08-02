"""
Alias Resolver for CurricuAlign AI Technology Normalization Engine.

Maps raw technology values to their canonical names using the registry's
alias index. Supports one-alias -> one-canonical resolution and tracks
whether a match came through an alias or a direct canonical hit.
"""

import logging
from typing import Dict, List, Optional, Tuple

from backend.industry_engine.processing.normalization.normalizer import TechnologyNormalizer
from backend.industry_engine.processing.normalization.technology_registry import TechnologyRegistry

logger = logging.getLogger("industry_engine.processing.normalization.alias_resolver")

# Match kind returned by resolve_with_kind()
MATCH_DIRECT = "direct"  # value matched the canonical name itself
MATCH_ALIAS = "alias"    # value matched a registered alias


class AliasResolver:
    """
    Resolves raw technology values to canonical technology names.
    """

    def __init__(self, registry: TechnologyRegistry, normalizer: Optional[TechnologyNormalizer] = None):
        self._registry = registry
        self._normalizer = normalizer or TechnologyNormalizer()

    def resolve(self, value: str) -> Optional[str]:
        """
        Return the canonical name for a raw value, or None if unknown.
        """
        return self._registry.resolve(value)

    def resolve_with_kind(self, value: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Resolve a value and report whether it matched directly or via alias.

        Returns:
            (canonical_name, match_kind) where match_kind is one of
            MATCH_DIRECT, MATCH_ALIAS, or None when the value is unknown.
        """
        canonical = self._registry.resolve(value)
        if canonical is None:
            return None, None

        value_key = self._normalizer.normalize_key_aggressive(value)
        canonical_key = self._normalizer.normalize_key_aggressive(canonical)
        if value_key == canonical_key:
            return canonical, MATCH_DIRECT
        return canonical, MATCH_ALIAS

    def resolve_batch(self, values: List[str]) -> Dict[str, Optional[str]]:
        """
        Resolve a batch of values at once.
        """
        return {value: self.resolve(value) for value in values}

    def registry(self) -> TechnologyRegistry:
        """Expose the underlying registry."""
        return self._registry
