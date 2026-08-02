"""
Semester Detector for PDF Parsing Engine.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger("academic_engine.parser.semester_detector")


class SemesterDetector:
    """Detects semester or term designations within curriculum text."""

    SEMESTER_PATTERNS = [
        r"(?i)\b(semester\s+[I|V|X|0-9]+)\b",
        r"(?i)\b(term\s+[0-9]+)\b",
        r"(?i)\b(year\s+[1-4])\b",
    ]

    @classmethod
    def detect_semester(cls, text: str) -> str:
        """
        Detect semester tag from text snippet or line.

        Returns:
            Semester string e.g. 'Semester 1' or 'Semester V'.
        """
        for pattern in cls.SEMESTER_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(1).title()
        return "Semester 1"
