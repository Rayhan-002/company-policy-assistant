from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Provider-agnostic interface for grounded-answer generation.

    The RAG pipeline talks to this interface only, never to a specific
    vendor SDK — free-tier availability/terms shift, so swapping providers
    should never require touching retrieval or prompt-building code.
    """

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.0) -> str:
        """Generate a response for a single-turn system+user prompt pair."""
