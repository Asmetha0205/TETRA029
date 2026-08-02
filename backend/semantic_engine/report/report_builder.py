"""
Report Builder for CurricuAlign AI Semantic Intelligence Engine.

Builds complete SemanticComparisonReport objects, formatted JSON results,
and visualization data structures (Coverage Pie Chart, Gap Bar Chart, Alignment Gauge,
Radar Chart, Category Heatmap, Skill Network, Trend Overlay).
"""

import logging
from typing import Any, Dict, List, Optional

from backend.semantic_engine.config.config import SemanticEngineConfig
from backend.semantic_engine.models.semantic_models import (
    CategoryAlignment,
    CoverageClassificationEnum,
    SemanticComparisonReport,
    SkillMatchResult,
)
from backend.semantic_engine.report.alignment_score import AlignmentScoreCalculator
from backend.semantic_engine.report.statistics import SemanticStatisticsEngine
from backend.semantic_engine.report.summary_generator import ExecutiveSummaryGenerator

logger = logging.getLogger("semantic_engine.report.report_builder")


class SemanticReportBuilder:
    """Builds complete alignment reports and visualization data structures."""

    def __init__(self, config: Optional[SemanticEngineConfig] = None) -> None:
        self.config = config or SemanticEngineConfig()
        self.score_calculator = AlignmentScoreCalculator(config=self.config)

    def build_report(self, match_results: List[SkillMatchResult]) -> SemanticComparisonReport:
        """
        Build full SemanticComparisonReport model.

        Returns:
            SemanticComparisonReport model.
        """
        alignment_score = self.score_calculator.calculate_overall_alignment(match_results)
        category_alignments = self.score_calculator.calculate_category_alignments(match_results)
        stats = SemanticStatisticsEngine.compute_statistics(match_results)

        covered_list = []
        partial_list = []
        gap_list = []

        for item in match_results:
            d = {
                "academic_skill": item.academic_skill or "N/A",
                "industry_skill": item.industry_skill,
                "similarity": item.similarity,
                "priority": item.priority.value,
                "category": item.category,
                "industry_score": item.industry_score,
                "evidence": item.evidence.summary,
            }
            if item.classification == CoverageClassificationEnum.COVERED:
                covered_list.append(d)
            elif item.classification == CoverageClassificationEnum.PARTIAL:
                partial_list.append(d)
            else:
                gap_list.append(d)

        # Build visualization data structures
        viz_data = self._build_visualization_data(
            alignment_score=alignment_score,
            stats=stats,
            category_alignments=category_alignments,
            match_results=match_results,
        )

        report = SemanticComparisonReport(
            alignment_score=alignment_score,
            statistics={"covered": stats["covered"], "partial": stats["partial"], "gap": stats["gap"]},
            covered=covered_list,
            partial=partial_list,
            gap=gap_list,
            category_alignment=category_alignments,
            visualization_data=viz_data,
        )

        logger.info("[Report] Semantic Comparison Report generated (Score: %.1f).", alignment_score)
        return report

    def _build_visualization_data(
        self,
        alignment_score: float,
        stats: Dict[str, Any],
        category_alignments: Dict[str, CategoryAlignment],
        match_results: List[SkillMatchResult],
    ) -> Dict[str, Any]:
        """
        Generate visualization data structures for charts & dashboards.
        """
        # 1. Coverage Pie Chart
        coverage_pie = [
            {"label": "Covered", "value": stats["covered"], "color": "#10B981"},
            {"label": "Partial", "value": stats["partial"], "color": "#F59E0B"},
            {"label": "Gap", "value": stats["gap"], "color": "#EF4444"},
        ]

        # 2. Gap Bar Chart
        gaps = [m for m in match_results if m.classification == CoverageClassificationEnum.GAP]
        gaps_sorted = sorted(gaps, key=lambda x: x.industry_score, reverse=True)[:10]
        gap_bar_chart = [
            {"skill": g.industry_skill, "industry_score": g.industry_score, "priority": g.priority.value}
            for g in gaps_sorted
        ]

        # 3. Alignment Gauge
        alignment_gauge = {
            "score": alignment_score,
            "min": 0.0,
            "max": 100.0,
            "status": "High" if alignment_score >= 80 else ("Medium" if alignment_score >= 60 else "Low"),
        }

        # 4. Radar Chart
        radar_chart = [
            {"category": cat_name, "score": cat.alignment_score}
            for cat_name, cat in category_alignments.items()
        ]

        # 5. Category Heatmap
        category_heatmap = [
            {
                "category": cat_name,
                "covered": cat.covered_count,
                "partial": cat.partial_count,
                "gap": cat.gap_count,
                "score": cat.alignment_score,
            }
            for cat_name, cat in category_alignments.items()
        ]

        # 6. Skill Network Nodes & Edges
        nodes = []
        edges = []
        for i, item in enumerate(match_results[:15]):
            nodes.append({"id": f"node-{i}", "label": item.industry_skill, "category": item.category})
            if item.academic_skill:
                edges.append({"source": f"academic-{item.academic_skill}", "target": f"node-{i}", "similarity": item.similarity})

        skill_network = {"nodes": nodes, "edges": edges}

        # 7. Trend Overlay
        trend_overlay = [
            {"skill": item.industry_skill, "industry_score": item.industry_score, "demand_score": item.demand_score}
            for item in match_results[:10]
        ]

        return {
            "coverage_pie_chart": coverage_pie,
            "gap_bar_chart": gap_bar_chart,
            "alignment_gauge": alignment_gauge,
            "radar_chart": radar_chart,
            "category_heatmap": category_heatmap,
            "skill_network": skill_network,
            "trend_overlay": trend_overlay,
        }
