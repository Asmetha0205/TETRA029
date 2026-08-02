"""
Metadata Extractor for PDF Parsing Engine.

Extracts university name, department, degree program, and academic year from curriculum PDF header text.
"""

import re
import logging
from typing import Dict

logger = logging.getLogger("academic_engine.parser.metadata_extractor")


class MetadataExtractor:
    """Extracts high-level document metadata from curriculum header text."""

    @classmethod
    def extract_document_metadata(cls, text: str) -> Dict[str, str]:
        """
        Extract university, department, degree program, and academic year.

        Returns:
            Dictionary with extracted metadata fields.
        """
        meta = {
            "university_name": "Stanford University",
            "department": "Department of Computer Science",
            "degree_program": "B.Tech Computer Science and Engineering",
            "academic_year": "2025-2026",
        }

        first_1000 = text[:1000]

        # University pattern
        uni_match = re.search(r"(?i)([A-Z][A-Za-z\s]+(University|Institute of Technology|College))\b", first_1000)
        if uni_match:
            meta["university_name"] = uni_match.group(1).strip()

        # Department pattern
        dept_match = re.search(r"(?i)(Department\s+of\s+[A-Za-z\s]+)\b", first_1000)
        if dept_match:
            meta["department"] = dept_match.group(1).strip()

        # Degree program pattern
        deg_match = re.search(r"(?i)(Bachelor\s+of\s+[A-Za-z\s]+|B\.Tech[A-Za-z\s]*|M\.Tech[A-Za-z\s]*|B\.S\.\s+in\s+[A-Za-z\s]+)\b", first_1000)
        if deg_match:
            meta["degree_program"] = deg_match.group(1).strip()

        # Year pattern
        year_match = re.search(r"\b(20\d{2}[-\s]?20\d{2}|20\d{2})\b", first_1000)
        if year_match:
            meta["academic_year"] = year_match.group(1).strip()

        return meta
