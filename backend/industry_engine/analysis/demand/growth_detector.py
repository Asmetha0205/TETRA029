"""
Growth Detector for the Demand & Trend Intelligence Engine.

Detects and classifies growth patterns for technologies:
- Explosive growth
- Significant growth
- Moderate growth
- Stable
- Decline
- Steep decline
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from backend.industry_engine.analysis.demand.config import DemandConfig
from backend.industry_engine.analysis.demand.models import (
    TrendMetrics,
)

logger = logging.getLogger("industry_engine.analysis.demand.growth_detector")


class GrowthPattern:
    """Represents a detected growth pattern."""

    def __init__(
        self,
        name: str,
        pattern_type: str,
        growth_rate: float,
        confidence: float,
        description: str,
    ):
        self.name = name
        self.pattern_type = pattern_type
        self.growth_rate = growth_rate
        self.confidence = confidence
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "pattern_type": self.pattern_type,
            "growth_rate": self.growth_rate,
            "confidence": self.confidence,
            "description": self.description,
        }


class GrowthDetector:
    """
    Detects and classifies growth patterns for technologies.
    
    Analyzes trend metrics to identify specific growth patterns
    and provide confidence scores for each detection.
    """

    def __init__(self, config: Optional[DemandConfig] = None) -> None:
        """
        Initialize the growth detector.
        
        Args:
            config: Optional DemandConfig for tuning thresholds.
        """
        self._config = config or DemandConfig()
        self._thresholds = self._config.growth_thresholds
        logger.info("[GrowthDetector] Initialized with thresholds: %s", self._thresholds)

    def detect_patterns(
        self, metrics: List[TrendMetrics]
    ) -> List[GrowthPattern]:
        """
        Detect growth patterns for all technologies.
        
        Args:
            metrics: List of TrendMetrics to analyze.
        
        Returns:
            List of detected GrowthPattern objects.
        """
        patterns = []
        for metric in metrics:
            if metric.data_points < 2 and metric.trend.value == "Emerging":
                pattern = self._detect_emerging_pattern(metric)
            else:
                pattern = self._detect_standard_pattern(metric)
            patterns.append(pattern)

        patterns.sort(key=lambda p: p.growth_rate, reverse=True)
        logger.info("[GrowthDetector] Detected %d growth patterns.", len(patterns))
        return patterns

    def _detect_emerging_pattern(self, metric: TrendMetrics) -> GrowthPattern:
        """Detect pattern for new/emerging technologies."""
        return GrowthPattern(
            name=metric.name,
            pattern_type="Emerging",
            growth_rate=metric.growth_rate,
            confidence=0.5,
            description=f"{metric.name} is a newly detected technology with {metric.data_points} data point(s)."
        )

    def _detect_standard_pattern(self, metric: TrendMetrics) -> GrowthPattern:
        """Detect pattern based on growth rate and other metrics."""
        t = self._thresholds
        growth = metric.growth_rate
        momentum = metric.momentum
        volatility = metric.volatility

        if growth >= t.explosive_growth:
            confidence = self._calculate_confidence(growth, momentum, volatility, "explosive")
            return GrowthPattern(
                name=metric.name,
                pattern_type="Explosive Growth",
                growth_rate=growth,
                confidence=confidence,
                description=f"{metric.name} shows explosive growth at {growth:.1f}%."
            )
        elif growth >= t.significant_growth:
            confidence = self._calculate_confidence(growth, momentum, volatility, "significant")
            return GrowthPattern(
                name=metric.name,
                pattern_type="Significant Growth",
                growth_rate=growth,
                confidence=confidence,
                description=f"{metric.name} shows significant growth at {growth:.1f}%."
            )
        elif growth >= 5.0:
            confidence = self._calculate_confidence(growth, momentum, volatility, "moderate")
            return GrowthPattern(
                name=metric.name,
                pattern_type="Moderate Growth",
                growth_rate=growth,
                confidence=confidence,
                description=f"{metric.name} shows moderate growth at {growth:.1f}%."
            )
        elif growth >= t.decline_threshold:
            confidence = self._calculate_confidence(growth, momentum, volatility, "stable")
            return GrowthPattern(
                name=metric.name,
                pattern_type="Stable",
                growth_rate=growth,
                confidence=confidence,
                description=f"{metric.name} is stable with {growth:.1f}% change."
            )
        elif growth >= t.steep_decline:
            confidence = self._calculate_confidence(abs(growth), momentum, volatility, "decline")
            return GrowthPattern(
                name=metric.name,
                pattern_type="Decline",
                growth_rate=growth,
                confidence=confidence,
                description=f"{metric.name} is declining at {growth:.1f}%."
            )
        else:
            confidence = self._calculate_confidence(abs(growth), momentum, volatility, "steep_decline")
            return GrowthPattern(
                name=metric.name,
                pattern_type="Steep Decline",
                growth_rate=growth,
                confidence=confidence,
                description=f"{metric.name} shows steep decline at {growth:.1f}%."
            )

    def _calculate_confidence(
        self,
        growth: float,
        momentum: float,
        volatility: float,
        pattern_type: str,
    ) -> float:
        """Calculate confidence score for pattern detection."""
        base_confidence = 0.7

        if pattern_type in ("explosive", "significant"):
            if momentum > 0:
                base_confidence += 0.1
            if volatility < 10:
                base_confidence += 0.1
        elif pattern_type in ("decline", "steep_decline"):
            if momentum < 0:
                base_confidence += 0.1
            if volatility < 10:
                base_confidence += 0.1
        elif pattern_type == "stable":
            if volatility < 5:
                base_confidence += 0.15

        return min(base_confidence, 1.0)

    def get_emerging_technologies(
        self, patterns: List[GrowthPattern]
    ) -> List[GrowthPattern]:
        """Get technologies with explosive or significant growth."""
        return [
            p for p in patterns
            if p.pattern_type in ("Explosive Growth", "Significant Growth")
        ]

    def get_declining_technologies(
        self, patterns: List[GrowthPattern]
    ) -> List[GrowthPattern]:
        """Get technologies with decline or steep decline."""
        return [
            p for p in patterns
            if p.pattern_type in ("Decline", "Steep Decline")
        ]

    def get_stable_technologies(
        self, patterns: List[GrowthPattern]
    ) -> List[GrowthPattern]:
        """Get stable technologies."""
        return [
            p for p in patterns
            if p.pattern_type == "Stable"
        ]

    def get_pattern_summary(
        self, patterns: List[GrowthPattern]
    ) -> Dict[str, int]:
        """Get count of each pattern type."""
        summary: Dict[str, int] = {}
        for pattern in patterns:
            summary[pattern.pattern_type] = summary.get(pattern.pattern_type, 0) + 1
        return summary
