"""
Trend Calculator for the Demand & Trend Intelligence Engine.

Calculates trend metrics for technologies by comparing current data
with historical snapshots:
- Growth rate
- Decline rate
- Moving average
- Momentum
- Velocity and acceleration
- Volatility
- Trend direction classification
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from backend.industry_engine.analysis.demand.config import DemandConfig
from backend.industry_engine.analysis.demand.exceptions import (
    MissingHistoricalDataError,
    NegativeGrowthError,
)
from backend.industry_engine.analysis.demand.models import (
    SnapshotEntry,
    TechnologySnapshot,
    TrendDirection,
    TrendMetrics,
)

logger = logging.getLogger("industry_engine.analysis.demand.trend_calculator")


class TrendCalculator:
    """
    Calculates trend metrics for technologies based on historical data.
    
    Compares current snapshot with previous snapshots to determine
    growth patterns and trend directions.
    """

    def __init__(self, config: Optional[DemandConfig] = None) -> None:
        """
        Initialize the trend calculator.
        
        Args:
            config: Optional DemandConfig for tuning thresholds.
        """
        self._config = config or DemandConfig()
        self._thresholds = self._config.trend_thresholds
        logger.info("[TrendCalculator] Initialized with thresholds: %s", self._thresholds)

    def calculate_trends(
        self,
        current_snapshot: TechnologySnapshot,
        previous_snapshots: List[TechnologySnapshot],
    ) -> List[TrendMetrics]:
        """
        Calculate trend metrics for all technologies in the current snapshot.
        
        Args:
            current_snapshot: The most recent technology snapshot.
            previous_snapshots: List of previous snapshots in chronological order.
        
        Returns:
            List of TrendMetrics for each technology.
        
        Raises:
            MissingHistoricalDataError: If no previous snapshots are provided.
        """
        if not previous_snapshots:
            logger.warning("[TrendCalculator] No previous snapshots provided. Using basic analysis.")
            return self._calculate_basic_trends(current_snapshot)

        metrics = []
        for tech_name, current_entry in current_snapshot.technologies.items():
            history = self._extract_technology_history(
                tech_name, current_snapshot, previous_snapshots
            )
            metric = self._calculate_single_trend(tech_name, history)
            metrics.append(metric)

        logger.info("[TrendCalculator] Calculated trends for %d technologies.", len(metrics))
        return metrics

    def _calculate_basic_trends(
        self, current_snapshot: TechnologySnapshot
    ) -> List[TrendMetrics]:
        """Calculate basic trends without historical data."""
        metrics = []
        for tech_name, entry in current_snapshot.technologies.items():
            metric = TrendMetrics(
                name=tech_name,
                trend=TrendDirection.STABLE,
                growth_rate=0.0,
                decline_rate=0.0,
                moving_average=float(entry.percentage),
                momentum=0.0,
                velocity=0.0,
                acceleration=0.0,
                volatility=0.0,
                data_points=1,
            )
            metrics.append(metric)
        return metrics

    def _extract_technology_history(
        self,
        tech_name: str,
        current_snapshot: TechnologySnapshot,
        previous_snapshots: List[TechnologySnapshot],
    ) -> List[Dict[str, Any]]:
        """Extract historical data points for a specific technology."""
        history = []

        for snapshot in previous_snapshots:
            if tech_name in snapshot.technologies:
                entry = snapshot.technologies[tech_name]
                history.append({
                    "timestamp": snapshot.timestamp,
                    "mentions": entry.mentions,
                    "percentage": entry.percentage,
                    "rank": entry.rank,
                })

        if tech_name in current_snapshot.technologies:
            current_entry = current_snapshot.technologies[tech_name]
            history.append({
                "timestamp": current_snapshot.timestamp,
                "mentions": current_entry.mentions,
                "percentage": current_entry.percentage,
                "rank": current_entry.rank,
            })

        return history

    def _calculate_single_trend(
        self, tech_name: str, history: List[Dict[str, Any]]
    ) -> TrendMetrics:
        """Calculate trend metrics for a single technology."""
        if len(history) < self._thresholds.min_data_points:
            return self._create_minimal_trend(tech_name, history)

        percentages = [h["percentage"] for h in history]
        mentions = [h["mentions"] for h in history]
        ranks = [h["rank"] for h in history]

        growth_rate = self._calculate_growth_rate(percentages)
        decline_rate = self._calculate_decline_rate(percentages)
        moving_average = self._calculate_moving_average(percentages)
        momentum = self._calculate_momentum(percentages)
        velocity = self._calculate_velocity(percentages)
        acceleration = self._calculate_acceleration(percentages)
        volatility = self._calculate_volatility(percentages)
        trend = self._classify_trend(growth_rate, momentum, volatility)

        return TrendMetrics(
            name=tech_name,
            trend=trend,
            growth_rate=round(growth_rate, 2),
            decline_rate=round(decline_rate, 2),
            moving_average=round(moving_average, 2),
            momentum=round(momentum, 2),
            velocity=round(velocity, 2),
            acceleration=round(acceleration, 2),
            volatility=round(volatility, 2),
            data_points=len(history),
        )

    def _create_minimal_trend(
        self, tech_name: str, history: List[Dict[str, Any]]
    ) -> TrendMetrics:
        """Create a minimal trend for technologies with insufficient data."""
        current_pct = history[-1]["percentage"] if history else 0.0
        return TrendMetrics(
            name=tech_name,
            trend=TrendDirection.EMERGING,
            growth_rate=0.0,
            decline_rate=0.0,
            moving_average=current_pct,
            momentum=0.0,
            velocity=0.0,
            acceleration=0.0,
            volatility=0.0,
            data_points=len(history),
        )

    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate overall growth rate from first to last value."""
        if len(values) < 2:
            return 0.0
        first, last = values[0], values[-1]
        if first == 0:
            return 100.0 if last > 0 else 0.0
        return ((last - first) / first) * 100

    def _calculate_decline_rate(self, values: List[float]) -> float:
        """Calculate decline rate (negative growth)."""
        growth = self._calculate_growth_rate(values)
        return abs(min(growth, 0.0))

    def _calculate_moving_average(self, values: List[float]) -> float:
        """Calculate moving average with configured window size."""
        window = min(self._thresholds.moving_average_window, len(values))
        if window == 0:
            return 0.0
        recent_values = values[-window:]
        return sum(recent_values) / len(recent_values)

    def _calculate_momentum(self, values: List[float]) -> float:
        """
        Calculate momentum as the average of recent changes.
        
        Positive momentum indicates accelerating growth.
        """
        if len(values) < 2:
            return 0.0

        changes = [values[i] - values[i - 1] for i in range(1, len(values))]
        window = min(self._thresholds.moving_average_window, len(changes))
        recent_changes = changes[-window:]
        return sum(recent_changes) / len(recent_changes)

    def _calculate_velocity(self, values: List[float]) -> float:
        """Calculate velocity (rate of change per time step)."""
        if len(values) < 2:
            return 0.0
        total_change = values[-1] - values[0]
        time_steps = len(values) - 1
        return total_change / time_steps

    def _calculate_acceleration(self, values: List[float]) -> float:
        """Calculate acceleration (change in velocity)."""
        if len(values) < 3:
            return 0.0

        velocities = [
            values[i] - values[i - 1] for i in range(1, len(values))
        ]
        if len(velocities) < 2:
            return 0.0

        total_velocity_change = velocities[-1] - velocities[0]
        time_steps = len(velocities) - 1
        return total_velocity_change / time_steps

    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation of changes)."""
        if len(values) < 2:
            return 0.0

        changes = [values[i] - values[i - 1] for i in range(1, len(values))]
        mean_change = sum(changes) / len(changes)
        squared_diffs = [(c - mean_change) ** 2 for c in changes]
        variance = sum(squared_diffs) / len(squared_diffs)
        return variance ** 0.5

    def _classify_trend(
        self, growth_rate: float, momentum: float, volatility: float
    ) -> TrendDirection:
        """Classify trend direction based on growth rate and momentum."""
        t = self._thresholds

        if growth_rate >= t.emerging_growth:
            return TrendDirection.EMERGING
        elif growth_rate >= t.rapidly_rising_growth:
            return TrendDirection.RAPIDLY_RISING
        elif growth_rate >= t.rising_growth:
            return TrendDirection.RISING
        elif growth_rate <= t.deprecated_threshold:
            return TrendDirection.DEPRECATED
        elif growth_rate <= t.legacy_threshold:
            return TrendDirection.LEGACY
        elif growth_rate <= t.declining_threshold:
            return TrendDirection.DECLINING
        else:
            return TrendDirection.STABLE

    def get_trend_summary(
        self, metrics: List[TrendMetrics]
    ) -> Dict[str, List[str]]:
        """Group technologies by their trend direction."""
        summary: Dict[str, List[str]] = {
            trend.value: [] for trend in TrendDirection
        }
        for metric in metrics:
            summary[metric.trend.value].append(metric.name)
        return summary

    def get_fastest_growing(
        self, metrics: List[TrendMetrics], top_n: int = 10
    ) -> List[TrendMetrics]:
        """Get the top N fastest growing technologies."""
        sorted_metrics = sorted(metrics, key=lambda m: m.growth_rate, reverse=True)
        return sorted_metrics[:top_n]

    def get_most_volatile(
        self, metrics: List[TrendMetrics], top_n: int = 10
    ) -> List[TrendMetrics]:
        """Get the top N most volatile technologies."""
        sorted_metrics = sorted(metrics, key=lambda m: m.volatility, reverse=True)
        return sorted_metrics[:top_n]
