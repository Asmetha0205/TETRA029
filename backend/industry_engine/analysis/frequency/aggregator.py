"""
Aggregator for the CurricuAlign AI Technology Frequency Analysis Engine.

Central aggregation layer that dispatches job records to the frequency,
category, and role counters and assembles the merged result set.
"""

import logging
from typing import Dict, List, Optional, Tuple

from backend.industry_engine.analysis.frequency.category_counter import CategoryCounter
from backend.industry_engine.analysis.frequency.config import FrequencyConfig
from backend.industry_engine.analysis.frequency.exceptions import EmptyDatasetError
from backend.industry_engine.analysis.frequency.frequency_counter import FrequencyCounter
from backend.industry_engine.analysis.frequency.models import (
    CategoryFrequency,
    JobTechnologyRecord,
    RoleFrequency,
    RoleTechnology,
    TechnologyFrequency,
)
from backend.industry_engine.analysis.frequency.role_counter import RoleCounter

logger = logging.getLogger("industry_engine.analysis.frequency.aggregator")


class Aggregator:
    """
    Dispatches job records to internal counters and produces merged results.
    Supports batch processing and cumulative state for incremental updates.
    """

    def __init__(self, config: Optional[FrequencyConfig] = None) -> None:
        self._config = config or FrequencyConfig()
        self._frequency_counter = FrequencyCounter()
        self._category_counter = CategoryCounter()
        self._role_counter = RoleCounter()
        self._raw_records: List[JobTechnologyRecord] = []

    def process_batch(self, records: List[JobTechnologyRecord]) -> None:
        """
        Process a batch of JobTechnologyRecords through all counters.
        """
        if not records:
            raise EmptyDatasetError("Cannot process an empty batch of job records.")

        self._frequency_counter.process_batch(records)

        for record in records:
            job_id = record.job_id
            for category, tech_names in record.technologies.items():
                for tech_name in tech_names:
                    self._category_counter.record(
                        category_key=category,
                        tech_name=tech_name,
                        job_id=job_id,
                    )
            role = record.role or record.metadata.get(self._config.role_field, "")
            self._role_counter.record(
                role=role,
                tech_names=[
                    tech
                    for tech_list in record.technologies.values()
                    for tech in tech_list
                ],
                job_id=job_id,
            )
            self._raw_records.append(record)

        logger.info(
            f"[Aggregator] Processed {len(records)} records. Total: {self._frequency_counter.get_total_jobs()} unique jobs."
        )

    def get_technology_frequencies(self) -> List[TechnologyFrequency]:
        """
        Return per-technology frequencies sorted by mentions.
        """
        return self._frequency_counter.get_technology_frequencies(
            min_mentions=self._config.min_mentions_threshold,
        )

    def get_category_frequencies(self) -> List[CategoryFrequency]:
        """
        Return per-category frequencies sorted by mentions.
        """
        summary = self._category_counter.build_summary()
        return [
            CategoryFrequency(
                category=s["category"],
                mentions=s["mentions"],
                unique_technologies=s["unique_technologies"],
                unique_jobs=s["unique_jobs"],
            )
            for s in summary
        ]

    def get_role_frequencies(self) -> List[RoleFrequency]:
        """
        Return per-role distributions.
        """
        roles_data = self._role_counter.build_all_roles(
            top_n=self._config.top_n_per_category
        )
        return [
            RoleFrequency(
                role=r["role"],
                job_count=r["job_count"],
                top_technologies=[
                    RoleTechnology(technology=t["technology"], percentage=t["percentage"])
                    for t in r["top_technologies"]
                ],
            )
            for r in roles_data
        ]

    def get_raw_records(self) -> List[JobTechnologyRecord]:
        """
        Return the accumulated raw records (for statistics computation).
        """
        return list(self._raw_records)

    def get_total_jobs(self) -> int:
        return self._frequency_counter.get_total_jobs()

    def process(self) -> Tuple[
        List[TechnologyFrequency],
        List[CategoryFrequency],
        List[RoleFrequency],
        int,
        List[JobTechnologyRecord],
    ]:
        """
        Execute the full aggregation pipeline and return intermediate results.
        """
        tech_freqs = self.get_technology_frequencies()
        cat_freqs = self.get_category_frequencies()
        role_freqs = self.get_role_frequencies() if self._config.compute_role_statistics else []
        total = self.get_total_jobs()
        records = self.get_raw_records()
        return tech_freqs, cat_freqs, role_freqs, total, records

    def reset(self) -> None:
        """
        Reset all internal counters so the aggregator can be reused.
        """
        self._frequency_counter.reset()
        self._category_counter.reset()
        self._role_counter.reset()
        self._raw_records.clear()
        logger.debug("[Aggregator] All counters reset.")