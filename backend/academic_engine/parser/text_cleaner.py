"""
Text Cleaner for PDF Parsing Engine.

Cleans raw extracted PDF text, normalizes whitespace, strips headers/footers,
and preserves headings and section boundaries.
"""

import re
import logging

logger = logging.getLogger("academic_engine.parser.text_cleaner")


class TextCleaner:
    """Cleans and formats extracted PDF text for downstream structure detection."""

    @classmethod
    def clean(cls, raw_text: str) -> str:
        """
        Clean raw PDF text.

        Args:
            raw_text: Raw string extracted from PDF.

        Returns:
            Cleaned and normalized text string.
        """
        if not raw_text:
            return ""

        # Remove null bytes & non-printable control chars (preserve \n and \t)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", raw_text)

        # Remove page numbers & repeating header/footer patterns
        text = re.sub(r"(?i)page\s+\d+\s+of\s+\d+", "", text)
        text = re.sub(r"(?i)page\s+\d+", "", text)

        # Normalize multiple spaces (keep newlines)
        text = re.sub(r"[ \t]+", " ", text)

        # Normalize multiple blank lines (max 2 consecutive newlines)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

        return text.strip()
