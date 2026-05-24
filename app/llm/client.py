"""LLM provider abstraction for groq-compatible and OpenAI-compatible chat APIs."""

from __future__ import annotations

import logging
from typing import Any, Protocol

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """Provider interface for chat completion."""

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float,
        max_tokens: int,
        json_mode: bool = True,
    ) -> str:
        """Return assistant message content."""
        ...


class LLMError(Exception):
    """Raised when the LLM provider call fails."""


class ChatLLMClient:
    """Chat completions client for OpenAI-compatible APIs."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        if not self._settings.llm_api_key:
            raise LLMError(
                "LLM_API_KEY is not set. Add it to .env for live LLM calls."
            )
        from openai import OpenAI

        kwargs: dict[str, Any] = {"api_key": self._settings.llm_api_key}
        if self._settings.llm_base_url:
            kwargs["base_url"] = self._settings.llm_base_url
        self._client = OpenAI(**kwargs, timeout=self._settings.llm_timeout_seconds)

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float,
        max_tokens: int,
        json_mode: bool = True,
    ) -> str:
        create_kwargs: dict[str, Any] = {
            "model": self._settings.llm_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            create_kwargs["response_format"] = {"type": "json_object"}

        try:
            response = self._client.chat.completions.create(**create_kwargs)
        except Exception as exc:
            raise LLMError(f"LLM API call failed: {exc}") from exc

        content = response.choices[0].message.content
        if not content:
            raise LLMError("LLM returned empty content")
        return content


class GroqLLMClient(ChatLLMClient):
    """Groq chat client using OpenAI-compatible responses endpoint."""

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float,
        max_tokens: int,
        json_mode: bool = True,
    ) -> str:
        create_kwargs: dict[str, Any] = {
            "model": self._settings.llm_model,
            "input": messages,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        try:
            response = self._client.responses.create(**create_kwargs)
        except Exception as exc:
            raise LLMError(f"LLM API call failed: {exc}") from exc

        content = getattr(response, "output_text", None)
        if not content and hasattr(response, "output"):
            output = response.output
            if output and isinstance(output, list):
                first = output[0]
                if isinstance(first, dict) and first.get("content"):
                    content_items = first["content"]
                    if isinstance(content_items, list) and content_items:
                        content = content_items[0].get("text")
        if not content:
            raise LLMError("LLM returned empty content")
        return content


def get_llm_client(settings: Settings | None = None) -> LLMClient:
    """Factory for the configured LLM client."""
    settings = settings or get_settings()
    if settings.llm_base_url and "groq.com" in settings.llm_base_url:
        return GroqLLMClient(settings)
    return ChatLLMClient(settings)
