"""
Utility helper functions for Recommendation Intelligence Layer.
Includes async helpers, formatting routines, hashing, and dict cleanups.
"""

import asyncio
import json
import hashlib
from typing import Any, Dict, List, Optional, TypeVar

T = TypeVar("T")


def generate_id(prefix: str, content: str) -> str:
    """Generate a deterministic short hash ID for entities."""
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def clean_json_text(raw_text: str) -> str:
    """
    Clean LLM response string to extract valid JSON substring.
    Removes markdown code fences like ```json ... ```.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        # Remove opening fence
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def safe_json_loads(data: str, default: Optional[Any] = None) -> Any:
    """Safely parse JSON text without throwing uncaught exceptions."""
    try:
        cleaned = clean_json_text(data)
        return json.loads(cleaned)
    except Exception:
        return default if default is not None else {}


def calculate_confidence(
    industry_score: float,
    evidence_count: int,
    similarity_score: float = 1.0,
    max_score: float = 100.0
) -> float:
    """
    Calculate a normalized confidence score (0.0 to 1.0) based on
    industry demand, quantity of backing evidence, and semantic similarity.
    """
    norm_industry = min(max(industry_score / max_score, 0.0), 1.0)
    evidence_factor = min(evidence_count / 5.0, 1.0)
    norm_similarity = min(max(similarity_score, 0.0), 1.0)

    confidence = (norm_industry * 0.4) + (evidence_factor * 0.3) + (norm_similarity * 0.3)
    return round(min(max(confidence, 0.1), 0.99), 2)


async def run_in_parallel(tasks: List[Any]) -> List[Any]:
    """Execute async coroutines or tasks in parallel."""
    return await asyncio.gather(*tasks, return_exceptions=True)
