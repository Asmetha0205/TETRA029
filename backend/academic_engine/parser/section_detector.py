"""
Section Detector for PDF Parsing Engine.

Identifies curriculum sections (Syllabus, Course Description, Learning Outcomes, Modules, Prerequisites, etc.).
"""

import re
import logging
from typing import List
from backend.academic_engine.models.academic_document import ParsedSection

logger = logging.getLogger("academic_engine.parser.section_detector")


class SectionDetector:
    """Detects structural sections within cleaned curriculum text."""

    SECTION_PATTERNS = [
        (r"(?i)^(course\s+description|course\s+overview|about\s+the\s+course)", "overview"),
        (r"(?i)^(learning\s+outcomes|course\s+outcomes|objectives)", "outcomes"),
        (r"(?i)^(prerequisites|eligibility)", "prerequisites"),
        (r"(?i)^(course\s+content|syllabus|curriculum|modules|units)", "modules"),
        (r"(?i)^(textbooks|reference\s+books|reading\s+list)", "references"),
        (r"(?i)^(assessment|grading\s+scheme|evaluation)", "assessment"),
    ]

    @classmethod
    def detect_sections(cls, text: str) -> List[ParsedSection]:
        """
        Split document text into structural sections.

        Returns:
            List of ParsedSection objects.
        """
        sections: List[ParsedSection] = []
        lines = text.split("\n")

        current_title = "General Overview"
        current_type = "overview"
        current_lines: List[str] = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            matched_type = None
            for pattern, stype in cls.SECTION_PATTERNS:
                if re.search(pattern, stripped):
                    matched_type = stype
                    break

            if matched_type:
                # Flush previous section
                if current_lines:
                    sections.append(
                        ParsedSection(
                            title=current_title,
                            content="\n".join(current_lines),
                            section_type=current_type,
                        )
                    )
                    current_lines = []
                current_title = stripped
                current_type = matched_type
            else:
                current_lines.append(stripped)

        if current_lines:
            sections.append(
                ParsedSection(
                    title=current_title,
                    content="\n".join(current_lines),
                    section_type=current_type,
                )
            )

        logger.info("[PDF] Detected %d document sections.", len(sections))
        return sections
