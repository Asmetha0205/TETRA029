# LLM Recommendation Engine

Interacts with Google Gemini API to produce grounded JSON curriculum recommendations.

## Features
- Gemini API client with retries, exponential backoff, token telemetry, and mock fallback.
- Response parser stripping markdown fences (` ```json `) and enforcing JSON compliance.
- Strict validator checking non-hallucinated technology lists and confidence bounds.
- Full execution stats logging (`[LLM] Recommendations Generated`).
