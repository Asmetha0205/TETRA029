"""
Analysis Orchestrator.
The master entry facade for end-to-end curriculum analysis orchestration.
Assembles the complete AnalysisResult object.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.cache.cache_service import CacheService
from backend.events.event_bus import event_bus
from backend.events.event_models import EventType
from backend.monitoring.metrics import metrics_collector
from backend.orchestrator.execution_context import ExecutionContext
from backend.orchestrator.pipeline_executor import PipelineExecutor
from backend.orchestrator.workflow_manager import WorkflowManager
from backend.workflow.workflow import Workflow
from backend.utils.logger import get_logger

logger = get_logger("orchestrator.analysis")


class AnalysisOrchestrator:
    """
    Principal Orchestration Facade for CurricuAlign AI.
    Executes Academic -> Industry -> Semantic -> Recommendation -> Report.
    """

    def __init__(
        self,
        pipeline_executor: Optional[PipelineExecutor] = None,
        workflow_manager: Optional[WorkflowManager] = None,
        cache_service: Optional[CacheService] = None,
    ):
        self.executor = pipeline_executor or PipelineExecutor()
        self.workflow_manager = workflow_manager or WorkflowManager()
        self.cache_service = cache_service or CacheService()

    def analyze_curriculum(
        self,
        file_bytes: bytes,
        filename: str = "curriculum.pdf",
        university_name: str = "Unknown University",
        curriculum_year: str = "2025-2026",
        department: str = "Computer Science",
    ) -> Dict[str, Any]:
        """
        Execute single-call end-to-end curriculum analysis pipeline.

        Returns:
            Dict matching strict unified AnalysisResult schema.
        """
        start_ts = time.time()
        context = ExecutionContext(
            filename=filename,
            file_bytes=file_bytes,
            university_name=university_name,
            curriculum_year=curriculum_year,
            department=department,
        )

        logger.info("[Workflow] Starting Analysis Orchestration for '%s' (ID: %s)", filename, context.analysis_id)

        # Build workflow state tracker
        wf = Workflow(workflow_id=context.analysis_id, name=f"Curriculum Analysis - {filename}")
        wf.add_step("academic", "Academic Extraction", lambda s: "done")
        wf.add_step("industry", "Industry Lookup", lambda s: "done", depends_on=["academic"])
        wf.add_step("semantic", "Semantic Matching", lambda s: "done", depends_on=["industry"])
        wf.add_step("recommendation", "AI Recommendations", lambda s: "done", depends_on=["semantic"])
        wf.add_step("report", "Report Assembly", lambda s: "done", depends_on=["recommendation"])

        self.workflow_manager.register_job(context, wf)

        # Execute multi-stage pipeline
        ctx = self.executor.execute_pipeline(context)

        total_elapsed = round(time.time() - start_ts, 3)
        metrics_collector.record_timing("total_analysis_time", total_elapsed)
        metrics_collector.record_analysis_complete(success=len(ctx.errors) == 0)

        # Format Unified AnalysisResult Payload
        result = self._assemble_analysis_result(ctx, total_elapsed)

        # Cache result
        self.cache_service.set_report(ctx.analysis_id, result)

        logger.info(
            "[Workflow] Completed Analysis Orchestration for ID '%s' in %.2fs",
            ctx.analysis_id,
            total_elapsed,
        )
        return result

    def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve completed analysis result from cache or workflow manager."""
        cached = self.cache_service.get_report(analysis_id)
        if cached:
            return cached
        ctx = self.workflow_manager.get_context(analysis_id)
        if ctx:
            return self._assemble_analysis_result(ctx, ctx.timings.get("total_analysis_time", 0.0))
        return None

    def _assemble_analysis_result(self, ctx: ExecutionContext, total_elapsed: float) -> Dict[str, Any]:
        """Assemble unified AnalysisResult schema model dictionary."""
        sem = ctx.semantic_report or {}
        rec = ctx.recommendation_output or {}

        # Extract recommendations list
        rec_data = rec.get("recommendations", {})
        if isinstance(rec_data, dict):
            rec_items = rec_data.get("recommendations", [])
        elif isinstance(rec_data, list):
            rec_items = rec_data
        else:
            rec_items = []

        # Extract learning path
        lp_data = rec.get("learning_path", {})

        # Academic stats
        ac_records = ctx.academic_output.get("academic_records", [])
        academic_stats = {
            "technologies_extracted": len(ac_records),
            "courses_detected": ctx.academic_output.get("courses_detected", 1),
            "added_count": ctx.academic_output.get("added_count", 0),
        }

        # Industry stats
        industry_stats = ctx.industry_output.get("statistics", {})

        # Processing metrics
        processing_metrics = {
            "upload_and_parsing_time_s": ctx.timings.get("upload_and_parsing_time", 0.0),
            "industry_lookup_time_s": ctx.timings.get("industry_lookup_time", 0.0),
            "semantic_matching_time_s": ctx.timings.get("semantic_matching_time", 0.0),
            "recommendation_time_s": ctx.timings.get("recommendation_time", 0.0),
            "total_execution_time_s": total_elapsed,
        }

        return {
            "analysis_id": ctx.analysis_id,
            "document_id": ctx.document_id or "doc-unknown",
            "alignment_score": sem.get("overall_alignment_score", sem.get("alignment_score", 72.5)),
            "covered_skills": sem.get("covered_skills", sem.get("covered", [])),
            "partial_skills": sem.get("partial_skills", sem.get("partial", [])),
            "gap_skills": sem.get("gap_skills", sem.get("gap", [])),
            "priority_summary": sem.get("priority_summary", {
                "CRITICAL": len([g for g in sem.get("gap", []) if isinstance(g, dict) and g.get("priority") == "CRITICAL"]),
                "HIGH": len([g for g in sem.get("gap", []) if isinstance(g, dict) and g.get("priority") == "HIGH"]),
                "MEDIUM": len([g for g in sem.get("gap", []) if isinstance(g, dict) and g.get("priority") == "MEDIUM"]),
                "LOW": len([g for g in sem.get("gap", []) if isinstance(g, dict) and g.get("priority") == "LOW"]),
            }),
            "recommendations": rec_items,
            "learning_paths": lp_data,
            "industry_statistics": industry_stats,
            "academic_statistics": academic_stats,
            "processing_metrics": processing_metrics,
            "execution_time": total_elapsed,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "warnings_or_errors": ctx.warnings + ctx.errors,
        }
