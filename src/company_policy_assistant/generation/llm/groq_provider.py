import os

from groq import Groq

from .base import LLMProvider

DEFAULT_MODEL = "llama-3.3-70b-versatile"


class GroqProvider(LLMProvider):
    def __init__(self, model: str | None = None, api_key: str | None = None):
        self._client = Groq(api_key=api_key or os.environ["GROQ_API_KEY"])
        self._model = model or os.environ.get("GROQ_MODEL", DEFAULT_MODEL)

    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.0) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content
