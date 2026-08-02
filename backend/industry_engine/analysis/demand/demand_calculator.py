"""
Demand Calculator for the Demand & Trend Intelligence Engine.

Calculates demand scores for technologies based on multiple weighted factors:
- Job frequency
- Unique job coverage
- Category importance
- Role importance
- Technology rank
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from backend.industry_engine.analysis.demand.config import DemandConfig
from backend.industry_engine.analysis.demand.exceptions import (
    ConfigurationError,
    EmptyDatasetError,
    InvalidInputError,
    WeightSumError,
)
from backend.industry_engine.analysis.demand.models import (
    DemandScore,
    TechnologyFrequencyInput,
)

logger = logging.getLogger("industry_engine.analysis.demand.demand_calculator")


class DemandCalculator:
    """
    Calculates demand scores for technologies based on weighted factors.
    
    The demand score (0-100) represents how much demand exists for a technology
    in the current job market.
    """

    def __init__(self, config: Optional[DemandConfig] = None) -> None:
        """
        Initialize the demand calculator.
        
        Args:
            config: Optional DemandConfig for tuning weights and thresholds.
        
        Raises:
            WeightSumError: If configured weights do not sum to approximately 1.0.
        """
        self._config = config or DemandConfig()
        if not self._config.demand_weights.validate_weights_sum():
            raise WeightSumError("Demand weights must sum to approximately 1.0.")
        logger.info("[DemandCalculator] Initialized with demand weights: %s", self._config.demand_weights)

    def calculate_scores(
        self,
        technologies: Dict[str, TechnologyFrequencyInput],
        total_jobs: int,
        category_metadata: Optional[Dict[str, Any]] = None,
        role_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[DemandScore]:
        """
        Calculate demand scores for all technologies.
        
        Args:
            technologies: Dictionary mapping technology names to their frequency data.
            total_jobs: Total number of jobs in the dataset.
            category_metadata: Optional metadata about technology categories.
            role_metadata: Optional metadata about job roles.
        
        Returns:
            List of DemandScore objects sorted by demand score (descending).
        
        Raises:
            EmptyDatasetError: If technologies dictionary is empty.
            InvalidInputError: If total_jobs is zero or negative.
        """
        if not technologies:
            raise EmptyDatasetError("Cannot calculate demand scores for empty dataset.")
        if total_jobs <= 0:
            raise InvalidInputError(f"Total jobs must be positive, got {total_jobs}.")

        scores = []
        for name, freq in technologies.items():
            score = self._calculate_single_score(
                name=name,
                freq=freq,
                total_jobs=total_jobs,
                all_technologies=technologies,
                category_metadata=category_metadata or {},
                role_metadata=role_metadata or {},
            )
            scores.append(score)

        scores.sort(key=lambda s: s.demand_score, reverse=True)
        logger.info("[DemandCalculator] Calculated demand scores for %d technologies.", len(scores))
        return scores

    def _calculate_single_score(
        self,
        name: str,
        freq: TechnologyFrequencyInput,
        total_jobs: int,
        all_technologies: Dict[str, TechnologyFrequencyInput],
        category_metadata: Dict[str, Any],
        role_metadata: Dict[str, Any],
    ) -> DemandScore:
        """Calculate demand score for a single technology."""
        weights = self._config.demand_weights

        frequency_score = self._calculate_frequency_score(freq, total_jobs)
        coverage_score = self._calculate_coverage_score(freq, total_jobs)
        category_score = self._calculate_category_score(name, category_metadata)
        role_score = self._calculate_role_score(name, role_metadata)
        rank_score = self._calculate_rank_score(freq, len(all_technologies))

        demand_score = (
            weights.frequency * frequency_score +
            weights.coverage * coverage_score +
            weights.category_importance * category_score +
            weights.role_importance * role_score +
            weights.rank_position * rank_score
        )

        demand_score = round(min(max(demand_score, 0.0), 100.0), 2)

        return DemandScore(
            name=name,
            demand_score=demand_score,
            frequency_score=round(frequency_score, 2),
            coverage_score=round(coverage_score, 2),
            category_score=round(category_score, 2),
            role_score=round(role_score, 2),
            rank_score=round(rank_score, 2),
        )

    def _calculate_frequency_score(
        self, freq: TechnologyFrequencyInput, total_jobs: int
    ) -> float:
        """
        Calculate score based on how frequently the technology appears.
        
        Uses a logarithmic scale to normalize the frequency distribution.
        """
        if total_jobs == 0:
            return 0.0

        percentage = freq.percentage
        if percentage >= 80:
            return 100.0
        elif percentage >= 50:
            return 80 + (percentage - 50) * 0.67
        elif percentage >= 20:
            return 40 + (percentage - 20) * 1.33
        elif percentage >= 5:
            return 10 + (percentage - 5) * 2.0
        else:
            return percentage * 2.0

    def _calculate_coverage_score(
        self, freq: TechnologyFrequencyInput, total_jobs: int
    ) -> float:
        """
        Calculate score based on unique job coverage.
        
        Considers both the percentage and the absolute number of jobs.
        """
        if total_jobs == 0:
            return 0.0

        percentage = freq.percentage
        coverage_factor = min(1.0, freq.mentions / max(total_jobs * 0.1, 1))

        score = (percentage * 0.7) + (coverage_factor * 30)
        return min(score, 100.0)

    def _calculate_category_score(
        self, name: str, category_metadata: Dict[str, Any]
    ) -> float:
        """Calculate score based on the importance of the technology's category."""
        category = category_metadata.get(name, {}).get("category", "Unknown")
        return self._config.category_importance.get_score(category) * 100

    def _calculate_role_score(
        self, name: str, role_metadata: Dict[str, Any]
    ) -> float:
        """Calculate score based on how important the technology is across roles."""
        if not role_metadata:
            return 50.0

        max_role_score = 0.0
        for role_name, role_data in role_metadata.items():
            techs_in_role = role_data.get("top_technologies", [])
            for tech in techs_in_role:
                if tech.get("technology") == name:
                    role_importance = self._config.role_importance.get_score(role_name)
                    max_role_score = max(max_role_score, role_importance * 100)

        return max_role_score if max_role_score > 0 else 50.0

    def _calculate_rank_score(
        self, freq: TechnologyFrequencyInput, total_technologies: int
    ) -> float:
        """
        Calculate score based on the technology's rank position.
        
        Higher rank (lower number) gives a higher score.
        """
        if total_technologies == 0:
            return 0.0

        rank_ratio = 1.0 - (freq.rank - 1) / max(total_technologies - 1, 1)
        return max(0.0, min(rank_ratio * 100, 100.0))

    def get_top_demanded(
        self,
        scores: List[DemandScore],
        top_n: int = 10,
    ) -> List[DemandScore]:
        """Get the top N most demanded technologies."""
        return scores[:top_n]

    def get_demand_distribution(
        self, scores: List[DemandScore]
    ) -> Dict[str, int]:
        """Get distribution of demand scores across ranges."""
        distribution = {
            "critical (90-100)": 0,
            "high (70-89)": 0,
            "moderate (50-69)": 0,
            "low (30-49)": 0,
            "minimal (0-29)": 0,
        }

        for score in scores:
            s = score.demand_score
            if s >= 90:
                distribution["critical (90-100)"] += 1
            elif s >= 70:
                distribution["high (70-89)"] += 1
            elif s >= 50:
                distribution["moderate (50-69)"] += 1
            elif s >= 30:
                distribution["low (30-49)"] += 1
            else:
                distribution["minimal (0-29)"] += 1

        return distribution
