"""
Duplicate Detector for CurricuAlign AI Preprocessing Pipeline.
Detects duplicate job postings using ID, URL, Content Hashes, and Title+Company combinations.
"""

import hashlib
import logging
from typing import Set, Tuple, Optional
from backend.industry_engine.models.job import Job

logger = logging.getLogger("industry_engine.processing.duplicate_detector")


class DuplicateDetector:
    """
    Stateful duplicate detector maintaining in-memory cache of seen jobs.
    """

    def __init__(self):
        self.seen_job_ids: Set[str] = set()
        self.seen_urls: Set[str] = set()
        self.seen_content_hashes: Set[str] = set()
        self.seen_title_company_pairs: Set[str] = set()

    def is_duplicate(self, job: Job, cleaned_description: str) -> Tuple[bool, Optional[str]]:
        """
        Checks if the job posting is a duplicate.
        Returns (is_duplicate: bool, reason: str or None).
        """
        # 1. Job ID check
        if job.job_id in self.seen_job_ids:
            return True, f"Duplicate job_id '{job.job_id}'"

        # 2. URL check (if URL present)
        if job.url and job.url.strip() and job.url in self.seen_urls:
            return True, f"Duplicate URL '{job.url}'"

        # 3. Title + Company pair check
        company_clean = (job.company or "unknown").strip().lower()
        title_clean = (job.title or "").strip().lower()
        pair_key = f"{title_clean}::{company_clean}"

        if title_clean and company_clean != "unknown" and pair_key in self.seen_title_company_pairs:
            return True, f"Duplicate Title+Company combination '{pair_key}'"

        # 4. Content MD5 Hash check
        content_clean = "".join(cleaned_description.lower().split())
        content_hash = hashlib.md5(content_clean.encode("utf-8")).hexdigest()

        if content_hash in self.seen_content_hashes:
            return True, f"Duplicate content hash '{content_hash}'"

        # If not duplicate, register into sets
        self.seen_job_ids.add(job.job_id)
        if job.url and job.url.strip():
            self.seen_urls.add(job.url)
        if title_clean and company_clean != "unknown":
            self.seen_title_company_pairs.add(pair_key)
        self.seen_content_hashes.add(content_hash)

        return False, None

    def reset(self) -> None:
        """
        Resets seen job state caches.
        """
        self.seen_job_ids.clear()
        self.seen_urls.clear()
        self.seen_content_hashes.clear()
        self.seen_title_company_pairs.clear()
