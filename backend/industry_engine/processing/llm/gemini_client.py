"""
Gemini API Client for CurricuAlign AI LLM Technology Intelligence Engine.
Handles Gemini API interaction with retries, exponential backoff, timeout, and telemetry.
"""

import json
import logging
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Callable

from backend.industry_engine.processing.llm.models import LLMConfig, LLMExecutionStats

logger = logging.getLogger("industry_engine.processing.llm.gemini_client")


class GeminiAPIError(Exception):
    """Raised when the Gemini API returns an unrecoverable error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class GeminiClient:
    """
    HTTP client for Google Gemini API with retry logic, exponential backoff,
    timeout handling, and token usage telemetry.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    # HTTP status codes that are retryable
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(self, config: Optional[LLMConfig] = None, mock_response_fn: Optional[Callable] = None):
        """
        Initialize the Gemini client.

        Args:
            config: LLM configuration. Uses defaults if None.
            mock_response_fn: Optional callable that accepts (system_prompt, user_prompt)
                              and returns a mock response string. Used for testing.
        """
        self._config = config or LLMConfig()
        self._mock_response_fn = mock_response_fn

        if not self._mock_response_fn and not self._config.api_key:
            logger.warning(
                "[GeminiClient] No API key configured. Set GEMINI_API_KEY environment variable "
                "or pass api_key in LLMConfig."
            )

    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Send a prompt to Gemini and return the response with execution stats.

        Args:
            system_prompt: System instruction prompt.
            user_prompt: User prompt with job description.

        Returns:
            Dictionary with keys:
                - 'text': Raw response text from Gemini.
                - 'stats': LLMExecutionStats object.

        Raises:
            GeminiAPIError: On unrecoverable API errors after all retries.
            ValueError: If API key is missing and no mock is configured.
        """
        # Use mock if configured
        if self._mock_response_fn:
            return self._generate_mock(system_prompt, user_prompt)

        if not self._config.api_key:
            raise ValueError(
                "Gemini API key is required. Set GEMINI_API_KEY environment variable "
                "or pass api_key in LLMConfig."
            )

        return self._generate_with_retries(system_prompt, user_prompt)

    def _generate_mock(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Generate a response using the mock function for testing.
        """
        start = time.time()
        response_text = self._mock_response_fn(system_prompt, user_prompt)
        elapsed_ms = round((time.time() - start) * 1000, 2)

        stats = LLMExecutionStats(
            prompt_tokens=len(system_prompt.split()) + len(user_prompt.split()),
            completion_tokens=len(response_text.split()),
            total_tokens=len(system_prompt.split()) + len(user_prompt.split()) + len(response_text.split()),
            latency_ms=elapsed_ms,
            retry_count=0,
            cache_hit=False,
        )

        logger.info(f"[GeminiClient] Mock response generated in {elapsed_ms}ms")
        return {"text": response_text, "stats": stats}

    def _generate_with_retries(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Execute the Gemini API call with exponential backoff retry logic.
        """
        url = (
            f"{self.BASE_URL}/{self._config.model_name}:generateContent"
            f"?key={self._config.api_key}"
        )

        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": self._config.temperature,
                "maxOutputTokens": self._config.max_tokens,
                "responseMimeType": "application/json",
            },
        }

        payload_bytes = json.dumps(payload).encode("utf-8")
        last_error: Optional[Exception] = None
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
                    response_data = json.loads(resp.read().decode("utf-8"))

                elapsed_ms = round((time.time() - start) * 1000, 2)

                # Extract response text
                response_text = self._extract_text(response_data)

                # Extract token usage
                usage = response_data.get("usageMetadata", {})
                stats = LLMExecutionStats(
                    prompt_tokens=usage.get("promptTokenCount", 0),
                    completion_tokens=usage.get("candidatesTokenCount", 0),
                    total_tokens=usage.get("totalTokenCount", 0),
                    latency_ms=elapsed_ms,
                    retry_count=retry_count,
                    cache_hit=False,
                )

                logger.info(
                    f"[GeminiClient] API call succeeded: "
                    f"prompt_tokens={stats.prompt_tokens}, "
                    f"completion_tokens={stats.completion_tokens}, "
                    f"latency={stats.latency_ms}ms, "
                    f"retries={stats.retry_count}"
                )

                return {"text": response_text, "stats": stats}

            except urllib.error.HTTPError as e:
                elapsed_ms = round((time.time() - start) * 1000, 2)
                retry_count += 1
                last_error = e

                if e.code in self.RETRYABLE_STATUS_CODES and attempt < self._config.retry_count:
                    backoff = min(2 ** attempt, 30)
                    logger.warning(
                        f"[GeminiClient] HTTP {e.code} on attempt {attempt + 1}. "
                        f"Retrying in {backoff}s... ({elapsed_ms}ms elapsed)"
                    )
                    time.sleep(backoff)
                    continue
                else:
                    error_body = ""
                    try:
                        error_body = e.read().decode("utf-8", errors="replace")
                    except Exception:
                        pass
                    logger.error(
                        f"[GeminiClient] HTTP {e.code} after {attempt + 1} attempts: {error_body[:500]}"
                    )
                    raise GeminiAPIError(
                        f"Gemini API error HTTP {e.code}: {error_body[:200]}",
                        status_code=e.code,
                    ) from e

            except urllib.error.URLError as e:
                elapsed_ms = round((time.time() - start) * 1000, 2)
                retry_count += 1
                last_error = e

                if attempt < self._config.retry_count:
                    backoff = min(2 ** attempt, 30)
                    logger.warning(
                        f"[GeminiClient] Connection error on attempt {attempt + 1}: {e.reason}. "
                        f"Retrying in {backoff}s..."
                    )
                    time.sleep(backoff)
                    continue
                else:
                    logger.error(f"[GeminiClient] Connection failed after {attempt + 1} attempts: {e.reason}")
                    raise GeminiAPIError(f"Gemini connection error: {e.reason}") from e

            except TimeoutError as e:
                elapsed_ms = round((time.time() - start) * 1000, 2)
                retry_count += 1
                last_error = e

                if attempt < self._config.retry_count:
                    backoff = min(2 ** attempt, 30)
                    logger.warning(
                        f"[GeminiClient] Timeout ({self._config.timeout}s) on attempt {attempt + 1}. "
                        f"Retrying in {backoff}s..."
                    )
                    time.sleep(backoff)
                    continue
                else:
                    logger.error(f"[GeminiClient] Timeout after {attempt + 1} attempts.")
                    raise GeminiAPIError(
                        f"Gemini API timeout after {self._config.timeout}s"
                    ) from e

        # Should not reach here, but handle edge cases
        raise GeminiAPIError(f"All {self._config.retry_count + 1} attempts failed: {last_error}")

    def _extract_text(self, response_data: Dict[str, Any]) -> str:
        """
        Extract the generated text from the Gemini API response structure.
        """
        try:
            candidates = response_data.get("candidates", [])
            if not candidates:
                raise GeminiAPIError("Gemini response contains no candidates.")

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                raise GeminiAPIError("Gemini response candidate contains no content parts.")

            return parts[0].get("text", "")

        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"[GeminiClient] Failed to extract text from response: {e}")
            raise GeminiAPIError(f"Malformed Gemini response structure: {e}") from e
