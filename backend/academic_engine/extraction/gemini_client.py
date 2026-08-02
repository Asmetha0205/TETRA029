"""
Gemini Client Wrapper for Academic Technology Extraction.

Calls Google Gemini API for extraction. Includes a deterministic keyword heuristic
fallback when running offline or when API keys are not provided.
"""

import os
import re
import logging
from typing import Dict, List, Optional

from backend.academic_engine.config.config import AcademicEngineConfig
from backend.academic_engine.extraction.prompt_builder import ExtractionPromptBuilder
from backend.academic_engine.extraction.response_parser import ExtractionResponseParser

logger = logging.getLogger("academic_engine.extraction.gemini_client")

_GENAI_AVAILABLE = False
try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False


class GeminiClient:
    """Wrapper for Google Gemini AI extraction with offline rule-based fallback."""

    def __init__(self, config: Optional[AcademicEngineConfig] = None) -> None:
        self.config = config or AcademicEngineConfig()
        self.api_key = self.config.gemini_api_key or os.getenv("GEMINI_API_KEY")
        self._model: Any = None

        if not self.config.force_offline_extraction and _GENAI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.config.gemini_model_name)
                logger.info("[Academic] Initialized Gemini model '%s'.", self.config.gemini_model_name)
            except Exception as exc:
                logger.warning("[Academic] Failed to initialize Gemini model: %s. Using fallback.", exc)

    def extract_technologies(self, text: str) -> Dict[str, List[str]]:
        """
        Extract technologies from curriculum text using Gemini or Fallback.

        Returns:
            Dict mapping categories to extracted technology lists.
        """
        if self._model and not self.config.force_offline_extraction:
            try:
                prompt = ExtractionPromptBuilder.build_prompt(text)
                response = self._model.generate_content(prompt)
                if response and response.text:
                    parsed = ExtractionResponseParser.parse_response(response.text)
                    if parsed:
                        logger.info("[Academic] Gemini extraction succeeded.")
                        return parsed
            except Exception as exc:
                logger.warning("[Academic] Gemini API call failed: %s. Using fallback extractor.", exc)

        return self._extract_fallback(text)

    @staticmethod
    def _extract_fallback(text: str) -> Dict[str, List[str]]:
        """Deterministic keyword extraction fallback."""
        low_text = text.lower()
        extracted: Dict[str, List[str]] = {}

        keyword_rules = {
            "programming_languages": [
                ("python", "Python"), ("c++", "C++"), ("java", "Java"),
                ("typescript", "TypeScript"), ("javascript", "JavaScript"),
                ("golang", "Go"), ("rust", "Rust"), ("c#", "C#"), ("sql", "SQL"),
            ],
            "frameworks": [
                ("django", "Django"), ("fastapi", "FastAPI"), ("react", "React"),
                ("spring", "Spring Boot"), ("express", "Express.js"), ("next.js", "Next.js"),
            ],
            "libraries": [
                ("pytorch", "PyTorch"), ("tensorflow", "TensorFlow"), ("numpy", "NumPy"),
                ("pandas", "Pandas"), ("scikit-learn", "scikit-learn"), ("opencv", "OpenCV"),
            ],
            "databases": [
                ("postgresql", "PostgreSQL"), ("mysql", "MySQL"), ("mongodb", "MongoDB"),
                ("redis", "Redis"), ("oracle", "Oracle DB"),
            ],
            "cloud": [
                ("aws", "AWS"), ("azure", "Azure"), ("gcp", "Google Cloud"),
            ],
            "devops": [
                ("docker", "Docker"), ("kubernetes", "Kubernetes"), ("terraform", "Terraform"),
                ("jenkins", "Jenkins"), ("git", "Git"),
            ],
            "ai_technologies": [
                ("machine learning", "Machine Learning"), ("deep learning", "Deep Learning"),
                ("computer vision", "Computer Vision"), ("natural language processing", "NLP"),
                ("artificial intelligence", "Artificial Intelligence"),
            ],
            "core_computer_science": [
                ("data structures", "Data Structures"), ("algorithms", "Algorithms"),
                ("operating systems", "Operating Systems"), ("database management", "Database Management Systems"),
                ("computer networks", "Computer Networks"), ("software engineering", "Software Engineering"),
            ],
            "mathematics": [
                ("linear algebra", "Linear Algebra"), ("calculus", "Calculus"),
                ("probability", "Probability & Statistics"), ("discrete mathematics", "Discrete Mathematics"),
            ],
            "developer_tools": [
                ("git", "Git"), ("vscode", "VS Code"), ("linux", "Linux"),
            ],
        }

        for cat, pairs in keyword_rules.items():
            found = []
            for kw, display in pairs:
                if re.search(r"\b" + re.escape(kw) + r"\b", low_text):
                    if display not in found:
                        found.append(display)
            if found:
                extracted[cat] = found

        logger.info("[Academic] Rule-based fallback extracted %d categories.", len(extracted))
        return extracted
