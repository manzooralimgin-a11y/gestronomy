import json
import logging
from typing import Any

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.default_model = "claude-sonnet-4-20250514"

    async def ask(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        try:
            kwargs: dict[str, Any] = {
                "model": self.default_model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system:
                kwargs["system"] = system
            response = await self.client.messages.create(**kwargs)
            return response.content[0].text
        except anthropic.APIError as e:
            logger.error("Anthropic API error: %s", e)
            raise
        except Exception as e:
            logger.error("LLM request failed: %s", e)
            raise

    async def analyze(self, data: dict[str, Any], instruction: str) -> dict[str, Any]:
        prompt = (
            f"{instruction}\n\n"
            f"Data:\n```json\n{json.dumps(data, default=str)}\n```\n\n"
            "Respond with valid JSON only, no markdown fences."
        )
        try:
            raw = await self.ask(prompt, max_tokens=2048)
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM JSON response: %s", e)
            return {"error": "Failed to parse response", "raw": raw}


llm = LLMClient()
