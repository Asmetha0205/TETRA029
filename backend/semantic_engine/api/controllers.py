"""
API Controllers for Semantic REST API.
"""

import logging
from typing import Any, Dict, List, Optional

from backend.semantic_engine.api.schemas import ComparisonReportResponse, SkillMatchResponseItem
from backend.semantic_engine.service.semantic_service import SemanticService

logger = logging.getLogger("semantic_engine.api.controllers")


class SemanticController:
    """Controller mapping HTTP endpoints to SemanticService methods."""

    def __init__(self, service: SemanticService) -> None:
        self.service = service

    def compare_curriculum(self) -> ComparisonReportResponse:
        logger.info("[API] POST /semantic/compare")
        report = self.service.compare_curriculum()
        return self._report_to_schema(report)

    def get_gaps(self) -> List[SkillMatchResponseItem]:
        logger.info("[API] GET /semantic/gaps")
        gaps = self.service.find_gaps()
        return [self._dict_to_item_schema(g) for g in gaps]

    def get_covered(self) -> List[SkillMatchResponseItem]:
        logger.info("[API] GET /semantic/covered")
        covered = self.service.get_covered()
        return [self._dict_to_item_schema(c) for c in covered]

    def get_partial(self) -> List[SkillMatchResponseItem]:
        logger.info("[API] GET /semantic/partial")
        partial = self.service.get_partial()
        return [self._dict_to_item_schema(p) for p in partial]

    def get_statistics(self) -> Dict[str, Any]:
        logger.info("[API] GET /semantic/statistics")
        return self.service.get_statistics()

    def get_report(self) -> ComparisonReportResponse:
        logger.info("[API] GET /semantic/report")
        report = self.service.generate_alignment_report()
        return self._report_to_schema(report)

    def search_similar(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        logger.info("[API] GET /semantic/search?q=%s", query)
        return self.service.search_similar(query=query, limit=limit)

    @staticmethod
    def _report_to_schema(report: Any) -> ComparisonReportResponse:
        cov_items = [SemanticController._dict_to_item_schema(c) for c in report.covered]
        part_items = [SemanticController._dict_to_item_schema(p) for p in report.partial]
        gap_items = [SemanticController._dict_to_item_schema(g) for g in report.gap]

        return ComparisonReportResponse(
            alignment_score=report.alignment_score,
            statistics=report.statistics,
            covered=cov_items,
            partial=part_items,
            gap=gap_items,
            visualization_data=report.visualization_data,
        )

    @staticmethod
    def _dict_to_item_schema(d: Dict[str, Any]) -> SkillMatchResponseItem:
        return SkillMatchResponseItem(
            academic_skill=d.get("academic_skill"),
            industry_skill=d.get("industry_skill", ""),
            similarity=float(d.get("similarity", 0.0)),
            priority=d.get("priority"),
            industry_score=float(d.get("industry_score", 0.0)),
            category=d.get("category", "General"),
            evidence=d.get("evidence"),
        )
