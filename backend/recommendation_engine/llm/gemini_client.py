"""
Gemini API Client for Recommendation Intelligence Layer.
Interacts with Google Gemini REST API with exponential backoff, timeout handling,
mock response fallbacks, and token usage telemetry.
"""

import json
import time
import urllib.request
import urllib.error
from typing import Any, Dict, Optional, Callable
from pydantic import BaseModel, Field
from backend.recommendation_engine.config.config import LLMRecommendationConfig, config as default_config
from backend.recommendation_engine.utils.logger import llm_logger


class LLMExecutionStats(BaseModel):
    """Execution statistics for LLM call."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    retry_count: int = 0
    mock_used: bool = False


class GeminiAPIError(Exception):
    """Raised when Gemini API fails unrecoverably."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class GeminiClient:
    """
    HTTP client for Google Gemini API with retries, exponential backoff,
    and mock fallback for offline/test environments.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(
        self,
        config: Optional[LLMRecommendationConfig] = None,
        mock_response_fn: Optional[Callable[[str, str], str]] = None
    ):
        self._config = config or default_config.llm
        self._mock_response_fn = mock_response_fn

        if not self._mock_response_fn and not self._config.api_key:
            llm_logger.warning("No GEMINI_API_KEY set. Dynamic mock fallback will be used if API key is absent.")

    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Execute LLM generation request.
        """
        if self._mock_response_fn:
            return self._generate_mock(system_prompt, user_prompt)

        if not self._config.api_key:
            llm_logger.info("Using internal fallback generator because GEMINI_API_KEY is not configured.")
            return self._generate_internal_fallback(system_prompt, user_prompt)

        return self._generate_with_retries(system_prompt, user_prompt)

    def _generate_mock(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        start = time.time()
        text = self._mock_response_fn(system_prompt, user_prompt)
        latency = round((time.time() - start) * 1000, 2)
        stats = LLMExecutionStats(
            prompt_tokens=len(system_prompt.split()) + len(user_prompt.split()),
            completion_tokens=len(text.split()),
            total_tokens=len(system_prompt.split()) + len(user_prompt.split()) + len(text.split()),
            latency_ms=latency,
            retry_count=0,
            mock_used=True,
        )
        llm_logger.info(f"Mock response generated in {latency}ms")
        return {"text": text, "stats": stats}

    def _generate_internal_fallback(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Synthesize a valid JSON recommendation payload from input user prompt evidence when offline."""
        start = time.time()
        
        # Check which default technologies are mentioned in the evidence prompt
        all_defaults = [
            {
                "technology": "Redis",
                "priority": "High",
                "industry_score": 91,
                "trend": "Rising",
                "reason": "Redis appears frequently in backend industry roles requiring high-performance caching.",
                "recommended_course": "Advanced Backend Systems",
                "recommended_module": "Caching & Distributed Systems",
                "learning_outcomes": [
                    "Understand in-memory caching strategies and eviction policies",
                    "Implement Redis key-value store in FastAPI web microservices"
                ],
                "lab": "Implement Redis cache in FastAPI.",
                "mini_project": "Distributed API Cache System",
                "learning_path": ["Docker", "Redis", "FastAPI", "Kubernetes"],
                "references": ["Neo4j Industry Intelligence", "Backend Engineering Matrix 2026"],
                "confidence": 0.94
            },
            {
                "technology": "Docker",
                "priority": "Critical",
                "industry_score": 90,
                "trend": "Rising",
                "reason": "Docker containerization is a foundational prerequisite for cloud deployments.",
                "recommended_course": "Cloud Infrastructure & DevOps",
                "recommended_module": "Containerization & Orchestration",
                "learning_outcomes": [
                    "Build multi-stage Dockerfiles for Python applications",
                    "Manage container networks and volumes"
                ],
                "lab": "Containerize a REST API with Docker Compose.",
                "mini_project": "Containerized Microservice Suite",
                "learning_path": ["SQL", "Docker", "Kubernetes"],
                "references": ["DevOps Role Standard 2026"],
                "confidence": 0.92
            },
            {
                "technology": "FastAPI",
                "priority": "High",
                "industry_score": 89,
                "trend": "Rapidly Growing",
                "reason": "FastAPI is the leading modern Python web framework for asynchronous API design.",
                "recommended_course": "Web Microservices & APIs",
                "recommended_module": "Asynchronous REST Services",
                "learning_outcomes": [
                    "Build high-throughput REST APIs with Pydantic validation",
                    "Implement OpenAPI spec documentation"
                ],
                "lab": "Build async CRUD endpoints with FastAPI.",
                "mini_project": "High-Throughput API Gateway",
                "learning_path": ["Python", "FastAPI"],
                "references": ["Modern Python Web Standards"],
                "confidence": 0.91
            }
        ]

        matched_recs = []
        evidence_block = user_prompt
        if "NEO4J GRAPH EVIDENCE:" in user_prompt:
            start_idx = user_prompt.find("NEO4J GRAPH EVIDENCE:")
            end_idx = user_prompt.find("INSTRUCTIONS:")
            if end_idx > start_idx:
                evidence_block = user_prompt[start_idx:end_idx]

        for default_item in all_defaults:
            tech = default_item["technology"]
            if tech.lower() in evidence_block.lower():
                matched_recs.append(default_item)

        if not matched_recs:
            matched_recs = all_defaults[:1]

        fallback_json = {"recommendations": matched_recs}
        text = json.dumps(fallback_json, indent=2)
        latency = round((time.time() - start) * 1000, 2)
        stats = LLMExecutionStats(
            prompt_tokens=150,
            completion_tokens=200,
            total_tokens=350,
            latency_ms=latency,
            mock_used=True,
        )
        llm_logger.info(f"Internal fallback response generated in {latency}ms for {len(matched_recs)} techs")
        return {"text": text, "stats": stats}

    def _generate_with_retries(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{self._config.model_name}:generateContent?key={self._config.api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": self._config.temperature,
                "maxOutputTokens": self._config.max_tokens,
                "responseMimeType": "application/json",
            },
        }

        payload_bytes = json.dumps(payload).encode("utf-8")
        last_error = None
        retry_count = 0

        for attempt in range(self._config.retry_count + 1):
            start = time.time()
            try:
                req = urllib.request.Request(
                    url,
                    data=payload_bytes,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=self._config.timeout) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))

                latency = round((time.time() - start) * 1000, 2)
                text = self._extract_text(resp_data)
                usage = resp_data.get("usageMetadata", {})

                stats = LLMExecutionStats(
                    prompt_tokens=usage.get("promptTokenCount", 0),
                    completion_tokens=usage.get("candidatesTokenCount", 0),
                    total_tokens=usage.get("totalTokenCount", 0),
                    latency_ms=latency,
                    retry_count=retry_count,
                    mock_used=False,
                )
                llm_logger.info(f"Gemini API call succeeded in {latency}ms")
                return {"text": text, "stats": stats}

            except urllib.error.HTTPError as e:
                retry_count += 1
                last_error = e
                if e.code in self.RETRYABLE_STATUS_CODES and attempt < self._config.retry_count:
                    backoff = min(2 ** attempt, 10)
                    llm_logger.warning(f"HTTP {e.code} on attempt {attempt + 1}. Retrying in {backoff}s...")
                    time.sleep(backoff)
                else:
                    llm_logger.error(f"HTTP {e.code} unrecoverable error.")
                    raise GeminiAPIError(f"Gemini API Error {e.code}", status_code=e.code) from e

            except Exception as e:
                retry_count += 1
                last_error = e
                if attempt < self._config.retry_count:
                    backoff = min(2 ** attempt, 10)
                    llm_logger.warning(f"Connection error ({e}) on attempt {attempt + 1}. Retrying in {backoff}s...")
                    time.sleep(backoff)
                else:
                    llm_logger.error(f"Gemini call failed after {attempt + 1} attempts.")
                    raise GeminiAPIError(f"Gemini API failure: {e}") from e

        raise GeminiAPIError(f"All attempts failed: {last_error}")

    def _extract_text(self, resp_data: Dict[str, Any]) -> str:
        candidates = resp_data.get("candidates", [])
        if not candidates:
            raise GeminiAPIError("No candidates returned from Gemini API.")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise GeminiAPIError("No parts returned in Gemini candidate content.")
        return parts[0].get("text", "")
