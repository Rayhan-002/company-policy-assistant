import re
import time

from ..generation import LLMProvider

_RETRY_DELAY_RE = re.compile(r"retryDelay['\"]?\s*[:=]\s*['\"]?(\d+(?:\.\d+)?)s")


def _extract_retry_delay(error: Exception) -> float | None:
    match = _RETRY_DELAY_RE.search(str(error))
    return float(match.group(1)) if match else None


class RetryingLLMProvider(LLMProvider):
    """Wraps an LLMProvider with retry-on-failure for batch eval runs.

    Not used on interactive paths (chat.py, the API) — those should fail fast
    rather than silently stall a user-facing request for minutes. Honors a
    provider's stated retry-after delay (e.g. Gemini's `retryDelay`) when
    present in the error text, since free-tier rate limits are otherwise
    invisible to the caller until they fire.
    """

    def __init__(self, wrapped: LLMProvider, max_retries: int = 6, default_backoff_seconds: float = 15.0):
        self._wrapped = wrapped
        self._max_retries = max_retries
        self._default_backoff_seconds = default_backoff_seconds

    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.0) -> str:
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                return self._wrapped.generate(system_prompt, user_prompt, temperature=temperature)
            except Exception as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    delay = (_extract_retry_delay(e) or self._default_backoff_seconds * (attempt + 1)) + 1
                    print(f"    (call failed: {e}; retrying in {delay:.0f}s)")
                    time.sleep(delay)
        assert last_error is not None
        raise last_error
