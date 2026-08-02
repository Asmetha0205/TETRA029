"""
Extraction Validator for Academic Technology Extraction.

Strips empty strings, removes duplicates, and filters illegal values.
"""

import logging
from typing import Dict, List

logger = logging.getLogger("academic_engine.extraction.validator")


class ExtractionValidator:
    """Validates and cleans extracted technology dicts."""

    @classmethod
    def validate_and_clean(cls, raw_categories: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Clean and validate extracted categories dict.

        Returns:
            Cleaned categories dict with unique, non-empty technology names.
        """
        cleaned: Dict[str, List[str]] = {}
        for cat, items in raw_categories.items():
            clean_cat = str(cat).strip().lower().replace(" ", "_")
            seen = set()
            valid_items = []
            for item in items:
                val = str(item).strip()
                val_lower = val.lower()
                if val and len(val) >= 2 and val_lower not in seen:
                    seen.add(val_lower)
                    valid_items.append(val)
            if valid_items:
                cleaned[clean_cat] = valid_items

        return cleaned
