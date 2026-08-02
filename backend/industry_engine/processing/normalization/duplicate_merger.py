"""
Duplicate Merger for CurricuAlign AI Technology Normalization Engine.

Merges multiple normalized technology records that resolve to the same
canonical technology. Combines matched variants and alias sets and reports
how many duplicates were collapsed.
"""

import logging
from typing import Dict, List, Tuple

from backend.industry_engine.processing.normalization.models import NormalizedTechnology

logger = logging.getLogger("industry_engine.processing.normalization.duplicate_merger")


class DuplicateMerger:
    """
    Collapses duplicate technology records into a single canonical record.
    """

    def merge(self, technologies: List[NormalizedTechnology]) -> Tuple[List[NormalizedTechnology], int]:
        """
        Merge technologies sharing a canonical name.

        Returns:
            (merged_technologies, duplicate_count) where duplicate_count is the
            number of records that were absorbed into an existing record.
        """
        merged_map: Dict[str, NormalizedTechnology] = {}
        duplicate_count = 0

        for tech in technologies:
            key = tech.canonical_name
            if key in merged_map:
                existing = merged_map[key]
                self._merge_variants(existing, tech)
                duplicate_count += 1
                logger.debug(
                    f"[DuplicateMerger] Merged '{tech.normalized_name}' into '{key}' "
                    f"(now {len(existing.matched_variants)} variants)."
                )
            else:
                merged_map[key] = tech.model_copy(deep=True)

        if duplicate_count:
            logger.info(
                f"[DuplicateMerger] Merged {duplicate_count} duplicate record(s) into "
                f"{len(merged_map)} canonical technologies."
            )

        return list(merged_map.values()), duplicate_count

    def _merge_variants(
        self,
        target: NormalizedTechnology,
        source: NormalizedTechnology,
    ) -> None:
        for variant in source.matched_variants:
            if variant not in target.matched_variants:
                target.matched_variants.append(variant)
        for alias in source.aliases:
            if alias not in target.aliases:
                target.aliases.append(alias)
        if target.source_category is None and source.source_category is not None:
            target.source_category = source.source_category
