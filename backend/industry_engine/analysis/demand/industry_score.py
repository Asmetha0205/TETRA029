"""
Industry Score Calculator for the Demand & Trend Intelligence Engine.

Calculates the Industry Intelligence Score (0-100) for each technology
by combining multiple weighted components:
- Demand component
- Growth component
- Role importance component
- Category importance component
- Technology popularity component
"""

import logging
from typing import Any, Dict, List, Optional

from backend.industry_engine.analysis.demand.config import DemandConfig
from backend.industry_engine.analysis.demand.models import (
    DemandScore,
    IndustryScore,
    TechnologyClassification,
    TrendMetrics,
)

logger = logging.getLogger("industry_engine.analysis.demand.industry_score")


class IndustryScoreCalculator:
    """
    Calculates Industry Intelligence Scores for technologies.
    
    Combines demand, growth, role importance, category importance,
    and popularity into a single comprehensive score.
    """

    def __init__(self, config: Optional[DemandConfig] = None) -> None:
        """
        Initialize the industry score calculator.
        
        Args:
            config: Optional DemandConfig for tuning weights.
        """
        self._config = config or DemandConfig()
        self._weights = self._config.industry_score_weights
        self._thresholds = self._config.classification_thresholds
        logger.info("[IndustryScoreCalculator] Initialized with weights: %s", self._weights)

    def calculate_scores(
        self,
        demand_scores: List[DemandScore],
        trend_metrics: List[TrendMetrics],
        total_technologies: int,
    ) -> List[IndustryScore]:
        """
        Calculate industry intelligence scores for all technologies.
        
        Args:
            demand_scores: List of DemandScore objects.
            trend_metrics: List of TrendMetrics objects.
            total_technologies: Total number of technologies in dataset.
        
        Returns:
            List of IndustryScore objects sorted by score (descending).
        """
        trend_map = {t.name: t for t in trend_metrics}

        scores = []
        for demand in demand_scores:
            trend = trend_map.get(demand.name)
            score = self._calculate_single_score(
                demand=demand,
                trend=trend,
                total_technologies=total_technologies,
            )
            scores.append(score)

        scores.sort(key=lambda s: s.industry_score, reverse=True)
        logger.info("[IndustryScoreCalculator] Calculated scores for %d technologies.", len(scores))
        return scores

    def _calculate_single_score(
        self,
        demand: DemandScore,
        trend: Optional[TrendMetrics],
        total_technologies: int,
    ) -> IndustryScore:
        """Calculate industry score for a single technology."""
        weights = self._weights

        demand_component = self._calculate_demand_component(demand)
        growth_component = self._calculate_growth_component(trend)
        role_component = self._calculate_role_component(demand)
        category_component = self._calculate_category_component(demand)
        popularity_component = self._calculate_popularity_component(
            demand, total_technologies
        )

        industry_score = (
            weights.demand * demand_component +
            weights.growth * growth_component +
            weights.role_importance * role_component +
            weights.category_importance * category_component +
            weights.popularity * popularity_component
        )

        industry_score = round(min(max(industry_score, 0.0), 100.0), 2)
        classification = self._classify_technology(
            industry_score, demand, trend
        )

        return IndustryScore(
            name=demand.name,
            industry_score=industry_score,
            demand_component=round(demand_component, 2),
            growth_component=round(growth_component, 2),
            role_component=round(role_component, 2),
            category_component=round(category_component, 2),
            popularity_component=round(popularity_component, 2),
            classification=classification,
        )

    def _calculate_demand_component(self, demand: DemandScore) -> float:
        """Calculate demand component from demand score."""
        return demand.demand_score

    def _calculate_growth_component(self, trend: Optional[TrendMetrics]) -> float:
        """Calculate growth component from trend metrics."""
        if not trend:
            return 50.0

        growth = trend.growth_rate
        momentum = trend.momentum

        if growth >= 100:
            base = 100.0
        elif growth >= 50:
            base = 80 + (growth - 50) * 0.4
        elif growth >= 10:
            base = 50 + (growth - 10) * 0.75
        elif growth >= 0:
            base = 40 + growth
        elif growth >= -30:
            base = 20 + (growth + 30) * 0.67
        else:
            base = max(0, 20 + growth * 0.3)

        if momentum > 0:
            base = min(base + momentum * 0.5, 100.0)
        elif momentum < 0:
            base = max(base + momentum * 0.3, 0.0)

        return base

    def _calculate_role_component(self, demand: DemandScore) -> float:
        """Calculate role importance component."""
        return demand.role_score

    def _calculate_category_component(self, demand: DemandScore) -> float:
        """Calculate category importance component."""
        return demand.category_score

    def _calculate_popularity_component(
        self, demand: DemandScore, total_technologies: int
    ) -> float:
        """Calculate popularity component based on relative position."""
        if total_technologies == 0:
            return 50.0

        rank_ratio = 1.0 - (demand.rank_score / 100.0)
        return rank_ratio * 100

    def _classify_technology(
        self,
        industry_score: float,
        demand: DemandScore,
        trend: Optional[TrendMetrics],
    ) -> TechnologyClassification:
        """Classify technology based on score and metrics."""
        t = self._thresholds
        mentions = demand.frequency_score

        if trend and trend.trend.value == "Deprecated":
            return TechnologyClassification.LEGACY

        if trend and trend.trend.value == "Legacy":
            return TechnologyClassification.LEGACY

        if trend and trend.trend.value == "Emerging":
            if industry_score < t.emerging_min_score:
                return TechnologyClassification.EXPERIMENTAL
            return TechnologyClassification.EMERGING

        if industry_score >= t.core_min_score:
            return TechnologyClassification.CORE
        elif industry_score >= t.supporting_min_score:
            return TechnologyClassification.SUPPORTING
        elif industry_score >= t.emerging_min_score:
            return TechnologyClassification.EMERGING
        elif industry_score >= t.experimental_min_score:
            return TechnologyClassification.EXPERIMENTAL
        else:
            return TechnologyClassification.LEGACY

    def get_classification_summary(
        self, scores: List[IndustryScore]
    ) -> Dict[str, List[str]]:
        """Group technologies by their classification."""
        summary: Dict[str, List[str]] = {
            classification.value: [] for classification in TechnologyClassification
        }
        for score in scores:
            summary[score.classification.value].append(score.name)
        return summary

    def get_core_technologies(
        self, scores: List[IndustryScore]
    ) -> List[IndustryScore]:
        """Get technologies classified as Core."""
        return [s for s in scores if s.classification == TechnologyClassification.CORE]

    def get_emerging_technologies(
        self, scores: List[IndustryScore]
    ) -> List[IndustryScore]:
        """Get technologies classified as Emerging."""
        return [s for s in scores if s.classification == TechnologyClassification.EMERGING]

    def get_score_distribution(
        self, scores: List[IndustryScore]
    ) -> Dict[str, int]:
        """Get distribution of industry scores across ranges."""
        distribution = {
            "elite (90-100)": 0,
            "strong (70-89)": 0,
            "moderate (50-69)": 0,
            "developing (30-49)": 0,
            "nascent (0-29)": 0,
        }

        for score in scores:
            s = score.industry_score
            if s >= 90:
                distribution["elite (90-100)"] += 1
            elif s >= 70:
                distribution["strong (70-89)"] += 1
            elif s >= 50:
                distribution["moderate (50-69)"] += 1
            elif s >= 30:
                distribution["developing (30-49)"] += 1
            else:
                distribution["nascent (0-29)"] += 1

        return distribution
