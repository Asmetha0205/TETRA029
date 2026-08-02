"""
PDF Parsing Engine Package for CurricuAlign AI Academic Engine.
"""

from backend.academic_engine.parser.course_detector import CourseDetector
from backend.academic_engine.parser.exceptions import CorruptPDFError, EncryptedPDFError, PDFParsingError, TextExtractionError
from backend.academic_engine.parser.metadata_extractor import MetadataExtractor
from backend.academic_engine.parser.pdf_parser import PDFParser
from backend.academic_engine.parser.section_detector import SectionDetector
from backend.academic_engine.parser.semester_detector import SemesterDetector
from backend.academic_engine.parser.text_cleaner import TextCleaner

__all__ = [
    "PDFParser",
    "TextCleaner",
    "SectionDetector",
    "CourseDetector",
    "SemesterDetector",
    "MetadataExtractor",
    "PDFParsingError",
    "CorruptPDFError",
    "EncryptedPDFError",
    "TextExtractionError",
]
