"""
Response Parser for LLM Recommendation Output.
Strips markdown code block wrappers (```json ... ```), parses JSON safely,
and handles JSON formatting errors.
"""

import json
from typing import Any, Dict
from backend.recommendation_engine.utils.helpers import clean_json_text
from backend.recommendation_engine.utils.logger import llm_logger


class ResponseParserError(Exception):
    """Raised when JSON parsing of LLM response fails."""
    pass


class LLMResponseParser:
    """
    Parses LLM text outputs into clean Python dictionaries.
    Strictly handles JSON extraction, stripping markdown fences.
    """

    @classmethod
    def parse_recommendations_json(cls, raw_text: str) -> Dict[str, Any]:
        """
        Parse raw text response from LLM into a dictionary payload.
        """
        if not raw_text or not raw_text.strip():
            llm_logger.error("Response Parser Error: Received empty raw response text from LLM.")
            raise ResponseParserError("LLM response text is empty.")

        cleaned = clean_json_text(raw_text)

        try:
            parsed = json.loads(cleaned)
            if not isinstance(parsed, dict):
                llm_logger.error(f"Response Parser Error: Expected JSON object dict, got {type(parsed)}")
                raise ResponseParserError(f"Expected JSON object dictionary, got {type(parsed)}")

            llm_logger.info("Parsed LLM Response JSON successfully.")
            return parsed

        except json.JSONDecodeError as e:
            llm_logger.error(f"JSON Decoding Failed: {e}. Raw text sample: {raw_text[:200]}")
            raise ResponseParserError(f"Failed to parse LLM JSON output: {e}") from e
