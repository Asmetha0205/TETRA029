"""
Refresh Pipeline for CurricuAlign AI Industry Intelligence Engine.

Orchestrates the complete 9-stage end-to-end pipeline:
Raw Jobs -> Cleaning -> Normalization -> Frequency -> Demand -> Knowledge Layer -> Embeddings -> ChromaDB -> Snapshot.
"""

import time
import logging
from typing import Any, Dict, List, Optional, Tuple

from backend.industry_engine.models.job import Job
from backend.industry_engine.processing.pipeline import JobPreprocessingPipeline
from backend.industry_engine.processing.normalization.pipeline import NormalizationPipeline
from backend.industry_engine.processing.normalization.models import TechnologyProfile
from backend.industry_engine.analysis.frequency.frequency_engine import FrequencyEngine
from backend.industry_engine.analysis.frequency.models import JobTechnologyRecord
from backend.industry_engine.analysis.demand.demand_engine import DemandEngine
from backend.industry_engine.knowledge.knowledge_service import KnowledgeService
from backend.industry_engine.embeddings.embedding_service import EmbeddingService
from backend.industry_engine.chromadb.sync_service import ChromaSyncService

logger = logging.getLogger("industry_engine.scheduler.refresh_pipeline")


class RefreshSummaryReport:
    """Summary report detailing the execution metrics of a refresh run."""

    def __init__(
        self,
        run_id: str,
        success: bool = True,
        raw_jobs_count: int = 0,
        clean_jobs_count: int = 0,
        normalized_count: int = 0,
        knowledge_created: int = 0,
        knowledge_updated: int = 0,
        embeddings_generated: int = 0,
        chroma_synced: int = 0,
        snapshot_id: Optional[str] = None,
        error_message: Optional[str] = None,
        execution_time_seconds: float = 0.0,
    ) -> None:
        self.run_id = run_id
        self.success = success
        self.raw_jobs_count = raw_jobs_count
        self.clean_jobs_count = clean_jobs_count
        self.normalized_count = normalized_count
        self.knowledge_created = knowledge_created
        self.knowledge_updated = knowledge_updated
        self.embeddings_generated = embeddings_generated
        self.chroma_synced = chroma_synced
        self.snapshot_id = snapshot_id
        self.error_message = error_message
        self.execution_time_seconds = execution_time_seconds

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "success": self.success,
            "raw_jobs_count": self.raw_jobs_count,
            "clean_jobs_count": self.clean_jobs_count,
            "normalized_count": self.normalized_count,
            "knowledge_created": self.knowledge_created,
            "knowledge_updated": self.knowledge_updated,
            "embeddings_generated": self.embeddings_generated,
            "chroma_synced": self.chroma_synced,
            "snapshot_id": self.snapshot_id,
            "error_message": self.error_message,
            "execution_time_seconds": self.execution_time_seconds,
        }


