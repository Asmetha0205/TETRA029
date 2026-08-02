"""
Frequency Counter for the CurricuAlign AI Technology Frequency Analysis Engine.

Counts per-technology occurrences and unique job reach across a dataset of
normalized job technology records. Produces TechnologyFrequency models with
percentage and rank.
"""

import logging
from collections import defaultdict
from typing import Dict, List, Optional, Union

from backend.industry_engine.analysis.frequency.exceptions import InvalidTechnologyError
from backend.industry_engine.analysis.frequency.models import (
    JobTechnologyRecord,
    TechnologyFrequency,
)
from backend.industry_engine.processing.normalization.models import (
    CATEGORY_DISPLAY,
    NormalizedTechnology,
)

logger = logging.getLogger("industry_engine.analysis.frequency.frequency_counter")


class FrequencyCounter:
    """
    Accumulates per-technology frequency counts across job records.
    Supports incremental ingestion and resets for batch processing.
    """

    def __init__(self) -> None:
        self._mentions: Dict[str, int] = defaultdict(int)
        self._unique_jobs_per_tech: Dict[str, set] = defaultdict(set)
        self._tech_to_category: Dict[str, str] = {}
        self._total_jobs: int = 0
        self._all_job_ids: set = set()

    def process_batch(self, records: List[JobTechnologyRecord]) -> int:
        """
        Process a batch of job technology records, updating internal counters.

        Returns the number of records processed.
        """
        for record in records:
            self._process_single(record)
        return len(records)

    def _process_single(self, record: JobTechnologyRecord) -> None:
        job_id = record.job_id
        if not job_id or not job_id.strip():
            raise InvalidTechnologyError("JobTechnologyRecord is missing a job_id.")
        self._all_job_ids.add(job_id)
        self._total_jobs = len(self._all_job_ids)

        for category, tech_names in record.technologies.items():
            display_category = CATEGORY_DISPLAY.get(category, category)
            for tech_name in tech_names:
                if not tech_name or not tech_name.strip():
                    continue
                key = tech_name.strip()
                display_category = CATEGORY_DISPLAY.get(category, category)
                self._mentions[key] = self._mentions.get(key, 0) + 1
                if key not in self._unique_jobs_per_tech:
                    self._unique_jobs_per_tech[key] = set()
                self._unique_jobs_per_tech[key].add(job_id)
                self._tech_to_category[key] = display_category

    def get_technology_frequencies(
        self,
        min_mentions: int = 0,
        sort_descending: bool = True,
    ) -> List[TechnologyFrequency]:
        """
        Return aggregated frequencies, optionally filtered and sorted.
        """
        results = []
        total_jobs = max(self._total_jobs, 1)
        for tech_name, mention_count in self._mentions.items():
            if mention_count < min_mentions:
                continue
            unique_job_count = len(self._unique_jobs_per_tech.get(tech_name, set()))
            percentage = round((unique_job_count / total_jobs) * 100.0, 2)
            results.append(
                TechnologyFrequency(
                    name=tech_name,
                    category=self._tech_to_category.get(tech_name, "Unknown"),
                    mentions=mention_count,
                    unique_jobs=unique_job_count,
                    percentage=percentage,
                    rank=0,
                )
            )
        results.sort(key=lambda f: f.mentions, reverse=sort_descending)
        for idx, freq in enumerate(results, start=1):
            freq.rank = idx
        return results

    def get_technology_count(self) -> int:
        """Return the number of distinct technologies tracked."""
        return len(self._mentions)

    def get_total_jobs(self) -> int:
        """Return the total number of distinct jobs processed."""
        return self._total_jobs

    def reset(self) -> None:
        """Clear all accumulated counters."""
        self._mentions.clear()
        self._unique_jobs_per_tech.clear()
        self._tech_to_category.clear()
        self._total_jobs = 0
        self._all_job_ids.clear()
        logger.debug("[FrequencyCounter] Reset all counters.")