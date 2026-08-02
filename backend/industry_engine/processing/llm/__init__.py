"""
CurricuAlign AI - LLM Technology Intelligence Engine Package.
Phase 3.4: AI-powered extraction of structured technology intelligence from job descriptions.
"""

from backend.industry_engine.processing.llm.models import (
    TechnologyCategories,
    TechnologyExtraction,
    LLMConfig,
    LLMExecutionStats,
)
from backend.industry_engine.processing.llm.cache import TechnologyExtractionCache
from backend.industry_engine.processing.llm.prompt_builder import PromptBuilder, VALID_CATEGORIES
from backend.industry_engine.processing.llm.response_parser import ResponseParser
from backend.industry_engine.processing.llm.validator import ExtractionValidator
from backend.industry_engine.processing.llm.gemini_client import GeminiClient, GeminiAPIError
from backend.industry_engine.processing.llm.technology_extractor import TechnologyExtractor

__all__ = [
    "TechnologyCategories",
    "TechnologyExtraction",
    "LLMConfig",
    "LLMExecutionStats",
    "TechnologyExtractionCache",
    "PromptBuilder",
    "VALID_CATEGORIES",
    "ResponseParser",
    "ExtractionValidator",
    "GeminiClient",
    "GeminiAPIError",
    "TechnologyExtractor",
]
