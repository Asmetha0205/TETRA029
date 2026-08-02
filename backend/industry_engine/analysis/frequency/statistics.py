"""
Statistics for the CurricuAlign AI Technology Frequency Analysis Engine.

Computes derived metrics: top-N lists, technology diversity, average
technologies per job, and most common co-occurring technology pairs.
"""

import logging
from collections import Counter
from typing import Dict, List, Optional

from backend.industry_engine.analysis.frequency.config import FrequencyConfig
from backend.industry_engine.analysis.frequency.models import (
    CategoryFrequency,
    FrequencyStatistics,
    TechnologyFrequency,
)

logger = logging.getLogger("industry_engine.analysis.frequency.statistics")


class StatisticsGenerator:
    """
    Computes statistical metrics from frequency and category counters.
    """

    def __init__(self, config: Optional[FrequencyConfig] = None) -> None:
        self._config = config or FrequencyConfig()

    def compute(
        self,
        technology_frequencies: List[TechnologyFrequency],
        category_frequencies: List[CategoryFrequency],
        total_jobs: int,
        optional_records: Optional[List] = None,
    ) -> FrequencyStatistics:
        """
        Generate statistics from aggregated frequencies.
        """
        top_techs = sorted(
            technology_frequencies,
            key=lambda t: t.mentions,
            reverse=True,
        )[: self._config.top_n_limit]

        top_per_category: Dict[str, List[TechnologyFrequency]] = {}
        for freq in technology_frequencies:
            cat = freq.category
            if cat not in top_per_category:
                top_per_category[cat] = []
            top_per_category[cat].append(freq)

        for cat in top_per_category:
            top_per_category[cat] = sorted(
                top_per_category[cat],
                key=lambda t: t.mentions,
                reverse=True,
            )[: self._config.top_n_per_category]

        unique_techs = len(technology_frequencies)
        total_mentions = sum(t.mentions for t in technology_frequencies)
        average_per_job = round(total_mentions / max(total_jobs, 1), 2)
        diversity = round(unique_techs / max(total_mentions, 1), 4)

        combinations = []
        if self._config.compute_combination_statistics and optional_records:
            combinations = self._most_common_pairs(optional_records)

        return FrequencyStatistics(
            top_technologies=top_techs,
            top_per_category=top_per_category,
            total_unique_technologies=unique_techs,
            average_technologies_per_job=average_per_job,
            technology_diversity_score=diversity,
            most_common_combinations=combinations,
        )

    def _most_common_pairs(self, records: List) -> List[List[str]]:
        """
        Compute most common technology pairs from a subset of records.
        Each record should have a `technologies` dict of category -> list.
        """
        max_records = min(len(records), self._config.combination_max_jobs)
        pair_counter: Counter = Counter()
        for record in records[:max_records]:
            techs = []
            for tech_list in record.technologies.values():
                techs.extend(tech_list)
            techs = list(set(techs))[: self._config.combination_max_technologies]
            for i in range(len(techs)):
                for j in range(i + 1, len(techs)):
                    pair = tuple(sorted([techs[i], techs[j]]))
                    pair_counter[pair] += 1

        top_pairs = pair_counter.most_common(self._config.top_n_limit)
        return [list(pair) for pair, _ in top_pairs]