"""
Unit tests for Academic Technology Extraction.
"""

import unittest
from backend.academic_engine.extraction import (
    AcademicExtractor,
    ExtractionPromptBuilder,
    ExtractionResponseParser,
    ExtractionValidator,
    GeminiClient,
)


class TestAcademicExtractionModule(unittest.TestCase):
    """Test suite for technology extraction pipeline."""

    def test_prompt_builder(self):
        prompt = ExtractionPromptBuilder.build_prompt("CS101 teaches Python, C++, and Docker.")
        self.assertIn("Python", prompt)
        self.assertIn("JSON", prompt)

    def test_response_parser(self):
        json_str = '```json\n{"programming_languages": ["Python", "C++"], "frameworks": ["Django"]}\n```'
        parsed = ExtractionResponseParser.parse_response(json_str)
        self.assertIn("programming_languages", parsed)
        self.assertEqual(parsed["programming_languages"], ["Python", "C++"])

    def test_validator(self):
        raw = {"programming_languages": [" Python ", "Python", "c++", ""]}
        cleaned = ExtractionValidator.validate_and_clean(raw)
        self.assertEqual(cleaned["programming_languages"], ["Python", "c++"])

    def test_gemini_fallback_extractor(self):
        client = GeminiClient()
        extractions = client.extract_technologies("Students will learn Python, PyTorch, Docker, and PostgreSQL.")
        self.assertIn("programming_languages", extractions)
        self.assertIn("Python", extractions["programming_languages"])
        self.assertIn("PyTorch", extractions["libraries"])
        self.assertIn("Docker", extractions["devops"])
        self.assertIn("PostgreSQL", extractions["databases"])


if __name__ == "__main__":
    unittest.main()
