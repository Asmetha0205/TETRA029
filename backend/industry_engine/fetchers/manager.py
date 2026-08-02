"""
Job Fetcher Manager for CurricuAlign AI.
Orchestrates job fetcher plugins, deduplicates jobs, tracks execution stats, and returns unified job lists.
"""

import time
import logging
import hashlib
from typing import List, Dict, Any, Set, Optional
from backend.industry_engine.models.job import Job
from backend.industry_engine.fetchers.base_fetcher import AbstractJobFetcher
from backend.industry_engine.fetchers.factory import FetcherFactory

logger = logging.getLogger("industry_engine.fetchers.manager")


class FetcherManager:
    """
    Manager that loads enabled job fetchers, coordinates parallel/sequential execution,
    deduplicates job records across sources, tracks detailed metrics, and produces a unified job list.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize FetcherManager with configuration dict.
        Config example:
          {
            "enabled_sources": ["api", "dataset"],
            "sources": {
              "api": {"endpoint_url": "https://api.example.com/jobs"},
              "dataset": {"file_path": "storage_data/cache/job_dataset.json"}
            }
          }
        """
        self.config = config or {
            "enabled_sources": ["api", "dataset"],
            "sources": {}
        }
        self.enabled_sources: List[str] = self.config.get("enabled_sources", ["api", "dataset"])
        self.sources_config: Dict[str, Any] = self.config.get("sources", {})
        self.fetchers: List[AbstractJobFetcher] = []
        self.last_execution_stats: Dict[str, Any] = {}

    def _load_fetchers(self) -> None:
        """
        Instantiates all enabled fetcher plugins via FetcherFactory.
        """
        self.fetchers.clear()
        for source_name in self.enabled_sources:
            try:
                source_cfg = self.sources_config.get(source_name, {})
                fetcher = FetcherFactory.create_fetcher(source_name, config=source_cfg)
                self.fetchers.append(fetcher)
            except Exception as e:
                logger.error(f"[FetcherManager] Failed to instantiate fetcher plugin for source '{source_name}': {e}")

    def fetch_all_jobs(self, limit_per_source: int = 100) -> List[Job]:
        """
        Executes job fetching across all enabled sources, deduplicates results,
        tracks execution statistics, and returns a unified list of Job models.
        """
        start_time = time.time()
        self._load_fetchers()

        raw_jobs_collected: List[Job] = []
        source_breakdown: Dict[str, int] = {}
        error_log: List[str] = []

        logger.info(f"[FetcherManager] Starting job ingestion execution across {len(self.fetchers)} fetchers...")

        for fetcher in self.fetchers:
            source_name = fetcher.source_name
            try:
                # 1. Initialize plugin
                fetcher.initialize()

                # 2. Health check
                if not fetcher.health_check():
                    logger.warning(f"[FetcherManager] Source '{source_name}' failed health check. Skipping.")
                    error_log.append(f"Source '{source_name}' failed health check.")
                    continue

                # 3. Fetch jobs
                jobs = fetcher.fetch_jobs(limit=limit_per_source)
                raw_jobs_collected.extend(jobs)
                source_breakdown[source_name] = len(jobs)
                logger.info(f"[FetcherManager] Fetcher '{source_name}' retrieved {len(jobs)} jobs.")

            except Exception as e:
                logger.error(f"[FetcherManager] Exception while executing fetcher '{source_name}': {e}")
                error_log.append(f"Fetcher '{source_name}' raised exception: {str(e)}")
            finally:
                try:
                    fetcher.close()
                except Exception as close_err:
                    logger.warning(f"[FetcherManager] Warning closing fetcher '{source_name}': {close_err}")

        # 4. Deduplicate across sources
        unique_jobs, duplicate_count = self._deduplicate_jobs(raw_jobs_collected)

        execution_time_ms = round((time.time() - start_time) * 1000, 2)

        # 5. Track statistics
        self.last_execution_stats = {
            "total_raw_jobs_collected": len(raw_jobs_collected),
            "unique_jobs_returned": len(unique_jobs),
            "duplicates_removed": duplicate_count,
            "execution_time_ms": execution_time_ms,
            "source_breakdown": source_breakdown,
            "errors": error_log
        }

        logger.info(
            f"[FetcherManager] Execution Completed: Returned {len(unique_jobs)} unique jobs "
            f"(deduplicated {duplicate_count}) in {execution_time_ms} ms."
        )

        return unique_jobs

    def _deduplicate_jobs(self, jobs: List[Job]) -> tuple[List[Job], int]:
        """
        Deduplicates jobs based on unique job_id and description text hashes.
        Returns tuple of (unique_job_list, duplicate_count).
        """
        seen_job_ids: Set[str] = set()
        seen_text_hashes: Set[str] = set()
        unique_jobs: List[Job] = []
        duplicate_count = 0

        for job in jobs:
            # Check 1: Explicit Job ID collision
            if job.job_id in seen_job_ids:
                duplicate_count += 1
                logger.debug(f"[FetcherManager] Duplicate job ID detected: '{job.job_id}'. Skipping.")
                continue

            # Check 2: Content Hash collision (MD5 of sanitized description)
            desc_clean = "".join(job.description.lower().split())
            text_hash = hashlib.md5(desc_clean.encode("utf-8")).hexdigest()

            if text_hash in seen_text_hashes:
                duplicate_count += 1
                logger.debug(f"[FetcherManager] Duplicate text content hash detected for job '{job.job_id}'. Skipping.")
                continue

            seen_job_ids.add(job.job_id)
            seen_text_hashes.add(text_hash)
            unique_jobs.append(job)

        return unique_jobs, duplicate_count

    def get_statistics(self) -> Dict[str, Any]:
        """
        Returns execution statistics from the most recent run.
        """
        return self.last_execution_stats
