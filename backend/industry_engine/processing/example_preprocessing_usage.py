"""
Example Usage Script for CurricuAlign AI Job Preprocessing Subsystem.
Demonstrates end-to-end processing from raw fetched jobs to sanitized CleanJob models.
"""

import json
import logging
from backend.industry_engine.fetchers.manager import FetcherManager
from backend.industry_engine.processing.pipeline import JobPreprocessingPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("example_preprocessing_usage")


def main():
    print("=" * 75)
    print("1. INGESTING RAW JOBS FROM FETCHING SUBSYSTEM")
    print("=" * 75)
    fetcher_manager = FetcherManager(config={"enabled_sources": ["api", "dataset"]})
    raw_jobs = fetcher_manager.fetch_all_jobs(limit_per_source=5)

    print(f"\nTotal Raw Jobs Fetched: {len(raw_jobs)}\n")

    print("=" * 75)
    print("2. EXECUTING PREPROCESSING PIPELINE (CLEAN, NORMALIZE, FILTER, DEDUP)")
    print("=" * 75)
    pipeline = JobPreprocessingPipeline(min_description_length=50)
    clean_jobs, stats = pipeline.process_jobs(raw_jobs)

    print("\n" + "=" * 75)
    print("3. SANITIZED CLEANJOB OUTPUT HIGHLIGHTS")
    print("=" * 75)
    for idx, cjob in enumerate(clean_jobs, 1):
        print(f"\n--- CleanJob #{idx} ---")
        print(f"Job ID    : {cjob.job_id}")
        print(f"Title     : {cjob.title}")
        print(f"Company   : {cjob.company}")
        print(f"Metadata  : {cjob.metadata}")
        print(f"Clean Text:\n{cjob.clean_description[:160]}...")

    print("\n" + "=" * 75)
    print("4. PIPELINE METRICS & AUDIT STATISTICS")
    print("=" * 75)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
