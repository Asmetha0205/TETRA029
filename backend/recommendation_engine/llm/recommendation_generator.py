"""
Recommendation Generator for LLM Module.
Coordinates prompt creation, Gemini API invocation, response parsing, and grounding validation.
"""

from typing import Any, Dict, List, Optional
from backend.recommendation_engine.llm.gemini_client import GeminiClient, LLMExecutionStats
from backend.recommendation_engine.llm.response_parser import LLMResponseParser
from backend.recommendation_engine.llm.validator import LLMOutputValidator
from backend.recommendation_engine.prompt.prompt_builder import GroundedPromptBuilder
from backend.recommendation_engine.utils.logger import llm_logger


class LLMRecommendationGenerator:
    """
    Generates evidence-grounded recommendations using Google Gemini LLM.
    """

    def __init__(self, client: Optional[GeminiClient] = None):
        self.client = client or GeminiClient()
        self.prompt_builder = GroundedPromptBuilder()

    def generate_recommendations(
        self,
        gap_analysis_data: Dict[str, Any],
        evidence_data: List[Dict[str, Any]],
        knowledge_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate grounded recommendations from evidence.
        """
        llm_logger.info("Initiating Recommendations Generation via Gemini LLM...")

        # 1. Build prompt
        prompt_pair = self.prompt_builder.build_recommendation_prompt(
            gap_analysis_data=gap_analysis_data,
            evidence_data=evidence_data,
            knowledge_context=knowledge_context
        )

        # 2. Invoke Gemini API
        llm_result = self.client.generate(
            system_prompt=prompt_pair["system_prompt"],
            user_prompt=prompt_pair["user_prompt"]
        )

        raw_text = llm_result["text"]
        stats: LLMExecutionStats = llm_result["stats"]

        # 3. Parse JSON
        parsed_data = LLMResponseParser.parse_recommendations_json(raw_text)

        # 4. Validate output grounding
        gap_tech_names = [e.get("tech_name", e.get("technology", "")) for e in evidence_data if "tech_name" in e or "technology" in e]
        val_result = LLMOutputValidator.validate_parsed_json(parsed_data, allowed_technologies=gap_tech_names)

        llm_logger.info(
            f"Recommendations Generated: count={len(parsed_data.get('recommendations', []))}, "
            f"latency={stats.latency_ms}ms, valid={val_result.is_valid}"
        )

        return {
            "payload": parsed_data,
            "stats": stats,
            "validation": val_result
        }
