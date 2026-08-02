"""
Data Models for the Demand & Trend Intelligence Engine.

Defines demand scores, trend analysis, industry intelligence scores,
technology classifications, and ranking models.
"""

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class TrendDirection(str, Enum):
    """Trend direction for technology adoption."""
    EMERGING = "Emerging"
    RAPIDLY_RISING = "Rapidly Rising"
    RISING = "Rising"
    STABLE = "Stable"
    DECLINING = "Declining"
    LEGACY = "Legacy"
    DEPRECATED = "Deprecated"


class TechnologyClassification(str, Enum):
    """Technology lifecycle classification."""
    CORE = "Core Technology"
    SUPPORTING = "Supporting Technology"
    EMERGING = "Emerging Technology"
    EXPERIMENTAL = "Experimental"
    LEGACY = "Legacy"


# =============================================================================
# Input Models
# =============================================================================

class TechnologyFrequencyInput(BaseModel):
    """Single technology frequency input from Phase 3.6."""
    mentions: int = Field(..., ge=0, description="Total mentions across all jobs.")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of jobs mentioning this tech.")
    rank: int = Field(..., ge=1, description="Frequency rank (1 = most frequent).")


class CategoryInput(BaseModel):
    """Category metadata for a technology."""
    mentions: int = Field(default=0, ge=0)
    unique_technologies: int = Field(default=0, ge=0)
    unique_jobs: int = Field(default=0, ge=0)


class RoleInput(BaseModel):
    """Role metadata for a technology."""
    job_count: int = Field(default=0, ge=0)
    top_technologies: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Snapshot Models
# =============================================================================

class SnapshotEntry(BaseModel):
    """A single technology entry in a historical snapshot."""
    name: str
    mentions: int = Field(default=0, ge=0)
    percentage: float = Field(default=0, ge=0, le=100)
    rank: int = Field(default=0, ge=0)


class TechnologySnapshot(BaseModel):
    """Historical snapshot of technology data at a point in time."""
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    total_jobs: int = Field(default=0, ge=0)
    technologies: Dict[str, SnapshotEntry] = Field(default_factory=dict)


class SnapshotHistory(BaseModel):
    """Collection of historical snapshots."""
    snapshots: List[TechnologySnapshot] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


# =============================================================================
# Demand Models
# =============================================================================

class DemandScore(BaseModel):
    """Computed demand metrics for a single technology."""
    name: str
    demand_score: float = Field(..., ge=0, le=100, description="Overall demand score 0-100.")
    frequency_score: float = Field(default=0, ge=0, le=100, description="Score from job frequency.")
    coverage_score: float = Field(default=0, ge=0, le=100, description="Score from unique job coverage.")
    category_score: float = Field(default=0, ge=0, le=100, description="Score from category importance.")
    role_score: float = Field(default=0, ge=0, le=100, description="Score from role importance.")
    rank_score: float = Field(default=0, ge=0, le=100, description="Score from technology rank.")


# =============================================================================
# Trend Models
# =============================================================================

class TrendMetrics(BaseModel):
    """Computed trend metrics for a single technology."""
    name: str
    trend: TrendDirection = Field(default=TrendDirection.STABLE)
    growth_rate: float = Field(default=0.0, description="Growth percentage.")
    decline_rate: float = Field(default=0.0, description="Decline percentage.")
    moving_average: float = Field(default=0.0, description="Moving average of mentions.")
    momentum: float = Field(default=0.0, description="Momentum score.")
    velocity: float = Field(default=0.0, description="Rate of change.")
    acceleration: float = Field(default=0.0, description="Acceleration of change.")
    volatility: float = Field(default=0.0, description="Volatility of mentions over time.")
    data_points: int = Field(default=0, description="Number of historical data points.")


# =============================================================================
# Industry Score Models
# =============================================================================

class IndustryScore(BaseModel):
    """Combined industry intelligence score for a single technology."""
    name: str
    industry_score: float = Field(..., ge=0, le=100, description="Overall industry intelligence score 0-100.")
    demand_component: float = Field(default=0, ge=0, le=100)
    growth_component: float = Field(default=0, ge=0, le=100)
    role_component: float = Field(default=0, ge=0, le=100)
    category_component: float = Field(default=0, ge=0, le=100)
    popularity_component: float = Field(default=0, ge=0, le=100)
    classification: TechnologyClassification = Field(default=TechnologyClassification.SUPPORTING)


# =============================================================================
# Ranking Models
# =============================================================================

