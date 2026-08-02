"""
Grounded Prompt Builder for Recommendation Intelligence Layer.
Combines GapAnalysisResult + Neo4j Evidence + Industry & Academic Knowledge
into strict, evidence-bound LLM prompts.
"""

import json
from typing import Any, Dict, List, Optional
from backend.recommendation_engine.prompt.prompt_templates import (
    SYSTEM_RECOMMENDATION_PROMPT,
    USER_RECOMMENDATION_PROMPT_TEMPLATE,
)
from backend.recommendation_engine.prompt.prompt_validator import PromptValidator, PromptValidationResult
from backend.recommendation_engine.utils.logger import prompt_logger


class GroundedPromptBuilder:
    """
    Constructs grounded system and user prompts for Gemini LLM.
    Inputs: GapAnalysisResult + Neo4j Evidence + Industry Knowledge + Academic Knowledge.
    """

    def build_recommendation_prompt(
        self,
        gap_analysis_data: Dict[str, Any],
        evidence_data: List[Dict[str, Any]],
        knowledge_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Build system and user prompt pair.
        """
        prompt_logger.info("Generating Grounded Recommendation Prompt...")

        gap_json_str = json.dumps(gap_analysis_data, indent=2)
        evidence_json_str = json.dumps(evidence_data, indent=2)
        knowledge_json_str = json.dumps(knowledge_context or {}, indent=2)

        user_prompt = USER_RECOMMENDATION_PROMPT_TEMPLATE.format(
            gap_analysis_json=gap_json_str,
            evidence_json=evidence_json_str,
            knowledge_context_json=knowledge_json_str
        )

        validation = PromptValidator.validate_prompt(SYSTEM_RECOMMENDATION_PROMPT, user_prompt)
        if not validation.is_valid:
            prompt_logger.error(f"Prompt generation resulted in validation errors: {validation.errors}")
            raise ValueError(f"Invalid prompt built: {validation.errors}")

        prompt_logger.info(f"Prompt Generated successfully (System: {len(SYSTEM_RECOMMENDATION_PROMPT)} chars, User: {len(user_prompt)} chars)")
        return {
            "system_prompt": SYSTEM_RECOMMENDATION_PROMPT,
            "user_prompt": user_prompt
        }
