"""
Evidence Ranking & Relevance Engine.
Ranks retrieved evidence items based on industry score, demand score,
trend velocity, and job frequency.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class RankedEvidence(BaseModel):
    """Container for ranked gap evidence item."""
    technology: str
    category: str = "General"
    industry_demand_score: float = 0.0
    industry_score: float = 0.0
    trend: str = "Stable"
    frequency: int = 0
    rank_score: float = 0.0
    related_roles: List[str] = Field(default_factory=list)
    related_technologies: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)


class EvidenceRanker:
    """
    Ranks evidence items by calculating a weighted priority score.
    Weights: Industry Score (40%), Demand Score (30%), Frequency (20%), Trend (10%).
    """

    TREND_WEIGHTS = {
        "Rapidly Growing": 1.2,
        "Rising": 1.1,
        "Stable": 1.0,
        "Declining": 0.7,
    }

    @classmethod
    def rank_evidence(cls, evidence_list: List[Dict[str, Any]]) -> List[RankedEvidence]:
        """Rank list of raw evidence items."""
        ranked_items: List[RankedEvidence] = []

        for item in evidence_list:
            tech_name = item.get("tech_name", item.get("technology", "Unknown"))
            demand = float(item.get("demand_score", 80.0))
            ind_score = float(item.get("industry_score", 85.0))
            freq = int(item.get("frequency", 40))
            trend_str = str(item.get("trend", "Rising"))

            trend_mult = cls.TREND_WEIGHTS.get(trend_str, 1.0)
            norm_freq = min(freq / 100.0, 1.0) * 100.0

            composite_score = (
                (ind_score * 0.4) +
                (demand * 0.3) +
                (norm_freq * 0.2)
            ) * trend_mult

            ranked_items.append(
                RankedEvidence(
                    technology=tech_name,
                    category=item.get("category", "General"),
                    industry_demand_score=demand,
                    industry_score=ind_score,
                    trend=trend_str,
                    frequency=freq,
                    rank_score=round(composite_score, 2),
                    related_roles=item.get("related_roles", []),
                    related_technologies=item.get("related_technologies", []),
                    prerequisites=item.get("prerequisites", [])
                )
            )

        # Sort descending by rank score
        ranked_items.sort(key=lambda x: x.rank_score, reverse=True)
        return ranked_items
