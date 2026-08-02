"""
Job Preprocessing Pipeline for CurricuAlign AI Industry Engine.
Orchestrates Cleaning, Normalization, Language Validation, Duplicate Detection, and Metric Tracking.
"""

import time
import logging
from typing import List, Dict, Any, Tuple
from backend.industry_engine.models.job import Job
from backend.industry_engine.models.clean_job import CleanJob
from backend.industry_engine.processing.job_cleaner import JobCleaner
from backend.industry_engine.processing.text_normalizer import TextNormalizer
from backend.industry_engine.processing.duplicate_detector import DuplicateDetector
from backend.industry_engine.processing.language_detector import LanguageDetector
from backend.industry_engine.processing.validators import PreprocessingValidator

logger = logging.getLogger("industry_engine.processing.pipeline")


class JobPreprocessingPipeline:
    """
    Complete Preprocessing Pipeline taking raw Job models and outputting clean, validated CleanJob models.
    """

    def __init__(self, min_description_length: int = 50):
        self.cleaner = JobCleaner()
        self.normalizer = TextNormalizer()
        self.duplicate_detector = DuplicateDetector()
        self.language_detector = LanguageDetector()
        self.validator = PreprocessingValidator(min_description_length=min_description_length)
        self.last_pipeline_stats: Dict[str, Any] = {}

    def process_jobs(self, raw_jobs: List[Job]) -> Tuple[List[CleanJob], Dict[str, Any]]:
        """
        Executes the preprocessing workflow over a list of raw Job postings.
        """
        start_time = time.time()
        clean_jobs: List[CleanJob] = []

        total_processed = len(raw_jobs)
        duplicates_count = 0
        rejections_count = 0
        rejection_reasons: Dict[str, int] = {}

        logger.info(f"[PreprocessingPipeline] Starting batch preprocessing for {total_processed} raw jobs...")

        for raw_job in raw_jobs:
            # Step 1: Clean raw HTML and strip boilerplate
            cleaned_text = self.cleaner.clean_text(raw_job.description)

            # Step 2: Normalize text formatting, quotes, bullet points
            normalized_text = self.normalizer.normalize(cleaned_text)

            # Step 3: Detect language
            is_en, lang, confidence = self.language_detector.is_english(normalized_text)

            # Step 4: Validate quality, length, corruption, and language
            is_valid, reject_reason = self.validator.validate_job(raw_job, normalized_text, is_en)
            if not is_valid:
                rejections_count += 1
                reason_str = reject_reason or "Unknown validation failure"
                rejection_reasons[reason_str] = rejection_reasons.get(reason_str, 0) + 1
                logger.debug(f"[PreprocessingPipeline] Job '{raw_job.job_id}' rejected: {reason_str}")
                continue

            # Step 5: Duplicate detection
            is_dup, dup_reason = self.duplicate_detector.is_duplicate(raw_job, normalized_text)
            if is_dup:
                duplicates_count += 1
                reason_str = f"Duplicate: {dup_reason}"
                rejection_reasons[reason_str] = rejection_reasons.get(reason_str, 0) + 1
                logger.debug(f"[PreprocessingPipeline] Job '{raw_job.job_id}' flagged as duplicate: {dup_reason}")
                continue

            # Step 6: Create CleanJob model
            clean_job = CleanJob(
                job_id=raw_job.job_id,
                title=raw_job.title,
                company=raw_job.company or "Unknown",
                location=raw_job.location or "Remote / Unspecified",
                clean_description=normalized_text,
                source=raw_job.source,
                url=raw_job.url,
                posted_date=raw_job.posted_date,
                metadata={
                    "char_count": len(normalized_text),
                    "word_count": len(normalized_text.split()),
                    "detected_language": lang,
                    "language_confidence": confidence
                }
            )
            clean_jobs.append(clean_job)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        self.last_pipeline_stats = {
            "total_raw_jobs_processed": total_processed,
            "valid_clean_jobs_produced": len(clean_jobs),
            "duplicates_removed": duplicates_count,
            "jobs_rejected": rejections_count,
            "rejection_reasons_breakdown": rejection_reasons,
            "processing_time_ms": elapsed_ms
        }

        logger.info(
            f"[PreprocessingPipeline] Batch Processing Completed: {len(clean_jobs)} clean jobs produced "
            f"({duplicates_count} duplicates, {rejections_count} rejected) in {elapsed_ms} ms."
        )

        return clean_jobs, self.last_pipeline_stats

    def reset_state(self) -> None:
        """
        Resets stateful duplicate detector cache.
        """
        self.duplicate_detector.reset()
