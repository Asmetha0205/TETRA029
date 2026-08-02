"""
Technology Ranker for the Demand & Trend Intelligence Engine.

Generates multiple rankings for technologies:
- Overall ranking
- Category ranking
- Role ranking
- Growth ranking
- Emerging technology ranking
"""

import logging
from typing import Any, Dict, List, Optional

from backend.industry_engine.analysis.demand.config import DemandConfig
from backend.industry_engine.analysis.demand.models import (
    DemandScore,
    TechnologyIntelligence,
    TechnologyRanking,
    TrendMetrics,
)

logger = logging.getLogger("industry_engine.analysis.demand.technology_ranker")


class TechnologyRanker:
    """
    Generates multiple technology rankings based on different criteria.
    
    Provides overall, category, role, growth, and emerging technology rankings.
    """

    def __init__(self, config: Optional[DemandConfig] = None) -> None:
        """
        Initialize the technology ranker.
        
        Args:
            config: Optional DemandConfig for tuning.
        """
        self._config = config or DemandConfig()
        logger.info("[TechnologyRanker] Initialized.")

    def generate_rankings(
        self,
        technologies: List[TechnologyIntelligence],
        demand_scores: List[DemandScore],
        trend_metrics: List[TrendMetrics],
    ) -> List[TechnologyRanking]:
        """
        Generate comprehensive rankings for all technologies.
        
        Args:
            technologies: List of TechnologyIntelligence objects.
            demand_scores: List of DemandScore objects.
            trend_metrics: List of TrendMetrics objects.
        
        Returns:
            List of TechnologyRanking objects.
        """
        overall_map = self._create_overall_ranking(technologies)
        growth_map = self._create_growth_ranking(trend_metrics)
        emerging_map = self._create_emerging_ranking(trend_metrics)
        category_map = self._create_category_ranking(technologies)
        role_map = self._create_role_ranking(technologies)

        rankings = []
        for tech in technologies:
            ranking = TechnologyRanking(
                name=tech.name,
                overall_rank=overall_map.get(tech.name, 0),
                category_rank=category_map.get(tech.name, 0),
                role_rank=role_map.get(tech.name, 0),
                growth_rank=growth_map.get(tech.name, 0),
                emerging_rank=emerging_map.get(tech.name, 0),
            )
            rankings.append(ranking)

        logger.info("[TechnologyRanker] Generated rankings for %d technologies.", len(rankings))
        return rankings

    def _create_overall_ranking(
        self, technologies: List[TechnologyIntelligence]
    ) -> Dict[str, int]:
        """Create overall ranking based on industry score."""
        sorted_techs = sorted(
            technologies,
            key=lambda t: t.industry_score,
            reverse=True,
        )
        return {tech.name: i + 1 for i, tech in enumerate(sorted_techs)}

    def _create_growth_ranking(
        self, trend_metrics: List[TrendMetrics]
    ) -> Dict[str, int]:
        """Create ranking based on growth rate."""
        sorted_metrics = sorted(
            trend_metrics,
            key=lambda m: m.growth_rate,
            reverse=True,
        )
        return {m.name: i + 1 for i, m in enumerate(sorted_metrics)}

    def _create_emerging_ranking(
        self, trend_metrics: List[TrendMetrics]
    ) -> Dict[str, int]:
        """Create ranking for emerging technologies only."""
        emerging = [
            m for m in trend_metrics
            if m.trend.value in ("Emerging", "Rapidly Rising")
        ]
        sorted_emerging = sorted(
            emerging,
            key=lambda m: m.growth_rate,
            reverse=True,
        )
        return {m.name: i + 1 for i, m in enumerate(sorted_emerging)}

    def _create_category_ranking(
        self, technologies: List[TechnologyIntelligence]
    ) -> Dict[str, int]:
        """Create ranking within each category."""
        category_map: Dict[str, List[TechnologyIntelligence]] = {}
        for tech in technologies:
            category = self._get_tech_category(tech)
            if category not in category_map:
                category_map[category] = []
            category_map[category].append(tech)

        rank_map: Dict[str, int] = {}
        for category, techs in category_map.items():
            sorted_techs = sorted(
                techs,
                key=lambda t: t.demand_score,
                reverse=True,
            )
            for i, tech in enumerate(sorted_techs):
                rank_map[tech.name] = i + 1

        return rank_map

    def _create_role_ranking(
        self, technologies: List[TechnologyIntelligence]
    ) -> Dict[str, int]:
        """Create ranking based on role importance."""
        rank_map: Dict[str, int] = {}
        sorted_techs = sorted(
            technologies,
            key=lambda t: t.demand_score,
            reverse=True,
        )
        for i, tech in enumerate(sorted_techs):
            rank_map[tech.name] = i + 1

        return rank_map

    def _get_tech_category(self, tech: TechnologyIntelligence) -> str:
        """Get category for a technology (placeholder - would come from metadata)."""
        return "General"

    def get_top_overall(
        self, rankings: List[TechnologyRanking], top_n: int = 10
    ) -> List[TechnologyRanking]:
        """Get top N technologies by overall rank."""
        sorted_rankings = sorted(
            rankings,
            key=lambda r: r.overall_rank,
        )
        return sorted_rankings[:top_n]

    def get_top_by_growth(
        self, rankings: List[TechnologyRanking], top_n: int = 10
    ) -> List[TechnologyRanking]:
        """Get top N technologies by growth rank."""
        sorted_rankings = sorted(
            rankings,
            key=lambda r: r.growth_rank,
        )
        return sorted_rankings[:top_n]

    def get_top_emerging(
        self, rankings: List[TechnologyRanking], top_n: int = 10
    ) -> List[TechnologyRanking]:
        """Get top N emerging technologies."""
        sorted_rankings = sorted(
            rankings,
            key=lambda r: r.emerging_rank if r.emerging_rank > 0 else float('inf'),
        )
        return [r for r in sorted_rankings if r.emerging_rank > 0][:top_n]

    def get_ranking_summary(
        self, rankings: List[TechnologyRanking]
    ) -> Dict[str, Any]:
        """Get summary statistics for rankings."""
        if not rankings:
            return {}

        overall_ranks = [r.overall_rank for r in rankings if r.overall_rank > 0]
        growth_ranks = [r.growth_rank for r in rankings if r.growth_rank > 0]
        emerging_count = sum(1 for r in rankings if r.emerging_rank > 0)

        return {
            "total_technologies": len(rankings),
            "avg_overall_rank": sum(overall_ranks) / len(overall_ranks) if overall_ranks else 0,
            "avg_growth_rank": sum(growth_ranks) / len(growth_ranks) if growth_ranks else 0,
            "emerging_count": emerging_count,
        }
