"""
Category Counter for the CurricuAlign AI Technology Frequency Analysis Engine.

Aggregates technology mentions by their canonical category, computing
total mentions, unique technology count, and unique job reach per category.
"""

import logging
from collections import defaultdict
from typing import Dict, List, Set

from backend.industry_engine.processing.normalization.models import CATEGORY_DISPLAY

logger = logging.getLogger("industry_engine.analysis.frequency.category_counter")


class CategoryCounter:
    """Accumulates per-category technology frequency metrics."""

    def __init__(self) -> None:
        self._mentions: Dict[str, int] = defaultdict(int)
        self._tech_per_category: Dict[str, Set[str]] = defaultdict(set)
        self._jobs_per_category: Dict[str, Set[str]] = defaultdict(set)
        self._all_job_ids: Set[str] = set()

    def record(
        self,
        category_key: str,
        tech_name: str,
        job_id: str,
    ) -> None:
        """Record a single technology mention within a job."""
        category = CATEGORY_DISPLAY.get(category_key, category_key)
        self._mentions[category] = self._mentions.get(category, 0) + 1
        self._tech_per_category[category].add(tech_name)
        self._jobs_per_category[category].add(job_id)
        self._all_job_ids.add(job_id)

    def process_batch(
        self,
        records: List[Dict],
    ) -> None:
        """
        Process a batch of {job_id, category, tech_name} entries.
        """
        for record in records:
            self.record(
                category_key=record["category"],
                tech_name=record["tech_name"],
                job_id=record["job_id"],
            )

    def process_from_frequency_entries(
        self,
        frequencies: List,
    ) -> None:
        """
        Accept pre-computed frequency entries to backfill category totals.
        frequencies are TechnologyFrequency objects.
        """
        for freq in frequencies:
            category = freq.category
            self._mentions[category] = self._mentions.get(category, 0) + freq.mentions
            self._tech_per_category[category].add(freq.name)

    def build_summary(self) -> List[Dict]:
        """
        Return a summary dict per category sorted by mentions descending.
        """
        total_jobs = max(len(self._all_job_ids), 1)
        summary = []
        for category in sorted(self._mentions, key=lambda c: self._mentions[c], reverse=True):
            summary.append({
                "category": category,
                "mentions": self._mentions[category],
                "unique_technologies": len(self._tech_per_category.get(category, set())),
                "unique_jobs": len(self._jobs_per_category.get(category, set())),
            })
        return summary

    def to_dict(self) -> Dict[str, Dict[str, int]]:
        """Return raw category-frequency map."""
        return {
            category: {
                "mentions": self._mentions.get(category, 0),
                "unique_technologies": len(self._tech_per_category.get(category, set())),
                "unique_jobs": len(self._jobs_per_category.get(category, set())),
            }
            for category in self._mentions
        }

    def reset(self) -> None:
        """Clear all accumulated category counters."""
        self._mentions.clear()
        self._tech_per_category.clear()
        self._jobs_per_category.clear()
        self._all_job_ids.clear()

    @property
    def total_categories(self) -> int:
        return len(self._mentions)