class RefreshPipeline:
    """
    Executes the end-to-end refresh workflow across all Industry Engine components.
    """

    def __init__(
        self,
        knowledge_service: KnowledgeService,
        embedding_service: EmbeddingService,
        chroma_sync_service: Optional[ChromaSyncService] = None,
    ) -> None:
        """
        Initialize the Refresh Pipeline with connected services.

        Args:
            knowledge_service: KnowledgeService instance.
            embedding_service: EmbeddingService instance.
            chroma_sync_service: Optional ChromaSyncService instance.
        """
        self.knowledge_service = knowledge_service
        self.embedding_service = embedding_service
        self.chroma_sync_service = chroma_sync_service

        self.preprocessing_pipeline = JobPreprocessingPipeline()
        self.normalization_pipeline = NormalizationPipeline()
        self.frequency_engine = FrequencyEngine()
        self.demand_engine = DemandEngine()

    def run_refresh(
        self,
        raw_jobs: Optional[List[Job]] = None,
        source_name: str = "pipeline_refresh",
        dry_run: bool = False,
    ) -> RefreshSummaryReport:
        """
        Run the end-to-end refresh pipeline.

        Args:
            raw_jobs: Optional list of Job postings. If None, uses default mock dataset.
            source_name: Name identifier for the refresh run.
            dry_run: If True, executes processing without saving persistent state.

        Returns:
            RefreshSummaryReport detailing pipeline metrics.
        """
        start_time = time.time()
        run_id = f"refresh-{int(start_time)}"
        logger.info("[Industry] Refresh Started (run_id='%s', dry_run=%s)", run_id, dry_run)

        jobs_list = raw_jobs or self._create_default_raw_jobs()
        raw_count = len(jobs_list)

        try:
            # Step 1 & 2: Clean jobs
            clean_jobs, _ = self.preprocessing_pipeline.process_jobs(jobs_list)
            clean_count = len(clean_jobs)

            # Step 3 & 4: Normalize extractions
            profiles = self._extract_profiles_from_clean_jobs(clean_jobs)
            combined_categories: Dict[str, List[Any]] = {}
            for p in profiles:
                for cat, vals in p.categories.items():
                    combined_categories.setdefault(cat, []).extend(vals)
            combined_profile = TechnologyProfile(categories=combined_categories)
            norm_result = self.normalization_pipeline.normalize(combined_profile)
            norm_count = len(norm_result.normalized)

            # Step 5: Frequency analysis
            freq_job_records = self._convert_clean_jobs_to_freq_records(clean_jobs, norm_result)
            freq_report = self.frequency_engine.process(freq_job_records)

            # Step 6: Demand analysis
            industry_report = self.demand_engine.process_from_frequency_report(freq_report.model_dump())

            if dry_run:
                elapsed = round(time.time() - start_time, 4)
                logger.info("[Industry] Refresh Dry-Run Completed in %.2fs.", elapsed)
                return RefreshSummaryReport(
                    run_id=run_id,
                    success=True,
                    raw_jobs_count=raw_count,
                    clean_jobs_count=clean_count,
                    normalized_count=norm_count,
                    execution_time_seconds=elapsed,
                )

            # Step 7: Knowledge Layer Update
            created, updated, snapshot = self.knowledge_service.ingest_pipeline_outputs(
                normalized_techs=norm_result,
                frequency_data=freq_report,
                demand_data=industry_report,
                source=source_name,
                auto_snapshot=True,
            )

            # Step 8: Embedding Generation
            batch_emb_res = self.embedding_service.generate_all_from_knowledge()
            emb_count = batch_emb_res.generated_count

            # Step 9: ChromaDB Synchronization
            chroma_count = 0
            if self.chroma_sync_service:
                all_techs = self.knowledge_service.get_all()
                pairs = []
                for tech in all_techs:
                    emb = self.embedding_service.get_embedding(tech.technology_id)
                    if emb:
                        pairs.append((tech, emb))
                sync_res = self.chroma_sync_service.sync_batch(pairs, incremental=True)
                chroma_count = sync_res.inserted_count + sync_res.updated_count

            elapsed = round(time.time() - start_time, 4)
            snap_id = snapshot.metadata.snapshot_id if snapshot else None

            logger.info("[Industry] Refresh Completed: %d created, %d updated in %.2fs.", created, updated, elapsed)

            return RefreshSummaryReport(
                run_id=run_id,
                success=True,
                raw_jobs_count=raw_count,
                clean_jobs_count=clean_count,
                normalized_count=norm_count,
                knowledge_created=created,
                knowledge_updated=updated,
                embeddings_generated=emb_count,
                chroma_synced=chroma_count,
                snapshot_id=snap_id,
                execution_time_seconds=elapsed,
            )

        except Exception as exc:
            elapsed = round(time.time() - start_time, 4)
            logger.error("[Industry] Refresh Failed (run_id='%s'): %s", run_id, exc)
            return RefreshSummaryReport(
                run_id=run_id,
                success=False,
                raw_jobs_count=raw_count,
                error_message=str(exc),
                execution_time_seconds=elapsed,
            )

    @staticmethod
    def _create_default_raw_jobs() -> List[Job]:
        """Generate default raw jobs for baseline refresh runs."""
        return [
            Job(
                job_id="job-001",
                title="Senior AI Engineer",
                company="TechCorp",
                location="Remote",
                description="We are seeking a Senior AI Engineer skilled in Python, PyTorch, TensorFlow, Redis, and Docker to scale LLM infrastructure on AWS.",
                source="linkedin",
                url="https://example.com/job1",
                posted_date="2026-08-01",
            ),
            Job(
                job_id="job-002",
                title="Full Stack Engineer",
                company="WebDev Inc",
                location="San Francisco",
                description="Looking for a Full Stack Engineer proficient in React, TypeScript, Node.js, FastAPI, PostgreSQL, and GraphQL.",
                source="indeed",
                url="https://example.com/job2",
                posted_date="2026-08-01",
            ),
            Job(
                job_id="job-003",
                title="DevOps Lead",
                company="CloudOps",
                location="New York",
                description="Seeking a DevOps Lead with expertise in Kubernetes, Docker, Terraform, AWS, Prometheus, and Python scripting.",
                source="glassdoor",
                url="https://example.com/job3",
                posted_date="2026-08-02",
            ),
        ]

    @staticmethod
    def _extract_profiles_from_clean_jobs(clean_jobs: List[Any]) -> List[TechnologyProfile]:
        """Extract TechnologyProfile inputs from CleanJob objects."""
        profiles = []
        for cj in clean_jobs:
            desc = cj.clean_description.lower()
            categories: Dict[str, List[Any]] = {}

            # Simple extraction heuristics for refresh pipeline
            tech_keywords = {
                "languages": ["python", "typescript", "java", "golang", "rust", "c++"],
                "frameworks": ["react", "fastapi", "django", "next.js"],
                "libraries": ["pytorch", "tensorflow", "scikit-learn", "numpy", "pandas"],
                "databases": ["postgresql", "redis", "mongodb"],
                "cloud": ["aws", "gcp", "azure"],
                "devops": ["docker", "kubernetes", "terraform"],
            }

            for cat_key, keywords in tech_keywords.items():
                matched = [kw for kw in keywords if kw in desc]
                if matched:
                    categories[cat_key] = matched

            if categories:
                profiles.append(TechnologyProfile(job_id=cj.job_id, categories=categories))
        return profiles

    @staticmethod
    def _convert_clean_jobs_to_freq_records(
        clean_jobs: List[Any], norm_result: Any
    ) -> List[JobTechnologyRecord]:
        """Convert CleanJobs & NormalizedTechs into JobTechnologyRecord objects for FrequencyEngine."""
        norm_map = {}
        for nt in norm_result.normalized:
            norm_map[nt.canonical_name.lower()] = nt.canonical_name

        freq_records = []
        for cj in clean_jobs:
            desc = cj.clean_description.lower()
            techs_by_cat: Dict[str, List[str]] = {}

            for kw, cname in norm_map.items():
                if kw in desc:
                    techs_by_cat.setdefault("general", []).append(cname)

            freq_records.append(
                JobTechnologyRecord(
                    job_id=cj.job_id,
                    role=cj.title,
                    technologies=techs_by_cat,
                )
            )
        return freq_records
