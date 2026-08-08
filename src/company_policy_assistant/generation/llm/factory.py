import os

from .base import LLMProvider
from .gemini_provider import GeminiProvider
from .groq_provider import GroqProvider

_PROVIDERS: dict[str, type[LLMProvider]] = {
    "groq": GroqProvider,
    "gemini": GeminiProvider,
}


def get_llm_provider(name: str | None = None) -> LLMProvider:
    name = (name or os.environ.get("LLM_PROVIDER", "groq")).lower()
    try:
        provider_cls = _PROVIDERS[name]
    except KeyError:
        raise ValueError(f"Unknown LLM provider '{name}'. Available: {sorted(_PROVIDERS)}") from None
    return provider_cls()