class TechnologyRanking(BaseModel):
    """Ranking information for a single technology."""
    name: str
    overall_rank: int = Field(default=0, ge=0)
    category_rank: int = Field(default=0, ge=0)
    role_rank: int = Field(default=0, ge=0)
    growth_rank: int = Field(default=0, ge=0)
    emerging_rank: int = Field(default=0, ge=0)


# =============================================================================
# Technology Intelligence Models
# =============================================================================

class TechnologyIntelligence(BaseModel):
    """Complete intelligence data for a single technology."""
    name: str
    demand_score: float = Field(default=0, ge=0, le=100)
    trend: TrendDirection = Field(default=TrendDirection.STABLE)
    growth: float = Field(default=0.0, description="Growth percentage.")
    industry_score: float = Field(default=0, ge=0, le=100)
    classification: TechnologyClassification = Field(default=TechnologyClassification.SUPPORTING)
    mentions: int = Field(default=0, ge=0)
    percentage: float = Field(default=0, ge=0, le=100)
    rank: int = Field(default=0, ge=0)


# =============================================================================
# Report Models
# =============================================================================

class DemandReport(BaseModel):
    """Report containing all demand-related intelligence."""
    technologies: List[TechnologyIntelligence] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    generated_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


class TrendReport(BaseModel):
    """Report containing all trend-related intelligence."""
    technologies: List[TrendMetrics] = Field(default_factory=list)
    emerging_technologies: List[str] = Field(default_factory=list)
    declining_technologies: List[str] = Field(default_factory=list)
    stable_technologies: List[str] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    generated_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


class IndustryReport(BaseModel):
    """Complete industry intelligence report."""
    technologies: List[TechnologyIntelligence] = Field(default_factory=list)
    rankings: List[TechnologyRanking] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    category_rankings: Dict[str, List[str]] = Field(default_factory=dict)
    role_rankings: Dict[str, List[str]] = Field(default_factory=dict)
    growth_rankings: List[str] = Field(default_factory=list)
    emerging_rankings: List[str] = Field(default_factory=list)
    generated_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


# =============================================================================
# Visualization Data Models
# =============================================================================

class VisualizationData(BaseModel):
    """Pre-formatted data for various chart types."""
    line_chart: Dict[str, Any] = Field(default_factory=dict)
    bar_chart: Dict[str, Any] = Field(default_factory=dict)
    heatmap: Dict[str, Any] = Field(default_factory=dict)
    radar_chart: Dict[str, Any] = Field(default_factory=dict)
    trend_timeline: Dict[str, Any] = Field(default_factory=dict)
    bubble_chart: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Snapshot History Manager
# =============================================================================

class SnapshotManager:
    """Manages historical snapshots of technology data."""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize snapshot manager."""
        self._storage_path = storage_path
        self._history = SnapshotHistory()

    def create_snapshot(
        self,
        technologies: Dict[str, TechnologyFrequencyInput],
        total_jobs: int
    ) -> TechnologySnapshot:
        """Create a new snapshot from current data."""
        snapshot = TechnologySnapshot(total_jobs=total_jobs)
        for name, freq in technologies.items():
            snapshot.technologies[name] = SnapshotEntry(
                name=name,
                mentions=freq.mentions,
                percentage=freq.percentage,
                rank=freq.rank,
            )
        self._history.snapshots.append(snapshot)
        self._history.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return snapshot

    def get_latest_snapshot(self) -> Optional[TechnologySnapshot]:
        """Get the most recent snapshot."""
        if not self._history.snapshots:
            return None
        return self._history.snapshots[-1]

    def get_previous_snapshot(self) -> Optional[TechnologySnapshot]:
        """Get the second most recent snapshot."""
        if len(self._history.snapshots) < 2:
            return None
        return self._history.snapshots[-2]

    def get_all_snapshots(self) -> List[TechnologySnapshot]:
        """Get all historical snapshots."""
        return self._history.snapshots

    def get_history(self) -> SnapshotHistory:
        """Get the complete snapshot history."""
        return self._history

    def load_history(self, history: SnapshotHistory) -> None:
        """Load snapshot history from storage."""
        self._history = history

    def get_technology_history(self, tech_name: str) -> List[Dict[str, Any]]:
        """Get historical data for a specific technology."""
        history = []
        for snapshot in self._history.snapshots:
            if tech_name in snapshot.technologies:
                entry = snapshot.technologies[tech_name]
                history.append({
                    "timestamp": snapshot.timestamp,
                    "mentions": entry.mentions,
                    "percentage": entry.percentage,
                    "rank": entry.rank,
                })
        return history
