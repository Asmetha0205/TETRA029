"""
Text Normalizer for CurricuAlign AI Preprocessing Pipeline.
Standardizes whitespace, quotes, bullet points, and formatting while preserving technical syntax.
"""

import re
import logging

logger = logging.getLogger("industry_engine.processing.text_normalizer")


class TextNormalizer:
    """
    Normalizes typographic quotes, bullet markers, whitespace, and line breaks.
    Specifically designed NOT to break programming language names (C++, C#, .NET, Node.js).
    """

    QUOTE_MAP = {
        "“": '"', "”": '"', "„": '"',
        "‘": "'", "’": "'", "`": "'"
    }

    BULLET_RE = re.compile(r"^[\s\t]*[•\*➢–—]\s*", re.MULTILINE)
    MULTIPLE_SPACES_RE = re.compile(r"[ \t]+")

    def normalize(self, text: str) -> str:
        """
        Executes text normalization pass.
        """
        if not text:
            return ""

        # 1. Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # 2. Normalize smart/curly quotes
        for fancy, plain in self.QUOTE_MAP.items():
            text = text.replace(fancy, plain)

        # 3. Standardize bullet points to markdown style "-"
        text = self.BULLET_RE.sub("- ", text)

        # 4. Collapse multiple inline spaces and tabs without touching newlines
        lines = []
        for line in text.split("\n"):
            normalized_line = self.MULTIPLE_SPACES_RE.sub(" ", line).strip()
            if normalized_line:
                lines.append(normalized_line)

        normalized_text = "\n".join(lines)
        return normalized_text
