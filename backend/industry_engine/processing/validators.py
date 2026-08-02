"""
Job Preprocessing Validator for CurricuAlign AI Industry Engine.
Verifies text lengths, non-corrupt content, title presence, and language criteria.
"""

import re
import logging
from typing import Tuple, Optional
from backend.industry_engine.models.job import Job

logger = logging.getLogger("industry_engine.processing.validators")


class PreprocessingValidator:
    """
    Validates job postings against quality thresholds prior to LLM extraction.
    """

    def __init__(self, min_description_length: int = 50):
        self.min_description_length = min_description_length
        # Pattern checking for garbage or corrupt characters
        self.CORRUPT_CONTENT_RE = re.compile(r"([\%\$\@\#\*\!\?\/\\\=\+]{5,})")

    def validate_job(self, job: Job, cleaned_description: str, is_english: bool) -> Tuple[bool, Optional[str]]:
        """
        Validates a processed job record.
        Returns tuple: (is_valid: bool, rejection_reason: Optional[str]).
        """
        # 1. Title presence check
        if not job.title or not job.title.strip():
            return False, "Missing or blank job title"

        # 2. Description length check
        if not cleaned_description or len(cleaned_description.strip()) < self.min_description_length:
            return False, f"Cleaned description length ({len(cleaned_description.strip())} chars) below minimum threshold ({self.min_description_length} chars)"

        # 3. Language check
        if not is_english:
            return False, "Unsupported non-English language"

        # 4. Corrupt / Garbage content check
        if self.CORRUPT_CONTENT_RE.search(cleaned_description):
            return False, "Detected corrupt or spam symbol sequences in job text"

        return True, None
