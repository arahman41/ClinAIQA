"""
Single entry point for all Claude API calls.
Retry, timeout, and structured-output parsing live here.
No other module calls the Anthropic client directly.
"""
import json
import time
from typing import Any

import anthropic

from clinaiqa.settings import settings

_DEFAULT_MODEL = "claude-sonnet-4-6"
_MAX_RETRIES = 3
_RETRY_DELAY_S = 2.0


class LLMError(Exception):
    """Raised when the LLM call fails after all retries or returns unparseable output."""


class ClinAIQALLMClient:
    def __init__(self) -> None:
        if not settings.anthropic_api_key:
            raise LLMError("ANTHROPIC_API_KEY is not set. Check your .env or environment.")
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def score(self, prompt: str, *, model: str = _DEFAULT_MODEL, max_tokens: int = 1024) -> dict[str, Any]:
        """Send a scoring prompt and return a parsed JSON dict.

        Retries up to _MAX_RETRIES times on transient errors.
        On parse failure raises LLMError (fail toward flagging, never silent pass).
        """
        last_exc: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                message = self._client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                raw = message.content[0].text
                return self._parse_json(raw)
            except anthropic.APIStatusError as exc:
                if exc.status_code < 500:
                    raise LLMError(f"LLM call failed with non-retryable status {exc.status_code}: {exc}") from exc
                last_exc = exc
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_DELAY_S * attempt)
            except (anthropic.APIConnectionError, anthropic.RateLimitError) as exc:
                last_exc = exc
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_DELAY_S * attempt)
        raise LLMError(f"LLM call failed after {_MAX_RETRIES} attempts: {last_exc}") from last_exc

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any]:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise LLMError(f"Could not parse LLM response as JSON: {exc}\nRaw response: {raw!r}") from exc


_client: ClinAIQALLMClient | None = None


def get_client() -> ClinAIQALLMClient:
    """Return the singleton LLM client, constructing it on first call."""
    global _client
    if _client is None:
        _client = ClinAIQALLMClient()
    return _client
