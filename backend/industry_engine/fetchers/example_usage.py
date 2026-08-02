"""
Example Usage & Plugin Extension Script for CurricuAlign AI Job Fetching Subsystem.
Demonstrates:
 1. Standard execution of FetcherManager.
 2. Custom plugin creation and zero-code-change registration via FetcherFactory.
"""

import logging
from typing import List, Dict, Any
from backend.industry_engine.models.job import Job
from backend.industry_engine.fetchers.base_fetcher import AbstractJobFetcher
from backend.industry_engine.fetchers.factory import FetcherFactory
from backend.industry_engine.fetchers.manager import FetcherManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("example_usage")


# =====================================================================
# DEMO: Adding a new job source plugin ("rss") requiring ZERO code changes to core
# =====================================================================
class CustomRSSJobFetcher(AbstractJobFetcher):
    """
    Example Custom RSS Plugin.
    Demonstrates zero-code-change extensibility.
    """

    def initialize(self) -> None:
        logger.info(f"[{self.source_name}] Initializing Custom RSS Job Fetcher...")
        self.is_initialized = True

    def health_check(self) -> bool:
        logger.info(f"[{self.source_name}] RSS Feed connection check passed.")
        return True

    def fetch_jobs(self, limit: int = 100) -> List[Job]:
        logger.info(f"[{self.source_name}] Fetching RSS jobs...")
        # Simulated RSS parsed item
        raw_rss_item = {
            "job_id": "rss_item_901",
            "title": "Lead Agentic AI Architect",
            "company": "Autonomous Systems Inc",
            "location": "Remote",
            "description": "Designing multi-agent frameworks using Agentic AI, MCP protocol, LangGraph, vLLM, Python, and ChromaDB.",
            "url": "https://rss.jobs.example.com/item/901",
            "posted_date": "2026-08-01"
        }

        if not self.validate(raw_rss_item):
            return []

        return [
            Job(
                job_id=raw_rss_item["job_id"],
                title=raw_rss_item["title"],
                company=raw_rss_item["company"],
                location=raw_rss_item["location"],
                description=raw_rss_item["description"],
                source=self.source_name,
                url=raw_rss_item["url"],
                posted_date=raw_rss_item["posted_date"],
                raw_data=raw_rss_item
            )
        ]

    def close(self) -> None:
        logger.info(f"[{self.source_name}] RSS fetcher closed.")
        self.is_initialized = False


def main():
    print("=" * 70)
    print("1. REGISTERING NEW CUSTOM PLUGIN VIA FACTORY")
    print("=" * 70)
    # Register new RSS plugin at runtime
    FetcherFactory.register_fetcher("rss", CustomRSSJobFetcher)
    print(f"Registered sources in factory: {FetcherFactory.get_registered_sources()}\n")

    print("=" * 70)
    print("2. CONFIGURING AND EXECUTING FETCHER MANAGER")
    print("=" * 70)
    manager_config = {
        "enabled_sources": ["api", "dataset", "rss"],  # Includes new source seamlessly
        "sources": {
            "api": {"endpoint_url": "https://api.jobs.com/feed"},
            "dataset": {"file_path": "storage_data/cache/job_dataset.json"},
            "rss": {"feed_url": "https://rss.jobs.com/tech"}
        }
    }

    manager = FetcherManager(config=manager_config)
    jobs: List[Job] = manager.fetch_all_jobs(limit_per_source=5)

    print("\n" + "=" * 70)
    print("3. INGESTION RESULTS & DEDUPLICATED UNIFIED JOB LIST")
    print("=" * 70)
    print(f"Total Unique Jobs Returned: {len(jobs)}")
    for idx, job in enumerate(jobs, 1):
        print(f"\n--- Job #{idx} ---")
        print(f"ID         : {job.job_id}")
        print(f"Title      : {job.title}")
        print(f"Company    : {job.company}")
        print(f"Source     : {job.source}")
        print(f"Description: {job.description[:100]}...")

    print("\n" + "=" * 70)
    print("4. EXECUTION STATISTICS & AUDIT TRAIL")
    print("=" * 70)
    stats = manager.get_statistics()
    import json
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
