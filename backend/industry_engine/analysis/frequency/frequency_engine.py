"""
Frequency Engine for the CurricuAlign AI Technology Frequency Analysis Engine.

Orchestrates the full analysis pipeline:

    [Normalized Technology Profiles]
        -> Validator
        -> Aggregator (Frequency Counter + Category Counter + Role Counter)
        -> Statistics Generator
        -> Report Generator
        -> FrequencyReport
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from backend.industry_engine.analysis.frequency.aggregator import Aggregator
from backend.industry_engine.analysis.frequency.config import FrequencyConfig
from backend.industry_engine.analysis.frequency.exceptions import (
    DuplicateJobError,
    EmptyDatasetError,
    FrequencyAnalysisError,
    InvalidInputError,
    MalformedRecordError,
)
from backend.industry_engine.analysis.frequency.models import (
    JobTechnologyRecord,
    FrequencyReport,
)
from backend.industry_engine.analysis.frequency.report_generator import ReportGenerator
from backend.industry_engine.analysis.frequency.statistics import StatisticsGenerator
from backend.industry_engine.processing.normalization.models import NormalizationResult

logger = logging.getLogger("industry_engine.analysis.frequency.frequency_engine")


class FrequencyEngine:
    """
    Complete frequency analysis engine for normalized technology profiles.
    """

    def __init__(self, config: Optional[FrequencyConfig] = None) -> None:
        """
        Initialize the engine.

        Args:
            config: Optional FrequencyConfig to tune behavior.
        """
        self._config = config or FrequencyConfig()
        self._aggregator = Aggregator(config=self._config)
        self._statistics = StatisticsGenerator(config=self._config)
        self._reporter = ReportGenerator(config=self._config)
        self.last_report: Optional[FrequencyReport] = None
        logger.info("[FrequencyEngine] Initialized Technology Frequency Analysis Engine.")

    def process(
        self,
        data: Union[
            List[JobTechnologyRecord],
            List[Dict[str, Any]],
            List[NormalizationResult],
        ],
    ) -> FrequencyReport:
        """
        Execute the full frequency analysis pipeline.

        Args:
            data: A list of JobTechnologyRecords, raw dicts in the spec format,
                or NormalizationResult objects from Phase 3.5.

        Returns:
            A populated FrequencyReport.

        Raises:
            EmptyDatasetError: If the input list is empty.
            InvalidInputError: If the input shape is unsupported.
        """
        if not data:
            raise EmptyDatasetError("Frequency analysis requires at least one job record.")

        records = self._normalize_input(data)
        total_time_start = time.time()

        self._aggregator.process_batch(records)

        tech_freqs, cat_freqs, role_freqs, total_jobs, raw_records = self._aggregator.process()

        raw_for_stats = raw_records if self._config.compute_combination_statistics else None
        stats = self._statistics.compute(
            technology_frequencies=tech_freqs,
            category_frequencies=cat_freqs,
            total_jobs=total_jobs,
            optional_records=raw_for_stats,
        )

        report = self._reporter.generate(
            technology_frequencies=tech_freqs,
            category_frequencies=cat_freqs,
            role_frequencies=role_freqs,
            statistics=stats,
            total_jobs=total_jobs,
        )
        self.last_report = report

        elapsed_ms = round((time.time() - total_time_start) * 1000, 2)
        logger.info(
            f"[FrequencyEngine] Analysis complete: {total_jobs} jobs, "
            f"{report.summary['unique_technologies']} unique techs, "
            f"{len(report.categories)} categories, "
            f"{len(report.roles)} roles in {elapsed_ms}ms."
        )
        return report

    def analyze_json(self, raw_json: str) -> FrequencyReport:
        """
        Process a raw JSON string payload.

        Raises:
            InvalidInputError: If the payload is not valid JSON or not a list.
        """
        try:
            data = json.loads(raw_json)
        except (json.JSONDecodeError, TypeError) as exc:
            raise InvalidInputError(f"Failed to parse frequency analysis input JSON: {exc}") from exc
        if not isinstance(data, list):
            raise InvalidInputError(
                f"Frequency analysis input must be a JSON array, got {type(data).__name__}."
            )
        return self.process(data)

    def export_report(self, output_path: Union[str, Path]) -> Path:
        """
        Export the most recent report to a JSON file.
        """
        if self.last_report is None:
            raise FrequencyAnalysisError("No report to export. Run process() first.")
        path = Path(output_path)
        self._reporter.export_report(self.last_report, path)
        return path

    def write_report(self, output_path: Union[str, Path]) -> Path:
        """Alias for export_report."""
        return self.export_report(output_path)

    def _normalize_input(self, data: List[Any]) -> List[JobTechnologyRecord]:
        """
        Coerce a supported input shape into a list of JobTechnologyRecords.
        """
        result: List[JobTechnologyRecord] = []
        seen_ids: set = set()

        for item in data:
            if isinstance(item, JobTechnologyRecord):
                record = item
            elif isinstance(item, dict):
                record = self._dict_to_record(item)
            elif isinstance(item, NormalizationResult):
                record = self._normalization_result_to_record(item)
            else:
                raise InvalidInputError(
                    f"Unsupported record type: {type(item).__name__}. "
                    "Expected JobTechnologyRecord, dict, or NormalizationResult."
                )

            if record.job_id in seen_ids:
                raise DuplicateJobError(
                    f"Duplicate job_id '{record.job_id}' detected in the input."
                )
            seen_ids.add(record.job_id)
            result.append(record)

        return result

    def _dict_to_record(self, item: Dict[str, Any]) -> JobTechnologyRecord:
        """
        Convert a raw dict to a JobTechnologyRecord.

        Supports both the spec format ({job_id, technologies}) and the
        NormalizationResult dict format ({job_id, ...other...}).
        """
        job_id = str(item.get("job_id", "")).strip()
        if not job_id:
            raise MalformedRecordError(f"Record missing job_id: {item!r}")

        technologies = {}
        if "technologies" in item and isinstance(item["technologies"], dict):
            technologies = item["technologies"]
        elif "normalized" in item:
            technologies = self._technologies_from_normalized_dict(item["normalized"])

        if not technologies:
            for key, value in item.items():
                if key in ("job_id", "normalized", "unknown", "rejected", "report"):
                    continue
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, list):
                            technologies[sub_key] = sub_value
            if not technologies:
                technologies = {}

        role = item.get("role") or item.get("title") or item.get("job_title", "")

        return JobTechnologyRecord(
            job_id=job_id,
            technologies=technologies,
            role=str(role) if role else None,
            metadata={k: v for k, v in item.items() if k not in ("job_id", "technologies", "role", "title")},
        )

    @staticmethod
    def _technologies_from_normalized_dict(normalized: List[Dict]) -> Dict[str, List[str]]:
        """Extract technologies from a normalized dict list."""
        categories = {}
        for entry in normalized:
            tech_name = entry.get("canonical_name", "")
            tech_category = entry.get("category", "Unknown")
            if tech_category not in categories:
                categories[tech_category] = []
            categories[tech_category].append(tech_name)
        return categories

    def _normalization_result_to_record(self, result_item: NormalizationResult) -> JobTechnologyRecord:
        """
        Convert a NormalizationResult to a JobTechnologyRecord.

        The NormalizationResult contains normalized_t list of NormalizedTechnology.
        """
        record = result_item.model_dump()
        job_id = record.get("job_id", "")
        if not job_id:
            job_id = f"result-{id(result_item)}"

        categories = {}
        for tech in result_item.normalized:
            cat = tech.category or "Unknown"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tech.canonical_name)

        return JobTechnologyRecord(
            job_id=job_id,
            technologies=categories,
            role=None,
            metadata=record.get("report", {}),
        )