"""
Recommendation Service for Recommendation Intelligence Layer.
Master orchestrator service exposing end-to-end recommendation workflow APIs:
- generate_recommendations()
- get_recommendation()
- get_learning_path()
- get_evidence()
- export_report()
"""

from typing import Any, Dict, List, Optional
from backend.recommendation_engine.graph.graph_repository import GraphRepository
from backend.recommendation_engine.learning_path.learning_path_builder import LearningPathBuilder
from backend.recommendation_engine.learning_path.path_generator import LearningPathPlan
from backend.recommendation_engine.llm.gemini_client import GeminiClient
from backend.recommendation_engine.llm.recommendation_generator import LLMRecommendationGenerator
from backend.recommendation_engine.recommendation.recommendation_builder import RecommendationBuilder
from backend.recommendation_engine.recommendation.recommendation_models import RecommendationItem, RecommendationResultSet
from backend.recommendation_engine.report.json_export import JSONReportExporter
from backend.recommendation_engine.report.markdown_export import MarkdownReportExporter
from backend.recommendation_engine.report.pdf_export import PDFReportExporter
from backend.recommendation_engine.report.report_builder import ExecutiveReport, ReportBuilder
from backend.recommendation_engine.retrieval.ranking import RankedEvidence
from backend.recommendation_engine.retrieval.retrieval_service import RetrievalService
from backend.recommendation_engine.service.service_models import (
    ExportReportRequest,
    GenerateRecommendationsRequest,
    ServiceExecutionResponse,
)
from backend.recommendation_engine.service.service_validator import ServiceValidator
from backend.recommendation_engine.utils.logger import recommendation_logger_tagged


