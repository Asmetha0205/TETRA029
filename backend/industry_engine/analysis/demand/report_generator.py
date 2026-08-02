"""
Report Generator for the Demand & Trend Intelligence Engine.

Generates comprehensive reports for:
- Demand Report
- Trend Report
- Emerging Technology Report
- Technology Ranking Report
- Industry Intelligence Report
- Visualization Data
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from backend.industry_engine.analysis.demand.config import DemandConfig
from backend.industry_engine.analysis.demand.exceptions import ExportError, ReportGenerationError
from backend.industry_engine.analysis.demand.models import (
    DemandReport,
    DemandScore,
    IndustryReport,
    IndustryScore,
    TechnologyClassification,
    TechnologyIntelligence,
    TechnologyRanking,
    TrendDirection,
    TrendMetrics,
    TrendReport,
    VisualizationData,
)

logger = logging.getLogger("industry_engine.analysis.demand.report_generator")


class ReportGenerator:
    """
    Generates comprehensive intelligence reports.
    
    Combines all analysis results into structured reports
    and prepares visualization data.
    """

    def __init__(self, config: Optional[DemandConfig] = None) -> None:
        """
        Initialize the report generator.
        
        Args:
            config: Optional DemandConfig for tuning.
        """
        self._config = config or DemandConfig()
        logger.info("[ReportGenerator] Initialized.")

    def generate_demand_report(
        self,
        technologies: List[TechnologyIntelligence],
        summary: Optional[Dict[str, Any]] = None,
    ) -> DemandReport:
        """
        Generate demand report.
        
        Args:
            technologies: List of TechnologyIntelligence objects.
            summary: Optional summary statistics.
        
        Returns:
            DemandReport object.
        """
        if summary is None:
            summary = self._generate_demand_summary(technologies)

        report = DemandReport(
            technologies=technologies,
            summary=summary,
        )
        logger.info("[ReportGenerator] Generated demand report with %d technologies.", len(technologies))
        return report

    def generate_trend_report(
        self,
        trend_metrics: List[TrendMetrics],
        summary: Optional[Dict[str, Any]] = None,
    ) -> TrendReport:
        """
        Generate trend report.
        
        Args:
            trend_metrics: List of TrendMetrics objects.
            summary: Optional summary statistics.
        
        Returns:
            TrendReport object.
        """
        emerging = [m.name for m in trend_metrics if m.trend == TrendDirection.EMERGING]
        rapidly_rising = [m.name for m in trend_metrics if m.trend == TrendDirection.RAPIDLY_RISING]
        rising = [m.name for m in trend_metrics if m.trend == TrendDirection.RISING]
        stable = [m.name for m in trend_metrics if m.trend == TrendDirection.STABLE]
        declining = [m.name for m in trend_metrics if m.trend == TrendDirection.DECLINING]
        legacy = [m.name for m in trend_metrics if m.trend == TrendDirection.LEGACY]
        deprecated = [m.name for m in trend_metrics if m.trend == TrendDirection.DEPRECATED]

        if summary is None:
            summary = self._generate_trend_summary(
                emerging, rapidly_rising, rising, stable, declining, legacy, deprecated
            )

        report = TrendReport(
            technologies=trend_metrics,
            emerging_technologies=emerging + rapidly_rising,
            declining_technologies=declining + legacy + deprecated,
            stable_technologies=stable,
            summary=summary,
        )
        logger.info("[ReportGenerator] Generated trend report.")
        return report

    def generate_industry_report(
        self,
        technologies: List[TechnologyIntelligence],
        rankings: List[TechnologyRanking],
        trend_metrics: List[TrendMetrics],
        summary: Optional[Dict[str, Any]] = None,
    ) -> IndustryReport:
        """
        Generate comprehensive industry intelligence report.
        
        Args:
            technologies: List of TechnologyIntelligence objects.
            rankings: List of TechnologyRanking objects.
            trend_metrics: List of TrendMetrics objects.
            summary: Optional summary statistics.
        
        Returns:
            IndustryReport object.
        """
        if summary is None:
            summary = self._generate_industry_summary(technologies, rankings)

        growth_rankings = [r.name for r in sorted(
            rankings, key=lambda r: r.growth_rank
        ) if r.growth_rank > 0]

        emerging_rankings = [r.name for r in sorted(
            rankings, key=lambda r: r.emerging_rank
        ) if r.emerging_rank > 0]

        report = IndustryReport(
            technologies=technologies,
            rankings=rankings,
            summary=summary,
            growth_rankings=growth_rankings,
            emerging_rankings=emerging_rankings,
        )
        logger.info("[ReportGenerator] Generated industry report.")
        return report

    def generate_visualization_data(
        self,
        technologies: List[TechnologyIntelligence],
        trend_metrics: List[TrendMetrics],
        rankings: List[TechnologyRanking],
    ) -> VisualizationData:
        """
        Generate pre-formatted data for visualizations.
        
        Args:
            technologies: List of TechnologyIntelligence objects.
            trend_metrics: List of TrendMetrics objects.
            rankings: List of TechnologyRanking objects.
        
        Returns:
            VisualizationData object with chart-ready data.
        """
        trend_map = {t.name: t for t in trend_metrics}

        line_chart = self._prepare_line_chart_data(technologies, trend_map)
        bar_chart = self._prepare_bar_chart_data(technologies)
        heatmap = self._prepare_heatmap_data(technologies, trend_map)
        radar_chart = self._prepare_radar_chart_data(technologies[:10])
        trend_timeline = self._prepare_trend_timeline(trend_metrics)
        bubble_chart = self._prepare_bubble_chart_data(technologies, trend_map)

        viz_data = VisualizationData(
            line_chart=line_chart,
            bar_chart=bar_chart,
            heatmap=heatmap,
            radar_chart=radar_chart,
            trend_timeline=trend_timeline,
            bubble_chart=bubble_chart,
        )
        logger.info("[ReportGenerator] Generated visualization data.")
        return viz_data

    def _prepare_line_chart_data(
        self,
        technologies: List[TechnologyIntelligence],
        trend_map: Dict[str, TrendMetrics],
    ) -> Dict[str, Any]:
        """Prepare data for line chart (demand over time)."""
        top_techs = sorted(technologies, key=lambda t: t.demand_score, reverse=True)[:10]
        return {
            "labels": [t.name for t in top_techs],
            "datasets": [
                {
                    "label": "Demand Score",
                    "data": [t.demand_score for t in top_techs],
                },
                {
                    "label": "Industry Score",
                    "data": [t.industry_score for t in top_techs],
                },
            ],
        }

    def _prepare_bar_chart_data(
        self, technologies: List[TechnologyIntelligence]
    ) -> Dict[str, Any]:
        """Prepare data for bar chart (top technologies)."""
        top_techs = sorted(technologies, key=lambda t: t.industry_score, reverse=True)[:15]
        return {
            "labels": [t.name for t in top_techs],
            "datasets": [
                {
                    "label": "Industry Score",
                    "data": [t.industry_score for t in top_techs],
                },
            ],
        }

    def _prepare_heatmap_data(
        self,
        technologies: List[TechnologyIntelligence],
        trend_map: Dict[str, TrendMetrics],
    ) -> Dict[str, Any]:
        """Prepare data for heatmap (demand vs growth)."""
        top_techs = sorted(technologies, key=lambda t: t.industry_score, reverse=True)[:20]
        return {
            "x_labels": [t.name for t in top_techs],
            "y_labels": ["Demand", "Growth", "Industry Score"],
            "data": [
                [t.demand_score for t in top_techs],
                [t.growth for t in top_techs],
                [t.industry_score for t in top_techs],
            ],
        }

    def _prepare_radar_chart_data(
        self, technologies: List[TechnologyIntelligence]
    ) -> Dict[str, Any]:
        """Prepare data for radar chart (technology comparison)."""
        return {
            "labels": ["Demand", "Growth", "Industry Score", "Classification"],
            "datasets": [
                {
                    "label": t.name,
                    "data": [
                        t.demand_score,
                        min(max(t.growth, 0), 100),
                        t.industry_score,
                        self._classification_to_score(t.classification),
                    ],
                }
                for t in technologies
            ],
        }

    def _prepare_trend_timeline(
        self, trend_metrics: List[TrendMetrics]
    ) -> Dict[str, Any]:
        """Prepare data for trend timeline."""
        return {
            "emerging": [m.name for m in trend_metrics if m.trend == TrendDirection.EMERGING],
            "rapidly_rising": [m.name for m in trend_metrics if m.trend == TrendDirection.RAPIDLY_RISING],
            "rising": [m.name for m in trend_metrics if m.trend == TrendDirection.RISING],
            "stable": [m.name for m in trend_metrics if m.trend == TrendDirection.STABLE],
            "declining": [m.name for m in trend_metrics if m.trend == TrendDirection.DECLINING],
        }

    def _prepare_bubble_chart_data(
        self,
        technologies: List[TechnologyIntelligence],
        trend_map: Dict[str, TrendMetrics],
    ) -> Dict[str, Any]:
        """Prepare data for bubble chart (demand vs growth vs mentions)."""
        top_techs = sorted(technologies, key=lambda t: t.industry_score, reverse=True)[:20]
        return {
            "datasets": [
                {
                    "label": t.name,
                    "data": [{
                        "x": t.demand_score,
                        "y": t.growth,
                        "r": max(3, min(t.mentions / 10, 30)),
                    }],
                }
                for t in top_techs
            ],
        }

    def _classification_to_score(self, classification: TechnologyClassification) -> float:
        """Convert classification to numeric score for visualization."""
        mapping = {
            TechnologyClassification.CORE: 100,
            TechnologyClassification.SUPPORTING: 75,
            TechnologyClassification.EMERGING: 50,
            TechnologyClassification.EXPERIMENTAL: 25,
            TechnologyClassification.LEGACY: 10,
        }
        return mapping.get(classification, 50)

    def _generate_demand_summary(
        self, technologies: List[TechnologyIntelligence]
    ) -> Dict[str, Any]:
        """Generate summary statistics for demand report."""
        if not technologies:
            return {}

        scores = [t.demand_score for t in technologies]
        return {
            "total_technologies": len(technologies),
            "avg_demand_score": sum(scores) / len(scores),
            "max_demand_score": max(scores),
            "min_demand_score": min(scores),
            "top_technology": max(technologies, key=lambda t: t.demand_score).name,
        }

    def _generate_trend_summary(
        self,
        emerging: List[str],
        rapidly_rising: List[str],
        rising: List[str],
        stable: List[str],
        declining: List[str],
        legacy: List[str],
        deprecated: List[str],
    ) -> Dict[str, Any]:
        """Generate summary statistics for trend report."""
        total = len(emerging) + len(rapidly_rising) + len(rising) + len(stable) + len(declining) + len(legacy) + len(deprecated)
        return {
            "total_technologies": total,
            "emerging_count": len(emerging),
            "rapidly_rising_count": len(rapidly_rising),
            "rising_count": len(rising),
            "stable_count": len(stable),
            "declining_count": len(declining),
            "legacy_count": len(legacy),
            "deprecated_count": len(deprecated),
        }

    def _generate_industry_summary(
        self,
        technologies: List[TechnologyIntelligence],
        rankings: List[TechnologyRanking],
    ) -> Dict[str, Any]:
        """Generate summary statistics for industry report."""
        if not technologies:
            return {}

        scores = [t.industry_score for t in technologies]
        classifications = {}
        for t in technologies:
            classifications[t.classification.value] = classifications.get(t.classification.value, 0) + 1

        return {
            "total_technologies": len(technologies),
            "avg_industry_score": sum(scores) / len(scores),
            "max_industry_score": max(scores),
            "min_industry_score": min(scores),
            "top_technology": max(technologies, key=lambda t: t.industry_score).name,
            "classifications": classifications,
        }

    def export_report(
        self,
        report: Union[DemandReport, TrendReport, IndustryReport],
        output_path: Union[str, Path],
    ) -> Path:
        """
        Export a report to JSON file.
        
        Args:
            report: Report object to export.
            output_path: Path to write the JSON file.
        
        Returns:
            Path to the exported file.
        
        Raises:
            ExportError: If export fails.
        """
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            if hasattr(report, "model_dump"):
                data = report.model_dump()
            else:
                data = report.__dict__

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info("[ReportGenerator] Exported report to %s", path)
            return path
        except Exception as e:
            raise ExportError(f"Failed to export report: {e}") from e
