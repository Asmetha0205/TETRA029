"""
Prompt Validator for Grounded Prompt Builder.
Validates prompt string integrity, placeholder substitution completeness,
and evidence grounding requirements.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.recommendation_engine.utils.logger import prompt_logger


class PromptValidationResult(BaseModel):
    """Validation report for a generated prompt."""
    is_valid: bool = True
    system_prompt_length: int = 0
    user_prompt_length: int = 0
    missing_variables: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class PromptValidator:
    """
    Validates generated prompts to ensure no unpopulated variables exist
    and that supplied evidence payloads are present.
    """

    REQUIRED_SUBSTITUTIONS = ["gap_analysis_json", "evidence_json", "knowledge_context_json"]

    @classmethod
    def validate_prompt(cls, system_prompt: str, user_prompt: str) -> PromptValidationResult:
        """Validate prompt structure."""
        errors: List[str] = []
        missing_vars: List[str] = []

        if not system_prompt or len(system_prompt.strip()) < 20:
            errors.append("System prompt is empty or too short.")

        if not user_prompt or len(user_prompt.strip()) < 20:
            errors.append("User prompt is empty or too short.")

        for var in cls.REQUIRED_SUBSTITUTIONS:
            placeholder = f"{{{var}}}"
            if placeholder in user_prompt:
                missing_vars.append(var)
                errors.append(f"Unsubstituted variable remaining in prompt: {placeholder}")

        is_valid = len(errors) == 0
        res = PromptValidationResult(
            is_valid=is_valid,
            system_prompt_length=len(system_prompt),
            user_prompt_length=len(user_prompt),
            missing_variables=missing_vars,
            errors=errors
        )

        if not is_valid:
            prompt_logger.warning(f"Prompt Validation Failed: {errors}")
        else:
            prompt_logger.info("Prompt Validation Passed cleanly.")
        return res
