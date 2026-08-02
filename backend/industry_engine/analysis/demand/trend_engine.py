"""
Trend Engine for the Demand & Trend Intelligence Engine.

Orchestrates trend analysis by managing historical snapshots
and calculating trend metrics:
- Snapshot management
- Historical comparison
- Trend calculation
- Growth detection
"""

import logging
import time
from typing import Any, Dict, List, Optional

from backend.industry_engine.analysis.demand.config import DemandConfig
from backend.industry_engine.analysis.demand.exceptions import (
    EmptyDatasetError,
    MissingHistoricalDataError,
)
from backend.industry_engine.analysis.demand.growth_detector import GrowthDetector, GrowthPattern
from backend.industry_engine.analysis.demand.models import (
    SnapshotEntry,
    SnapshotHistory,
    SnapshotManager,
    TechnologyFrequencyInput,
    TechnologySnapshot,
    TrendMetrics,
)
from backend.industry_engine.analysis.demand.trend_calculator import TrendCalculator

logger = logging.getLogger("industry_engine.analysis.demand.trend_engine")


class TrendEngine:
    """
    Orchestrates trend analysis for technologies.
    
    Manages historical snapshots, calculates trends, and detects
    growth patterns over time.
    """

    def __init__(self, config: Optional[DemandConfig] = None) -> None:
        """
        Initialize the trend engine.
        
        Args:
            config: Optional DemandConfig for tuning.
        """
        self._config = config or DemandConfig()
        self._snapshot_manager = SnapshotManager()
        self._trend_calculator = TrendCalculator(config=self._config)
        self._growth_detector = GrowthDetector(config=self._config)
        self.last_metrics: Optional[List[TrendMetrics]] = None
        self.last_patterns: Optional[List[GrowthPattern]] = None
        logger.info("[TrendEngine] Initialized.")

    def process(
        self,
        technologies: Dict[str, TechnologyFrequencyInput],
        total_jobs: int,
        load_history: Optional[SnapshotHistory] = None,
    ) -> List[TrendMetrics]:
        """
        Process current data and calculate trends.
        
        Args:
            technologies: Current technology frequency data.
            total_jobs: Total number of jobs in current dataset.
            load_history: Optional historical snapshot data to load.
        
        Returns:
            List of TrendMetrics for all technologies.
        
        Raises:
            EmptyDatasetError: If technologies dictionary is empty.
        """
        if not technologies:
            raise EmptyDatasetError("Trend engine requires at least one technology.")

        start_time = time.time()

        if load_history:
            self._snapshot_manager.load_history(load_history)

        current_snapshot = self._create_snapshot(technologies, total_jobs)
        previous_snapshots = self._snapshot_manager.get_all_snapshots()

        metrics = self._trend_calculator.calculate_trends(
            current_snapshot=current_snapshot,
            previous_snapshots=previous_snapshots,
        )

        patterns = self._growth_detector.detect_patterns(metrics)

        self._snapshot_manager.create_snapshot(technologies, total_jobs)

        self.last_metrics = metrics
        self.last_patterns = patterns

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(
            "[TrendEngine] Processed trends for %d technologies in %ms.",
            len(metrics), elapsed_ms
        )
        return metrics

    def _create_snapshot(
        self,
        technologies: Dict[str, TechnologyFrequencyInput],
        total_jobs: int,
    ) -> TechnologySnapshot:
        """Create a snapshot from current technology data."""
        snapshot = TechnologySnapshot(total_jobs=total_jobs)
        for name, freq in technologies.items():
            snapshot.technologies[name] = SnapshotEntry(
                name=name,
                mentions=freq.mentions,
                percentage=freq.percentage,
                rank=freq.rank,
            )
        return snapshot

    def get_trends(self) -> Optional[List[TrendMetrics]]:
        """Get the last calculated trend metrics."""
        return self.last_metrics

    def get_growth_patterns(self) -> Optional[List[GrowthPattern]]:
        """Get the last detected growth patterns."""
        return self.last_patterns

    def get_snapshot_history(self) -> SnapshotHistory:
        """Get the complete snapshot history."""
        return self._snapshot_manager.get_history()

    def load_snapshot_history(self, history: SnapshotHistory) -> None:
        """Load historical snapshot data."""
        self._snapshot_manager.load_history(history)

    def get_technology_history(self, tech_name: str) -> List[Dict[str, Any]]:
        """Get historical data for a specific technology."""
        return self._snapshot_manager.get_technology_history(tech_name)

    def get_trend_summary(self) -> Dict[str, Any]:
        """Get summary of trend analysis results."""
        if not self.last_metrics:
            return {}

        summary = self._trend_calculator.get_trend_summary(self.last_metrics)
        return {
            "total_technologies": len(self.last_metrics),
            "trend_distribution": {k: len(v) for k, v in summary.items()},
            "fastest_growing": [
                m.name for m in self._trend_calculator.get_fastest_growing(self.last_metrics, 5)
            ],
            "most_volatile": [
                m.name for m in self._trend_calculator.get_most_volatile(self.last_metrics, 5)
            ],
        }

    def get_emerging_technologies(self) -> List[str]:
        """Get list of emerging technologies."""
        if not self.last_metrics:
            return []
        return [
            m.name for m in self.last_metrics
            if m.trend.value in ("Emerging", "Rapidly Rising")
        ]

    def get_declining_technologies(self) -> List[str]:
        """Get list of declining technologies."""
        if not self.last_metrics:
            return []
        return [
            m.name for m in self.last_metrics
            if m.trend.value in ("Declining", "Legacy", "Deprecated")
        ]

    def export_history(self) -> Dict[str, Any]:
        """Export snapshot history as dictionary."""
        history = self._snapshot_manager.get_history()
        return history.model_dump()
