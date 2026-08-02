"""
Text Normalizer for CurricuAlign AI Technology Normalization Engine.

Provides three tiers of normalization:
1. display normalization - cleaned, whitespace-collapsed form used for output.
2. soft key normalization  - lowercase + collapsed, used for exact alias matching.
3. aggressive key normalization - punctuation removed, used for fuzzy matching.
"""

import re
from typing import Any, Optional

from backend.industry_engine.processing.normalization.exceptions import InvalidTechnologyNameError


class TechnologyNormalizer:
    """
    Normalizes raw technology strings for consistent matching and display.
    """

    _WHITESPACE_RE = re.compile(r"\s+")
    _AGGRESSIVE_RE = re.compile(r"[^a-z0-9+#]")
    _SLUG_RE = re.compile(r"[^a-z0-9+#]+")

    def normalize(self, value: Any) -> str:
        """
        Produce the cleaned display form of a technology value.

        Strips surrounding whitespace and collapses all internal whitespace
        runs to a single space. Preserves case and punctuation.
        """
        if not isinstance(value, str):
            raise InvalidTechnologyNameError(f"Expected string technology name, got {type(value).__name__}")
        cleaned = value.strip()
        return self._WHITESPACE_RE.sub(" ", cleaned)

    def normalize_key_soft(self, value: str) -> str:
        """
        Lowercased, whitespace-collapsed key. Punctuation is preserved.
        Used for exact alias lookups (e.g. "Fast API" -> "fast api").
        """
        return self.normalize(value).lower()

    def normalize_key_aggressive(self, value: str) -> str:
        """
        Lowercased key with all non-alphanumeric characters removed.
        '#' and '+' are retained so C#, C++, and similar names survive.
        Used as a fuzzy fallback (e.g. "fast-api" -> "fastapi").
        """
        lowered = value.lower()
        return self._AGGRESSIVE_RE.sub("", lowered)

    def slugify(self, value: str) -> str:
        """
        Generate a URL-safe canonical ID from a canonical name.
        E.g. "Machine Learning" -> "machine-learning".
        """
        lowered = value.lower().strip()
        slug = self._SLUG_RE.sub("-", lowered).strip("-")
        return slug or "unknown"

    def canonical_id(self, value: str, explicit_id: Optional[str] = None) -> str:
        """
        Resolve the canonical ID for a technology name.

        If an explicit ID is provided it is normalized and returned,
        otherwise it is derived from the canonical name.
        """
        if explicit_id:
            return self.slugify(explicit_id)
        return self.slugify(value)
