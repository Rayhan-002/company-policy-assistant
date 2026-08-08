import os

from google import genai
from google.genai import types

from .base import LLMProvider

DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiProvider(LLMProvider):
    def __init__(self, model: str | None = None, api_key: str | None = None):
        self._client = genai.Client(api_key=api_key or os.environ["GEMINI_API_KEY"])
        self._model = model or os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)

    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.0) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
            ),
        )
        return response.text
