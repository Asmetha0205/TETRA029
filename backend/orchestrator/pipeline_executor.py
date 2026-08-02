"""
Pipeline Executor.
Coordinates end-to-end multi-engine analysis execution with fault-tolerant fallbacks.
"""

import time
from typing import Any, Dict, Optional
from backend.gateway.academic_gateway import AcademicGateway
from backend.gateway.industry_gateway import IndustryGateway
from backend.gateway.semantic_gateway import SemanticGateway
from backend.gateway.recommendation_gateway import RecommendationGateway
from backend.events.event_bus import event_bus
from backend.events.event_models import EventType
from backend.monitoring.execution_timer import ExecutionTimer
from backend.monitoring.metrics import metrics_collector
from backend.orchestrator.execution_context import ExecutionContext
from backend.orchestrator.exceptions import PipelineExecutionError
from backend.utils.logger import get_logger

logger = get_logger("orchestrator.pipeline")


class PipelineExecutor:
    """Executes the analysis pipeline steps sequentially with resilient fallback policies."""

    def __init__(
        self,
        academic_gateway: Optional[AcademicGateway] = None,
        industry_gateway: Optional[IndustryGateway] = None,
        semantic_gateway: Optional[SemanticGateway] = None,
        recommendation_gateway: Optional[RecommendationGateway] = None,
    ):
        self.academic_gateway = academic_gateway or AcademicGateway()
        self.industry_gateway = industry_gateway or IndustryGateway()
        self.semantic_gateway = semantic_gateway or SemanticGateway()
        self.recommendation_gateway = recommendation_gateway or RecommendationGateway()

    def execute_pipeline(self, context: ExecutionContext) -> ExecutionContext:
        """Execute all engines sequentially with fallbacks."""
        logger.info("[Workflow] [Analysis: %s] Analysis Started", context.analysis_id)

        # ------------------------------------------------------------------
        # STAGE 1: Academic Engine
        # ------------------------------------------------------------------
        event_bus.publish(
            EventType.ACADEMIC_ANALYSIS_STARTED,
            {"message": "Starting Academic Parsing & Extraction"},
            analysis_id=context.analysis_id,
        )
        t0 = time.time()
        try:
            if not context.file_bytes:
                raise PipelineExecutionError("No file bytes provided for upload.")

            ac_res = self.academic_gateway.process_pdf(
                file_bytes=context.file_bytes,
                filename=context.filename,
                university_name=context.university_name,
                curriculum_year=context.curriculum_year,
                department=context.department,
            )
            context.document_id = ac_res["document_id"]
            context.academic_output = ac_res
            duration = round(time.time() - t0, 3)
            context.timings["upload_and_parsing_time"] = duration
            metrics_collector.record_timing("upload_time", duration)
            metrics_collector.record_timing("parsing_time", duration)

            event_bus.publish(
                EventType.ACADEMIC_ANALYSIS_COMPLETED,
                {"message": "Academic parsing and extraction completed successfully."},
                analysis_id=context.analysis_id,
            )
            logger.info("[Academic] Completed successfully in %.2fs", duration)
        except Exception as e:
            logger.error("[Academic] Failed: %s", e)
            context.errors.append(f"Academic Engine error: {e}")
            raise PipelineExecutionError(f"Academic Engine stage failed: {e}") from e

        # ------------------------------------------------------------------
        # STAGE 2: Industry Knowledge Lookup
        # ------------------------------------------------------------------
        t0 = time.time()
        try:
            ind_records = self.industry_gateway.get_all_technologies()
            ind_stats = self.industry_gateway.get_statistics()
            context.industry_output = {
                "records_count": len(ind_records),
                "statistics": ind_stats,
            }
            context.timings["industry_lookup_time"] = round(time.time() - t0, 3)
            logger.info("[Industry] Industry Knowledge Lookup complete (%d skills loaded)", len(ind_records))
        except Exception as e:
            logger.warning("[Industry] Industry lookup degraded: %s", e)
            context.warnings.append(f"Industry Engine lookup degraded: {e}")
            context.industry_output = {"records_count": 0, "statistics": {}}

        # ------------------------------------------------------------------
        # STAGE 3: Semantic Intelligence Engine
        # ------------------------------------------------------------------
        event_bus.publish(
            EventType.SEMANTIC_ANALYSIS_STARTED,
            {"message": "Comparing Academic vs Industry Skills"},
            analysis_id=context.analysis_id,
        )
        t0 = time.time()
        try:
            academic_records = context.academic_output.get("academic_records", [])
            sem_report = self.semantic_gateway.compare_curriculum(academic_records=academic_records)
            context.semantic_report = sem_report.model_dump()
            duration = round(time.time() - t0, 3)
            context.timings["semantic_matching_time"] = duration
            metrics_collector.record_timing("semantic_matching_time", duration)

            event_bus.publish(
                EventType.SEMANTIC_ANALYSIS_COMPLETED,
                {"message": "Semantic matching and gap analysis complete."},
                analysis_id=context.analysis_id,
            )
            logger.info("[Semantic] Comparison Complete in %.2fs", duration)
        except Exception as e:
            logger.error("[Semantic] Matcher failed: %s", e)
            context.errors.append(f"Semantic Engine error: {e}")
            raise PipelineExecutionError(f"Semantic Engine stage failed: {e}") from e

        # ------------------------------------------------------------------
        # STAGE 4: Recommendation Intelligence Layer
        # ------------------------------------------------------------------
        event_bus.publish(
            EventType.RECOMMENDATION_STARTED,
            {"message": "Generating evidence-backed recommendations"},
            analysis_id=context.analysis_id,
        )
        t0 = time.time()
        try:
            gap_data = context.semantic_report or {}
            rec_res = self.recommendation_gateway.generate_recommendations(
                gap_analysis_data=gap_data
            )
            if rec_res.success:
                context.recommendation_output = {
                    "recommendations": rec_res.recommendations.model_dump() if rec_res.recommendations else {},
                    "learning_path": rec_res.learning_path.model_dump() if rec_res.learning_path else {},
                    "evidence": [e.model_dump() for e in (rec_res.evidence or [])],
                    "report": rec_res.report.model_dump() if rec_res.report else {},
                }
            else:
                logger.warning("[Recommendation] Failed: %s. Using partial fallbacks.", rec_res.message)
                context.warnings.append(f"Recommendation Engine partial fallback: {rec_res.message}")
                context.recommendation_output = self._create_fallback_recommendations(gap_data)

            duration = round(time.time() - t0, 3)
            context.timings["recommendation_time"] = duration
            metrics_collector.record_timing("recommendation_time", duration)

            event_bus.publish(
                EventType.RECOMMENDATION_COMPLETED,
                {"message": "Recommendations generated successfully."},
                analysis_id=context.analysis_id,
            )
            logger.info("[Recommendation] Generated in %.2fs", duration)
        except Exception as e:
            logger.warning("[Recommendation] Recommendation engine failed gracefully: %s", e)
            context.warnings.append(f"Recommendation Engine exception: {e}")
            context.recommendation_output = self._create_fallback_recommendations(context.semantic_report or {})

        # ------------------------------------------------------------------
        # STAGE 5: Report Generation & Completion
        # ------------------------------------------------------------------
        event_bus.publish(
            EventType.REPORT_GENERATED,
            {"message": "Report generation finished."},
            analysis_id=context.analysis_id,
        )
        event_bus.publish(
            EventType.ANALYSIS_COMPLETED,
            {"message": "Curriculum analysis pipeline completed successfully."},
            analysis_id=context.analysis_id,
        )
        logger.info("[Report] Completed")
        return context

    @staticmethod
    def _create_fallback_recommendations(gap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate safe fallback recommendations when recommendation engine errors out."""
        raw_gaps = gap_data.get("gap", [])
        gap_items = []
        for g in raw_gaps[:5]:
            tech = g.get("industry_skill", "Key Industry Tech") if isinstance(g, dict) else str(g)
            gap_items.append({
                "recommendation_id": f"rec-fallback-{tech.lower().replace(' ', '-')}",
                "technology": tech,
                "action": f"Integrate {tech} module into foundational curriculum",
                "priority": "HIGH",
                "target_courses": ["CS101 Core Syllabus"],
                "reasoning": f"Critical industry gap identified for {tech} with high market demand.",
            })

        return {
            "recommendations": {"recommendations": gap_items},
            "learning_path": {
                "phases": [
                    {
                        "phase": 1,
                        "title": "Foundational Tech Integration",
                        "technologies": [item["technology"] for item in gap_items[:2]],
                    }
                ]
            },
            "evidence": [],
            "report": {"executive_summary": "Partial report generated based on gap analysis."},
        }
