"""
Response Parser for Academic Technology Extraction.

Parses raw LLM text responses into structured technology extractions.
"""

import json
import re
import logging
from typing import Any, Dict, List

from backend.academic_engine.extraction.exceptions import MalformedExtractionJSONError

logger = logging.getLogger("academic_engine.extraction.response_parser")


class ExtractionResponseParser:
    """Parses JSON text responses from Gemini or fallback extractors."""

    @classmethod
    def parse_response(cls, raw_response: str) -> Dict[str, List[str]]:
        """
        Parse raw response string into a normalized category dict.

        Returns:
            Dict mapping category strings to lists of technology names.
        """
        if not raw_response or not raw_response.strip():
            return {}

        text = raw_response.strip()

        # Clean markdown codeblocks ```json ... ```
        text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"```$", "", text, flags=re.MULTILINE).strip()

        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                result: Dict[str, List[str]] = {}
                for k, v in parsed.items():
                    if isinstance(v, list):
                        result[k] = [str(item).strip() for item in v if str(item).strip()]
                return result
        except json.JSONDecodeError as exc:
            logger.warning("[Academic] Response JSON decode failed: %s", exc)

        # Regex fallback for JSON objects in text
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, dict):
                    result = {}
                    for k, v in parsed.items():
                        if isinstance(v, list):
                            result[k] = [str(item).strip() for item in v if str(item).strip()]
                    return result
            except json.JSONDecodeError:
                pass

        raise MalformedExtractionJSONError(f"Failed to parse LLM extraction JSON: {raw_response[:200]}")
