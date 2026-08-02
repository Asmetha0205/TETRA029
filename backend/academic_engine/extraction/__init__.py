"""
Academic Technology Extraction Package for CurricuAlign AI Academic Engine.
"""

from backend.academic_engine.extraction.academic_extractor import AcademicExtractor
from backend.academic_engine.extraction.exceptions import ExtractionError, GeminiAPIError, MalformedExtractionJSONError
from backend.academic_engine.extraction.gemini_client import GeminiClient
from backend.academic_engine.extraction.prompt_builder import ExtractionPromptBuilder
from backend.academic_engine.extraction.response_parser import ExtractionResponseParser
from backend.academic_engine.extraction.validator import ExtractionValidator

__all__ = [
    "AcademicExtractor",
    "GeminiClient",
    "ExtractionPromptBuilder",
    "ExtractionResponseParser",
    "ExtractionValidator",
    "ExtractionError",
    "GeminiAPIError",
    "MalformedExtractionJSONError",
]
