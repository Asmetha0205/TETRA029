"""
Prompt Builder for CurricuAlign AI LLM Technology Intelligence Engine.
Constructs zero-hallucination system and user prompts for Gemini technology extraction.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("industry_engine.processing.llm.prompt_builder")

# All 18 valid technology category keys expected in LLM output
VALID_CATEGORIES = [
    "languages",
    "frameworks",
    "libraries",
    "databases",
    "cloud",
    "devops",
    "ai",
    "vector_databases",
    "llm_frameworks",
    "agent_frameworks",
    "operating_systems",
    "developer_tools",
    "version_control",
    "message_brokers",
    "container_technologies",
    "infrastructure_tools",
    "monitoring_tools",
    "testing_frameworks",
]

SYSTEM_PROMPT = """You are a Technology Extraction Engine.

Your ONLY task is to extract technology names that EXPLICITLY appear in the provided job description text.

STRICT RULES — VIOLATION OF ANY RULE IS A CRITICAL FAILURE:

1. Extract ONLY technologies that are explicitly mentioned by name in the job description text.
2. NEVER infer, guess, or assume any technology that is not explicitly written.
3. NEVER expand abbreviations unless the expanded form is explicitly written in the text.
4. NEVER recommend technologies.
5. NEVER summarize the job description.
6. NEVER explain your reasoning.
7. NEVER add commentary, notes, or additional text.
8. NEVER generate technologies based on context clues or implications.
9. If a technology is not explicitly mentioned by exact name, DO NOT include it.
10. Return ONLY valid JSON. No markdown. No code fences. No explanations.

OUTPUT FORMAT:
Return a single JSON object with exactly these category keys:
{
    "languages": [],
    "frameworks": [],
    "libraries": [],
    "databases": [],
    "cloud": [],
    "devops": [],
    "ai": [],
    "vector_databases": [],
    "llm_frameworks": [],
    "agent_frameworks": [],
    "operating_systems": [],
    "developer_tools": [],
    "version_control": [],
    "message_brokers": [],
    "container_technologies": [],
    "infrastructure_tools": [],
    "monitoring_tools": [],
    "testing_frameworks": []
}

Each category value MUST be a JSON array of strings.
If no technologies are found for a category, return an empty array [].
Do NOT add any categories beyond those listed above.
Do NOT nest objects inside arrays — only plain string values.
"""


class PromptBuilder:
    """
    Constructs structured prompts for Gemini technology extraction.
    """

    def __init__(self):
        self._system_prompt = SYSTEM_PROMPT

    @property
    def system_prompt(self) -> str:
        """Return the system prompt."""
        return self._system_prompt

    def build_user_prompt(
        self,
        job_id: str,
        title: str,
        company: str,
        location: str,
        clean_description: str,
    ) -> str:
        """
        Build the user prompt containing the job posting details.

        Args:
            job_id: Unique job identifier.
            title: Normalized job title.
            company: Hiring company name.
            location: Job location.
            clean_description: Cleaned and normalized job description text.

        Returns:
            Formatted user prompt string.
        """
        user_prompt = (
            f"Extract all explicitly mentioned technologies from the following job posting.\n\n"
            f"Job ID: {job_id}\n"
            f"Job Title: {title}\n"
            f"Company: {company}\n"
            f"Location: {location}\n\n"
            f"--- JOB DESCRIPTION START ---\n"
            f"{clean_description}\n"
            f"--- JOB DESCRIPTION END ---\n\n"
            f"Return ONLY the JSON object with the extracted technologies. No other text."
        )

        logger.debug(
            f"[PromptBuilder] Built user prompt for job_id='{job_id}' "
            f"(description length={len(clean_description)} chars)"
        )
        return user_prompt

    def build_full_prompt(
        self,
        job_id: str,
        title: str,
        company: str,
        location: str,
        clean_description: str,
    ) -> Dict[str, Any]:
        """
        Build the complete prompt payload for the Gemini API.

        Returns:
            Dictionary with 'system_prompt' and 'user_prompt' keys.
        """
        user_prompt = self.build_user_prompt(
            job_id=job_id,
            title=title,
            company=company,
            location=location,
            clean_description=clean_description,
        )

        return {
            "system_prompt": self._system_prompt,
            "user_prompt": user_prompt,
        }
