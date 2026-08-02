"""
Job Cleaner for CurricuAlign AI Preprocessing Pipeline.
Sanitizes raw text, removes HTML, decodes entities, strips emojis, and filters recruiter boilerplate.
"""

import re
import html
import unicodedata
import logging
from typing import List

logger = logging.getLogger("industry_engine.processing.job_cleaner")


class JobCleaner:
    """
    Cleans raw HTML/unstructured job text while preserving technical terminology.
    """

    # Boilerplate patterns commonly found in job postings
    BOILERPLATE_PATTERNS: List[re.Pattern] = [
        re.compile(r"equal\s+opportunity\s+employer.*?(?=\n|\.|$)", re.IGNORECASE),
        re.compile(r"eoe\s+m/f/d/v.*?(?=\n|\.|$)", re.IGNORECASE),
        re.compile(r"all\s+qualified\s+applicants\s+will\s+receive\s+consideration.*?(?=\n|\.|$)", re.IGNORECASE),
        re.compile(r"apply\s+now|click\s+here\s+to\s+apply|submit\s+your\s+resume", re.IGNORECASE),
        re.compile(r"we\s+are\s+an\s+equal\s+opportunity\s+employer.*?(?=\n|\.|$)", re.IGNORECASE),
        re.compile(r"privacy\s+policy|terms\s+of\s+service|cookie\s+settings", re.IGNORECASE),
        re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE),  # Remove tracking URLs
    ]

    # Regex for stripping HTML tags
    HTML_TAG_RE = re.compile(r"<[^>]+>")

    # Emoji regex range
    EMOJI_RE = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )

    def clean_text(self, raw_text: str) -> str:
        """
        Executes full text cleaning pass.
        """
        if not raw_text or not raw_text.strip():
            return ""

        # 1. Decode HTML entities (e.g. &amp; -> &, &lt; -> <)
        text = html.unescape(raw_text)

        # 2. Strip HTML tags (convert <br> and <p> to newlines first)
        text = re.sub(r"<(br|p|div|li)[^>]*>", "\n", text, flags=re.IGNORECASE)
        text = self.HTML_TAG_RE.sub(" ", text)

        # 3. Unicode NFKC normalization
        text = unicodedata.normalize("NFKC", text)

        # 4. Remove emojis
        text = self.EMOJI_RE.sub("", text)

        # 5. Filter recruiter boilerplate and advertisements
        for pattern in self.BOILERPLATE_PATTERNS:
            text = pattern.sub("", text)

        # 6. Normalize excessive blank lines and spaces
        lines = [line.strip() for line in text.splitlines()]
        cleaned_lines = [line for line in lines if line]
        text = "\n".join(cleaned_lines)

        return text.strip()
