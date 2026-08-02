"""
Report Generator for the CurricuAlign AI Technology Frequency Analysis Engine.

Produces the FrequencyReport envelope, persistent reports, and human-readable
summaries of technology distributions.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from backend.industry_engine.analysis.frequency.config import FrequencyConfig
from backend.industry_engine.analysis.frequency.models import (
    CategoryFrequency,
    FrequencyReport,
    FrequencyStatistics,
    RoleFrequency,
    TechnologyFrequency,
)

logger = logging.getLogger("industry_engine.analysis.frequency.report_generator")


class ReportGenerator:
    """
    Assembles the final FrequencyReport and supports file export.
    """

    def __init__(self, config: FrequencyConfig) -> None:
        self._config = config

    def generate(
        self,
        technology_frequencies: List[TechnologyFrequency],
        category_frequencies: List[CategoryFrequency],
        role_frequencies: List[RoleFrequency],
        statistics: FrequencyStatistics,
        total_jobs: int,
    ) -> FrequencyReport:
        """
        Build the complete FrequencyReport.
        """
        unique_techs = statistics.total_unique_technologies
        average_per_job = statistics.average_technologies_per_job

        return FrequencyReport(
            summary={
                "total_jobs": total_jobs,
                "unique_technologies": unique_techs,
                "average_technologies_per_job": average_per_job,
            },
            technologies=technology_frequencies,
            categories=category_frequencies,
            roles=role_frequencies,
            statistics=statistics,
        )

    def generate_technology_technical_report(self, technology_frequencies: List[TechnologyFrequency]) -> str:
        """
        Generate a plain-text list of all technologies sorted by rank.
        """
        lines = ["Technology Frequency Report", "=" * 40, ""]
        lines.append(f"{'Rank':<6} {'Technology':<30} {'Category':<25} {'Mentions':<10} {'Jobs':<8} {'%':>6}")
        lines.append("-" * 100)
        for freq in technology_frequencies:
            lines.append(
                f"{freq.rank:<6} {freq.name:<30} {freq.category:<25} "
                f"{freq.mentions:<10} {freq.unique_jobs:<8} {freq.percentage:>5.1f}%"
            )
        return "\n".join(lines)

    def generate_category_distribution_report(
        self,
        category_frequencies: List[CategoryFrequency],
    ) -> str:
        """Generate a text report of category distributions."""
        lines = ["Category Distribution Report", "=" * 40, ""]
        lines.append(f"{'Category':<30} {'Mentions':<12} {'Unique Techs':<14} {'Jobs':<8}")
        lines.append("-" * 70)
        for cf in category_frequencies:
            lines.append(
                f"{cf.category:<30} {cf.mentions:<12} {cf.unique_technologies:<14} {cf.unique_jobs:<8}"
            )
        return "\n".join(lines)

    def generate_top_technology_report(self, statistics: FrequencyStatistics) -> str:
        """Generate a top-N technology summary report."""
        lines = [f"Top {self._config.top_n_limit} Technologies", "=" * 40, ""]
        for tech in statistics.top_technologies:
            lines.append(f"- {tech.name} ({tech.category}): {tech.mentions} mentions, {tech.percentage}%")
        if statistics.top_per_category:
            lines.append("")
            lines.append("Top Per Category")
            lines.append("=" * 20)
            for cat, techs in statistics.top_per_category.items():
                if techs:
                    lines.append(f"\n{cat}:")
                    for t in techs:
                        lines.append(f"  - {t.name}: {t.mentions} mentions")
        return "\n".join(lines)

    def generate_role_technology_report(self, role_frequencies: List[RoleFrequency]) -> str:
        """Generate a per-role technology distribution report."""
        lines = ["Role Technology Report", "=" * 30, ""]
        for rf in role_frequencies:
            lines.append(f"Role: {rf.role} (Jobs: {rf.job_count})")
            for rt in rf.top_technologies:
                lines.append(f"  - {rt.technology}: {rt.percentage}%")
            lines.append("")
        return "\n".join(lines)

    def export_report(self, report: FrequencyReport, output_path: Path) -> None:
        """Export the full FrequencyReport envelope to a JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)
        logger.info(f"[ReportGenerator] Report exported to '{output_path}'.")

    def write_summary(self, summary: Dict[str, Any]) -> str:
        """Return a human-readable summary string."""
        return (
            f"Frequency Analysis Summary\n"
            f"  Total jobs:          {summary.get('total_jobs', 0)}\n"
            f"  Unique technologies: {summary.get('unique_technologies', 0)}\n"
            f"  Avg techs per job:   {summary.get('average_technologies_per_job', 0)}"
        )