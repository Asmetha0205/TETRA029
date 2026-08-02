"""
Academic Technology Extractor for CurricuAlign AI Academic Engine.

Main orchestrator for LLM-based technology extraction from ParsedAcademicDocument.
"""

import logging
from typing import Dict, List, Optional

from backend.academic_engine.config.config import AcademicEngineConfig
from backend.academic_engine.extraction.gemini_client import GeminiClient
from backend.academic_engine.extraction.validator import ExtractionValidator
from backend.academic_engine.models.academic_document import ParsedAcademicDocument

logger = logging.getLogger("academic_engine.extraction.academic_extractor")


class AcademicExtractor:
    """
    Main Extractor facade for extracting technology categories from parsed curriculum documents.
    """

    def __init__(self, config: Optional[AcademicEngineConfig] = None) -> None:
        self.config = config or AcademicEngineConfig()
        self.gemini_client = GeminiClient(config=self.config)

    def extract_technologies_from_document(
        self, document: ParsedAcademicDocument
    ) -> Dict[str, List[str]]:
        """
        Extract technologies from a ParsedAcademicDocument.

        Returns:
            Dict mapping clean category keys to lists of technology names.
        """
        logger.info("[Academic] Technologies Extracted from document '%s'.", document.document_id)
        raw_extractions = self.gemini_client.extract_technologies(document.clean_text)
        cleaned = ExtractionValidator.validate_and_clean(raw_extractions)

        total_extracted = sum(len(v) for v in cleaned.values())
        logger.info(
            "[Academic] Extracted %d total technology mentions across %d categories.",
            total_extracted, len(cleaned)
        )
        return cleaned
