"""
PDF Parser for CurricuAlign AI Academic Engine.

Main parser facade combining multi-engine PDF text extraction, text cleaning,
section detection, course detection, and metadata extraction.
"""

import logging
from pathlib import Path
from typing import Optional, Union

from backend.academic_engine.models.academic_document import ParsedAcademicDocument
from backend.academic_engine.parser.course_detector import CourseDetector
from backend.academic_engine.parser.exceptions import TextExtractionError
from backend.academic_engine.parser.metadata_extractor import MetadataExtractor
from backend.academic_engine.parser.section_detector import SectionDetector
from backend.academic_engine.parser.text_cleaner import TextCleaner
from backend.academic_engine.utils.pdf_utils import extract_text_from_pdf

logger = logging.getLogger("academic_engine.parser.pdf_parser")


class PDFParser:
    """
    Primary Parser facade for converting curriculum PDF documents into structured ParsedAcademicDocument objects.
    """

    def parse_pdf(
        self,
        file_source: Union[str, Path, bytes],
        document_id: str = "doc-default",
    ) -> ParsedAcademicDocument:
        """
        Parse a curriculum PDF into a structured document representation.

        Args:
            file_source: PDF file path or byte string.
            document_id: Document ID.

        Returns:
            ParsedAcademicDocument model.
        """
        # Step 1: Text extraction
        raw_text, pages_text, engine_name = extract_text_from_pdf(file_source)

        if not raw_text or not raw_text.strip():
            logger.error("[Academic] PDF Text extraction failed for '%s'.", document_id)
            raise TextExtractionError(f"No readable text could be extracted from PDF document '{document_id}'.")

        # Step 2: Clean text
        clean_text = TextCleaner.clean(raw_text)

        # Step 3: Extract document metadata
        meta = MetadataExtractor.extract_document_metadata(clean_text)

        # Step 4: Detect sections
        sections = SectionDetector.detect_sections(clean_text)

        # Step 5: Detect courses
        courses = CourseDetector.detect_courses(clean_text)
        course_dicts = [c.model_dump() for c in courses]

        doc = ParsedAcademicDocument(
            document_id=document_id,
            university_name=meta["university_name"],
            department=meta["department"],
            degree_program=meta["degree_program"],
            academic_year=meta["academic_year"],
            total_pages=len(pages_text),
            clean_text=clean_text,
            sections=sections,
            courses=course_dicts,
            metadata={"extractor_engine": engine_name},
        )

        logger.info("[Academic] PDF Parsed: '%s' (%d courses, %d sections, engine='%s').",
                    document_id, len(courses), len(sections), engine_name)
        return doc
