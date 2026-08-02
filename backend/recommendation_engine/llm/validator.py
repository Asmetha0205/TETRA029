"""
LLM Output Grounding Validator.
Validates LLM recommendation JSON output against grounded evidence requirements.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.recommendation_engine.utils.logger import llm_logger


class LLMValidationResult(BaseModel):
    """Result of LLM output validation."""
    is_valid: bool = True
    total_recommendations: int = 0
    errors: List[str] = Field(default_factory=list)


class LLMOutputValidator:
    """
    Validates parsed LLM JSON output to enforce non-hallucination,
    required output keys, and score bounds.
    """

    REQUIRED_KEYS = [
        "technology",
        "priority",
        "industry_score",
        "trend",
        "reason",
        "recommended_course",
        "recommended_module",
        "learning_outcomes",
        "lab",
        "mini_project",
        "learning_path",
        "references",
        "confidence",
    ]

    @classmethod
    def validate_parsed_json(cls, parsed_payload: Dict[str, Any], allowed_technologies: Optional[List[str]] = None) -> LLMValidationResult:
        """
        Validate parsed recommendation JSON payload.
        """
        errors: List[str] = []
        recs = parsed_payload.get("recommendations", [])

        if not isinstance(recs, list) or len(recs) == 0:
            errors.append("Output JSON does not contain a non-empty 'recommendations' array.")
            return LLMValidationResult(is_valid=False, errors=errors)

        allowed_set = {t.lower() for t in allowed_technologies} if allowed_technologies else None

        for idx, item in enumerate(recs):
            if not isinstance(item, dict):
                errors.append(f"Recommendation item at index {idx} is not a dictionary.")
                continue

            for key in cls.REQUIRED_KEYS:
                if key not in item:
                    errors.append(f"Item {idx} ({item.get('technology', 'Unknown')}) missing required key: '{key}'")

            tech = item.get("technology", "")
            if allowed_set and tech.lower() not in allowed_set:
                errors.append(f"Ungrounded technology '{tech}' not present in provided gap evidence list!")

            conf = item.get("confidence", 0.0)
            if not (0.0 <= conf <= 1.0):
                errors.append(f"Confidence score {conf} for '{tech}' out of bounds [0.0, 1.0]")

        is_valid = len(errors) == 0
        if is_valid:
            llm_logger.info(f"LLM Output Grounding Passed cleanly for {len(recs)} recommendations.")
        else:
            llm_logger.warning(f"LLM Output Grounding Validation Warnings/Errors: {errors}")

        return LLMValidationResult(
            is_valid=is_valid,
            total_recommendations=len(recs),
            errors=errors
        )
