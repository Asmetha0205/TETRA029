"""
Demand Engine for the Demand & Trend Intelligence Engine.

Main orchestrator that combines all analysis components:
- Demand calculation
- Trend analysis
- Growth detection
- Technology ranking
- Industry score calculation
- Report generation
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from backend.industry_engine.analysis.demand.config import DemandConfig
from backend.industry_engine.analysis.demand.demand_calculator import DemandCalculator
from backend.industry_engine.analysis.demand.exceptions import (
    DemandEngineError,
    EmptyDatasetError,
    ExportError,
    InvalidInputError,
)
from backend.industry_engine.analysis.demand.growth_detector import GrowthDetector, GrowthPattern
from backend.industry_engine.analysis.demand.industry_score import IndustryScoreCalculator
from backend.industry_engine.analysis.demand.models import (
    DemandReport,
    DemandScore,
    IndustryReport,
    IndustryScore,
    SnapshotHistory,
    TechnologyClassification,
    TechnologyFrequencyInput,
    TechnologyIntelligence,
    TechnologyRanking,
    TrendDirection,
    TrendMetrics,
    TrendReport,
    VisualizationData,
)
from backend.industry_engine.analysis.demand.report_generator import ReportGenerator
from backend.industry_engine.analysis.demand.technology_ranker import TechnologyRanker
from backend.industry_engine.analysis.demand.trend_calculator import TrendCalculator
from backend.industry_engine.analysis.demand.trend_engine import TrendEngine

logger = logging.getLogger("industry_engine.analysis.demand.demand_engine")


class DemandEngine:
    """
    Main orchestrator for the Demand & Trend Intelligence Engine.
    
    Converts raw frequency statistics into meaningful Industry Intelligence
    by combining demand analysis, trend detection, and scoring.
    """

    def __init__(self, config: Optional[DemandConfig] = None) -> None:
        """
        Initialize the demand engine.
        
        Args:
            config: Optional DemandConfig for tuning all parameters.
        """
        self._config = config or DemandConfig()
        self._demand_calculator = DemandCalculator(config=self._config)
        self._trend_engine = TrendEngine(config=self._config)
        self._growth_detector = GrowthDetector(config=self._config)
        self._industry_score_calculator = IndustryScoreCalculator(config=self._config)
        self._technology_ranker = TechnologyRanker(config=self._config)
        self._report_generator = ReportGenerator(config=self._config)

        self.last_report: Optional[IndustryReport] = None
        self.last_technologies: Optional[List[TechnologyIntelligence]] = None
        self.last_rankings: Optional[List[TechnologyRanking]] = None
        self.last_trend_metrics: Optional[List[TrendMetrics]] = None

        logger.info("[DemandEngine] Initialized Demand & Trend Intelligence Engine.")

    def process(
        self,
        technologies: Dict[str, Any],
        total_jobs: int,
        load_history: Optional[SnapshotHistory] = None,
    ) -> IndustryReport:
        """
        Execute the full demand and trend analysis pipeline.
        
        Args:
            technologies: Dictionary mapping technology names to their frequency data.
                Format: {"TechName": {"mentions": int, "percentage": float, "rank": int}}
            total_jobs: Total number of jobs in the dataset.
            load_history: Optional historical snapshot data to load.
        
        Returns:
            IndustryReport with complete intelligence data.
        
        Raises:
            EmptyDatasetError: If technologies dictionary is empty.
            InvalidInputError: If input data is invalid.
        """
        if not technologies:
            raise EmptyDatasetError("Demand engine requires at least one technology.")

        start_time = time.time()

        freq_inputs = self._parse_frequency_inputs(technologies)

        demand_scores = self._demand_calculator.calculate_scores(
            technologies=freq_inputs,
            total_jobs=total_jobs,
        )

        trend_metrics = self._trend_engine.process(
            technologies=freq_inputs,
            total_jobs=total_jobs,
            load_history=load_history,
        )

        industry_scores = self._industry_score_calculator.calculate_scores(
            demand_scores=demand_scores,
            trend_metrics=trend_metrics,
            total_technologies=len(technologies),
        )

        tech_intelligences = self._build_technology_intelligences(
            freq_inputs=freq_inputs,
            demand_scores=demand_scores,
            trend_metrics=trend_metrics,
            industry_scores=industry_scores,
        )

        rankings = self._technology_ranker.generate_rankings(
            technologies=tech_intelligences,
            demand_scores=demand_scores,
            trend_metrics=trend_metrics,
        )

        report = self._report_generator.generate_industry_report(
            technologies=tech_intelligences,
            rankings=rankings,
            trend_metrics=trend_metrics,
        )

        self.last_report = report
        self.last_technologies = tech_intelligences
        self.last_rankings = rankings
        self.last_trend_metrics = trend_metrics

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(
            "[DemandEngine] Analysis complete: %d technologies, "
            "avg industry score %.1f in %dms.",
            len(tech_intelligences),
            report.summary.get("avg_industry_score", 0),
            elapsed_ms,
        )
        return report

    def process_from_frequency_report(
        self,
        frequency_data: Dict[str, Any],
    ) -> IndustryReport:
        """
        Process data directly from a frequency report format.
        
        Args:
            frequency_data: Frequency report data with technology statistics.
        
        Returns:
            IndustryReport with complete intelligence data.
        """
        technologies = {}
        total_jobs = 0

        if "technologies" in frequency_data:
            for tech in frequency_data["technologies"]:
                name = tech.get("name", "")
                if name:
                    technologies[name] = {
                        "mentions": tech.get("mentions", 0),
                        "percentage": tech.get("percentage", 0),
                        "rank": tech.get("rank", 0),
                    }
                    total_jobs = max(total_jobs, tech.get("mentions", 0))

        if "summary" in frequency_data:
            total_jobs = frequency_data["summary"].get("total_jobs", total_jobs)

        if total_jobs == 0:
            total_jobs = sum(t.get("mentions", 0) for t in technologies.values())

        return self.process(technologies=technologies, total_jobs=total_jobs)

    def process_json(self, raw_json: str) -> IndustryReport:
        """
        Process a raw JSON string payload.
        
        Args:
            raw_json: JSON string with technology frequency data.
        
        Returns:
            IndustryReport with complete intelligence data.
        
        Raises:
            InvalidInputError: If JSON is invalid.
        """
        try:
            data = json.loads(raw_json)
        except (json.JSONDecodeError, TypeError) as exc:
            raise InvalidInputError(f"Failed to parse JSON: {exc}") from exc

        if isinstance(data, dict):
            if "technologies" in data:
                return self.process_from_frequency_report(data)
            return self.process(technologies=data, total_jobs=data.get("total_jobs", 0))
        elif isinstance(data, list):
            technologies = {}
            for item in data:
                if isinstance(item, dict):
                    name = item.get("name", "")
                    if name:
                        technologies[name] = item
            return self.process(technologies=technologies, total_jobs=0)
        else:
            raise InvalidInputError(f"Unsupported JSON type: {type(data).__name__}")

    def _parse_frequency_inputs(
        self, technologies: Dict[str, Any]
    ) -> Dict[str, TechnologyFrequencyInput]:
        """Parse raw technology data into TechnologyFrequencyInput objects."""
        freq_inputs = {}
        for name, data in technologies.items():
            if isinstance(data, dict):
                freq_inputs[name] = TechnologyFrequencyInput(
                    mentions=data.get("mentions", 0),
                    percentage=data.get("percentage", 0),
                    rank=data.get("rank", 0),
                )
            else:
                freq_inputs[name] = TechnologyFrequencyInput(
                    mentions=0, percentage=0, rank=0
                )
        return freq_inputs

    def _build_technology_intelligences(
        self,
        freq_inputs: Dict[str, TechnologyFrequencyInput],
        demand_scores: List[DemandScore],
        trend_metrics: List[TrendMetrics],
        industry_scores: List[IndustryScore],
    ) -> List[TechnologyIntelligence]:
        """Build TechnologyIntelligence objects from all components."""
        demand_map = {d.name: d for d in demand_scores}
        trend_map = {t.name: t for t in trend_metrics}
        industry_map = {s.name: s for s in industry_scores}

        intelligences = []
        for name in freq_inputs:
            freq = freq_inputs[name]
            demand = demand_map.get(name)
            trend = trend_map.get(name)
            industry = industry_map.get(name)

            intelligence = TechnologyIntelligence(
                name=name,
                demand_score=demand.demand_score if demand else 0,
                trend=trend.trend if trend else TrendDirection.STABLE,
                growth=trend.growth_rate if trend else 0,
                industry_score=industry.industry_score if industry else 0,
                classification=industry.classification if industry else TechnologyClassification.SUPPORTING,
                mentions=freq.mentions,
                percentage=freq.percentage,
                rank=freq.rank,
            )
            intelligences.append(intelligence)

        intelligences.sort(key=lambda t: t.industry_score, reverse=True)
        return intelligences

    def get_top_technologies(self, top_n: int = 10) -> List[TechnologyIntelligence]:
        """Get the top N technologies by industry score."""
        if not self.last_technologies:
            return []
        return self.last_technologies[:top_n]

    def get_emerging_technologies(self) -> List[TechnologyIntelligence]:
        """Get technologies classified as Emerging."""
        if not self.last_technologies:
            return []
        return [t for t in self.last_technologies if t.classification == TechnologyClassification.EMERGING]

    def get_core_technologies(self) -> List[TechnologyIntelligence]:
        """Get technologies classified as Core."""
        if not self.last_technologies:
            return []
        return [t for t in self.last_technologies if t.classification == TechnologyClassification.CORE]

    def get_tech_intelligence(self, name: str) -> Optional[TechnologyIntelligence]:
        """Get intelligence data for a specific technology."""
        if not self.last_technologies:
            return None
        for tech in self.last_technologies:
            if tech.name.lower() == name.lower():
                return tech
        return None

    def get_visualization_data(self) -> Optional[VisualizationData]:
        """Get pre-formatted visualization data."""
        if not self.last_technologies or not self.last_trend_metrics or not self.last_rankings:
            return None
        return self._report_generator.generate_visualization_data(
            technologies=self.last_technologies,
            trend_metrics=self.last_trend_metrics,
            rankings=self.last_rankings,
        )

    def export_report(self, output_path: Union[str, Path]) -> Path:
        """
        Export the most recent report to JSON file.
        
        Args:
            output_path: Path to write the JSON file.
        
        Returns:
            Path to the exported file.
        
        Raises:
            ExportError: If no report available or export fails.
        """
        if self.last_report is None:
            raise ExportError("No report to export. Run process() first.")
        return self._report_generator.export_report(self.last_report, output_path)

    def export_visualization_data(self, output_path: Union[str, Path]) -> Path:
        """
        Export visualization data to JSON file.
        
        Args:
            output_path: Path to write the JSON file.
        
        Returns:
            Path to the exported file.
        """
        viz_data = self.get_visualization_data()
        if viz_data is None:
            raise ExportError("No visualization data available. Run process() first.")

        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(viz_data.model_dump(), f, indent=2, default=str)
            logger.info("[DemandEngine] Exported visualization data to %s", path)
            return path
        except Exception as e:
            raise ExportError(f"Failed to export visualization data: {e}") from e

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics from the last analysis."""
        if not self.last_report:
            return {}
        return self.last_report.summary
