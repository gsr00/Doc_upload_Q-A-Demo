"""Centralized LLM gateway.

All model calls flow through this module so we can swap providers, add logging,
caching, or safety checks in one place.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests
from dotenv import load_dotenv

# Load environment variables from a local .env file if present
load_dotenv()


@dataclass
class LLMResponse:
    content: str


def get_api_key() -> str | None:
    """Fetch API key from environment variables."""
    return os.getenv("OPENAI_API_KEY")


def get_default_model() -> str:
    """Allow environment override for model; default to gpt-4o-mini."""
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _build_messages(user_prompt: str, system_prompt: str | None) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    return messages


def generate_text(
    prompt: str,
    model: str | None = None,
    system: str | None = None,
    max_tokens: int = 350,
) -> LLMResponse:
    """
    Call the OpenAI-compatible chat completions API.

    Args:
        prompt: User message content.
        model: Optional model id; defaults to env OPENAI_MODEL or gpt-4o-mini if not provided.
        system: Optional system persona to prepend.
        max_tokens: Cap on generated tokens.
    """
    api_key = get_api_key()
    if not api_key:
        return LLMResponse(
            content="OpenAI API key is missing. Set OPENAI_API_KEY in your .env file."
        )

    endpoint = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1/chat/completions")
    model_name = model or get_default_model()

    payload = {
        "model": model_name,
        "messages": _build_messages(prompt, system),
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }

    try:
        resp = requests.post(
            endpoint,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return LLMResponse(content=content)
    except Exception as exc:  # Pragmatic catch-all for network/API issues
        return LLMResponse(
            content=f"LLM call failed: {exc}. Please retry or check your API key/settings."
        )
