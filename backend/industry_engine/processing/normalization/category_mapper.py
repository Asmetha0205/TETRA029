"""
Category Mapper for CurricuAlign AI Technology Normalization Engine.

Assigns canonical categories to technologies. Known technologies receive
their registry category; the LLM extraction category key is translated to a
human-readable display label; unknown input categories are handled gracefully.
"""

import logging
from typing import Optional

from backend.industry_engine.processing.normalization.models import (
    CATEGORY_DISPLAY,
    UNKNOWN_CATEGORY,
    VALID_CATEGORY_KEYS,
)

logger = logging.getLogger("industry_engine.processing.normalization.category_mapper")


class CategoryMapper:
    """
    Maps technologies and input category keys to canonical display categories.
    """

    def to_display(self, category_key: Optional[str]) -> str:
        """
        Translate an LLM category key into a display category label.

        Unknown keys are returned verbatim with a warning instead of raising.
        """
        if not category_key:
            return UNKNOWN_CATEGORY
        key = category_key.strip().lower()
        if key in CATEGORY_DISPLAY:
            return CATEGORY_DISPLAY[key]
        logger.warning(f"[CategoryMapper] Unrecognized category key '{category_key}', using verbatim.")
        return category_key.strip() or UNKNOWN_CATEGORY

    def is_valid_category(self, category_key: Optional[str]) -> bool:
        """Return True if the category key is a recognized LLM category."""
        return bool(category_key) and category_key.strip().lower() in VALID_CATEGORY_KEYS

    def assign(
        self,
        canonical_name: str,
        registry_category: Optional[str],
        source_category: Optional[str] = None,
    ) -> str:
        """
        Assign a category to a technology.

        Priority:
          1. Registry category for known technologies.
          2. Display label derived from the source LLM category key.
          3. "Unknown" fallback.
        """
        if registry_category:
            return registry_category
        return self.to_display(source_category)
