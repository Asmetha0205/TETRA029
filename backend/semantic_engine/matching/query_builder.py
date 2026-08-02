"""
Query Builder for Semantic Matching Engine.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("semantic_engine.matching.query_builder")


class MatchingQueryBuilder:
    """Constructs vector search query descriptors from academic technology records."""

    @classmethod
    def build_query(cls, academic_skill: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Build query descriptor for candidate vector lookup.

        Returns:
            Dict containing query string and metadata filter parameters.
        """
        clean_skill = academic_skill.strip()
        where_filter = {"category": category} if category and category != "Unknown" else None

        return {
            "query_text": clean_skill,
            "category": category,
            "where_filter": where_filter,
        }
