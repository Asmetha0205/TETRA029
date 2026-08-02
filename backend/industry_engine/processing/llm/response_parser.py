"""
Response Parser for CurricuAlign AI LLM Technology Intelligence Engine.
Converts raw Gemini LLM responses into validated TechnologyExtraction objects.
"""

import json
import logging
import re
from typing import Optional, Dict, Any, List

from backend.industry_engine.processing.llm.models import (
    TechnologyExtraction,
    TechnologyCategories,
    LLMExecutionStats,
)
from backend.industry_engine.processing.llm.validator import ExtractionValidator

logger = logging.getLogger("industry_engine.processing.llm.response_parser")


class ResponseParser:
    """
    Parses raw LLM text responses into structured, validated TechnologyExtraction objects.
    Handles markdown code fences, JSON extraction, validation, and model construction.
    """

    def __init__(self, strict_presence_check: bool = True):
        self._validator = ExtractionValidator(strict_presence_check=strict_presence_check)

    def strip_markdown_fences(self, raw_text: str) -> str:
        """
        Remove markdown code block wrappers (```json ... ``` or ``` ... ```) from LLM output.
        """
        text = raw_text.strip()

        # Pattern: ```json\n...\n``` or ```\n...\n```
        pattern = r"^```(?:json)?\s*\n?(.*?)\n?\s*```$"
        match = re.match(pattern, text, re.DOTALL)
        if match:
            text = match.group(1).strip()

        return text

    def extract_json_from_text(self, raw_text: str) -> str:
        """
        Extract the first valid JSON object from potentially messy LLM output.
        Falls back to the full stripped text if no brace-delimited block is found.
        """
        cleaned = self.strip_markdown_fences(raw_text)

        # Try to find the outermost { ... } block
        brace_start = cleaned.find("{")
        brace_end = cleaned.rfind("}")
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            return cleaned[brace_start : brace_end + 1]

        return cleaned

    def parse_json(self, raw_text: str) -> Dict[str, Any]:
        """
        Parse raw LLM output text into a Python dictionary.

        Raises:
            ValueError: If the text cannot be parsed as valid JSON.
        """
        json_str = self.extract_json_from_text(raw_text)
        try:
            parsed = json.loads(json_str)
            if not isinstance(parsed, dict):
                raise ValueError(f"Expected JSON object (dict), got {type(parsed).__name__}")
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"[ResponseParser] JSON parsing failed: {e}")
            logger.debug(f"[ResponseParser] Raw text was: {raw_text[:500]}")
            raise ValueError(f"Failed to parse LLM response as JSON: {e}") from e

    def parse_response(
        self,
        raw_text: str,
        job_id: str,
        source_text: str,
        stats: Optional[LLMExecutionStats] = None,
    ) -> TechnologyExtraction:
        """
        Full response parsing pipeline: strip → parse JSON → validate → build model.

        Args:
            raw_text: Raw text response from Gemini LLM.
            job_id: Job identifier for the extraction.
            source_text: Original cleaned job description (for hallucination pruning).
            stats: Optional LLM execution statistics.

        Returns:
            Validated TechnologyExtraction object.

        Raises:
            ValueError: If parsing or validation fails irrecoverably.
        """
        logger.info(f"[ResponseParser] Parsing response for job_id='{job_id}' ({len(raw_text)} chars)")

        # Step 1: Parse JSON
        parsed = self.parse_json(raw_text)

        # Step 2: Handle nested "technologies" key if present
        if "technologies" in parsed and isinstance(parsed["technologies"], dict):
            tech_data = parsed["technologies"]
        else:
            tech_data = parsed

        # Step 3: Validate and clean
        cleaned_data, removed, warnings = self._validator.validate_and_clean(
            data=tech_data,
            source_text=source_text,
        )

        for w in warnings:
            logger.warning(f"[ResponseParser] Validation warning: {w}")

        # Step 4: Build TechnologyCategories model
        categories = TechnologyCategories(**cleaned_data)

        # Step 5: Build TechnologyExtraction result
        extraction = TechnologyExtraction(
            job_id=job_id,
            technologies=categories,
            stats=stats,
        )

        total_techs = sum(len(v) for v in cleaned_data.values())
        logger.info(
            f"[ResponseParser] Extraction complete for job_id='{job_id}': "
            f"{total_techs} technologies across {sum(1 for v in cleaned_data.values() if v)} categories. "
            f"{len(removed)} hallucinations pruned."
        )

        return extraction