class RecommendationService:
    """
    Main entry point for Recommendation Intelligence Layer.
    Orchestrates Graph evidence retrieval, Prompt building, LLM generation,
    Recommendation formatting, Learning Path resolution, and Report exporting.
    """

    def __init__(
        self,
        repository: Optional[GraphRepository] = None,
        llm_client: Optional[GeminiClient] = None
    ):
        self.repo = repository or GraphRepository()
        self.retrieval_service = RetrievalService(self.repo)
        self.llm_generator = LLMRecommendationGenerator(llm_client)
        self.rec_builder = RecommendationBuilder()
        self.path_builder = LearningPathBuilder(self.repo)
        self.report_builder = ReportBuilder()

        # Cache active session data
        self._last_result_set: Optional[RecommendationResultSet] = None
        self._last_learning_path: Optional[LearningPathPlan] = None
        self._last_evidence: Optional[List[RankedEvidence]] = None
        self._last_report: Optional[ExecutiveReport] = None
        self._last_gap_data: Optional[Dict[str, Any]] = None

    def generate_recommendations(self, request: GenerateRecommendationsRequest) -> ServiceExecutionResponse:
        """
        Transform GapAnalysisResult into explainable, evidence-backed curriculum recommendations.
        """
        recommendation_logger_tagged.info("Executing generate_recommendations workflow...")

        validation = ServiceValidator.validate_generate_request(request)
        if not validation.is_valid:
            return ServiceExecutionResponse(
                success=False,
                message=f"Validation failed: {', '.join(validation.errors)}"
            )

        gap_data = request.gap_analysis_data
        self._last_gap_data = gap_data

        # Extract target gap technology names
        target_gaps = request.target_gaps or []
        if not target_gaps:
            raw_gaps = gap_data.get("gap", [])
            for g in raw_gaps:
                if isinstance(g, dict):
                    tech = g.get("industry_skill", g.get("industry_technology_id", g.get("technology", "")))
                else:
                    tech = str(g)
                if tech:
                    target_gaps.append(tech)

        if not target_gaps:
            # Default sample gaps if empty
            target_gaps = ["Redis", "Docker", "FastAPI", "Kubernetes"]

        # 1. Retrieve evidence strictly for target gaps
        evidence_items = self.retrieval_service.get_evidence_for_gaps(target_gaps)
        self._last_evidence = evidence_items

        evidence_dicts = [item.model_dump() for item in evidence_items]

        # 2. LLM Generation
        llm_out = self.llm_generator.generate_recommendations(
            gap_analysis_data=gap_data,
            evidence_data=evidence_dicts,
            knowledge_context=request.knowledge_context
        )

        # 3. Build Recommendation Result Set
        result_set = self.rec_builder.build_recommendations(
            llm_payload=llm_out["payload"],
            evidence_list=evidence_dicts
        )
        self._last_result_set = result_set

        # 4. Generate Dependency-Aware Learning Path
        rec_tech_list = [r.technology for r in result_set.recommendations]
        learning_path = self.path_builder.build_learning_path(rec_tech_list)
        self._last_learning_path = learning_path

        # 5. Build Executive Report
        report = self.report_builder.build_report(
            recommendation_result=result_set,
            learning_path_plan=learning_path,
            evidence_list=evidence_items,
            gap_analysis_data=gap_data
        )
        self._last_report = report

        recommendation_logger_tagged.info("End-to-End Recommendation Workflow completed successfully!")

        return ServiceExecutionResponse(
            success=True,
            message="Recommendations generated successfully",
            recommendations=result_set,
            learning_path=learning_path,
            evidence=evidence_items,
            report=report
        )

    def get_recommendation(self, tech_name_or_id: str) -> Optional[RecommendationItem]:
        """
        Get recommendation item by technology name.
        """
        if not self._last_result_set:
            return None
        for item in self._last_result_set.recommendations:
            if item.technology.lower() == tech_name_or_id.lower():
                return item
        return None

    def get_learning_path(self, target_technologies: Optional[List[str]] = None) -> LearningPathPlan:
        """
        Get dependency-aware learning path.
        """
        if target_technologies:
            return self.path_builder.build_learning_path(target_technologies)
        if self._last_learning_path:
            return self._last_learning_path
        # Default sample learning path
        return self.path_builder.build_learning_path(["Python", "SQL", "Docker", "Redis", "FastAPI", "Kubernetes", "Microservices"])

    def get_evidence(self, gap_technologies: Optional[List[str]] = None) -> List[RankedEvidence]:
        """
        Retrieve evidence items for gaps.
        """
        if gap_technologies:
            return self.retrieval_service.get_evidence_for_gaps(gap_technologies)
        if self._last_evidence:
            return self._last_evidence
        return self.retrieval_service.get_evidence_for_gaps(["Redis", "Docker", "FastAPI"])

    def export_report(self, request: ExportReportRequest) -> ServiceExecutionResponse:
        """
        Export generated report to JSON, Markdown, or PDF/HTML.
        """
        validation = ServiceValidator.validate_export_request(request)
        if not validation.is_valid:
            return ServiceExecutionResponse(
                success=False,
                message=f"Export validation error: {', '.join(validation.errors)}"
            )

        if not self._last_report:
            # Build fallback default report
            dummy_recs = self.rec_builder.build_recommendations(
                {"recommendations": [{"technology": "Redis", "priority": "High", "industry_score": 91, "reason": "High demand"}]},
                [{"tech_name": "Redis", "industry_score": 91}]
            )
            dummy_path = self.path_builder.build_learning_path(["Redis"])
            self._last_report = self.report_builder.build_report(dummy_recs, dummy_path, [])

        report_dict = self._last_report.model_dump()
        fmt = request.format.lower().strip()

        if fmt == "json":
            content = JSONReportExporter.export(report_dict, request.file_path)
        elif fmt == "markdown":
            content = MarkdownReportExporter.export(report_dict, request.file_path)
        elif fmt in ["pdf", "html"]:
            content = PDFReportExporter.export(report_dict, request.file_path)
        else:
            content = JSONReportExporter.export(report_dict, request.file_path)

        recommendation_logger_tagged.info(f"Report exported successfully in format: {fmt}")
        return ServiceExecutionResponse(
            success=True,
            message=f"Report exported successfully in {fmt} format",
            report=self._last_report,
            exported_content=content
        )
