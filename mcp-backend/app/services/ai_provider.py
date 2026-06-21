"""Multi-provider AI chat layer.

Builds provider-correct request payloads and routes a chat completion across
the configured providers (Gemini + OpenAI-compatible: OpenRouter, Groq, xAI),
falling back to the next provider on failure.

Payload rules enforced here:
- Gemini: one ``Content`` object per turn, each with a single ``parts`` entry
  containing one ``text`` field. Never multiple ``text`` parts in one turn.
- OpenAI-compatible: ``messages`` is a flat list of objects with a string
  ``content`` (not a list), one object per turn.
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

DEFAULT_TIMEOUT = 60.0

# Turns coming from the API are normalized to {"role": "user"|"assistant", "content": str}.
_SKIP_CONTENTS = {"", "Selesai."}


def normalize_turns(history: List[Dict[str, Any]], message: str) -> List[Dict[str, str]]:
    """Flatten history + the new user message into clean {role, content} turns."""
    turns: List[Dict[str, str]] = []
    for item in history or []:
        content = str(item.get("content") or "").strip()
        if content in _SKIP_CONTENTS:
            continue
        role = "user" if item.get("role") == "user" else "assistant"
        turns.append({"role": role, "content": content})
    turns.append({"role": "user", "content": message})
    return turns


def build_openai_messages(
    turns: List[Dict[str, str]], system_prompt: Optional[str]
) -> List[Dict[str, str]]:
    """OpenAI-compatible payload: flat messages, string content, one per turn."""
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    for turn in turns:
        messages.append({"role": turn["role"], "content": turn["content"]})
    return messages


def build_gemini_contents(turns: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Gemini payload: one Content per turn, single text part each."""
    contents: List[Dict[str, Any]] = []
    for turn in turns:
        role = "user" if turn["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": turn["content"]}]})
    return contents


@dataclass
class OpenAICompatProvider:
    name: str
    api_key_env: str
    base_url: str
    model_env: str
    default_model: str
    extra_headers: Dict[str, str] = field(default_factory=dict)


# OpenAI-compatible providers, tried in this order after Gemini.
OPENAI_COMPAT_PROVIDERS: List[OpenAICompatProvider] = [
    OpenAICompatProvider(
        name="openrouter",
        api_key_env="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
        model_env="OPENROUTER_MODEL",
        default_model="openai/gpt-4o-mini",
    ),
    OpenAICompatProvider(
        name="groq",
        api_key_env="GROQ_API_KEY",
        base_url="https://api.groq.com/openai/v1",
        model_env="GROQ_MODEL",
        default_model="llama-3.3-70b-versatile",
    ),
    OpenAICompatProvider(
        name="xai",
        api_key_env="XAI_API_KEY",
        base_url="https://api.x.ai/v1",
        model_env="XAI_MODEL",
        default_model="grok-2-latest",
    ),
]


@dataclass
class AIResult:
    text: str
    provider: str
    status: str  # ONLINE | NOT_CONFIGURED | DEGRADED
    errors: Dict[str, str] = field(default_factory=dict)


async def _call_openai_compat(
    provider: OpenAICompatProvider, messages: List[Dict[str, str]]
) -> str:
    api_key = os.getenv(provider.api_key_env)
    model = os.getenv(provider.model_env, provider.default_model)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        **provider.extra_headers,
    }
    payload = {"model": model, "messages": messages}
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.post(
            f"{provider.base_url}/chat/completions", headers=headers, json=payload
        )
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"] or ""


def _call_gemini_sync(
    contents: List[Dict[str, Any]], system_prompt: Optional[str], model: str
) -> str:
    from google import genai

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    config = {"system_instruction": system_prompt} if system_prompt else None
    generation = client.models.generate_content(
        model=model, contents=contents, config=config
    )
    return generation.text or ""


async def generate_chat_response(
    message: str,
    history: List[Dict[str, Any]],
    system_prompt: Optional[str] = None,
) -> AIResult:
    """Route the chat request across configured providers, returning the first success."""
    turns = normalize_turns(history, message)
    errors: Dict[str, str] = {}

    if os.getenv("GEMINI_API_KEY"):
        try:
            contents = build_gemini_contents(turns)
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            text = await asyncio.to_thread(
                _call_gemini_sync, contents, system_prompt, model
            )
            if text.strip():
                return AIResult(text=text, provider="gemini", status="ONLINE", errors=errors)
            errors["gemini"] = "empty response"
        except Exception as exc:  # noqa: BLE001 - report and fall through to next provider
            errors["gemini"] = str(exc)

    messages = build_openai_messages(turns, system_prompt)
    for provider in OPENAI_COMPAT_PROVIDERS:
        if not os.getenv(provider.api_key_env):
            continue
        try:
            text = await _call_openai_compat(provider, messages)
            if text.strip():
                return AIResult(
                    text=text, provider=provider.name, status="ONLINE", errors=errors
                )
            errors[provider.name] = "empty response"
        except Exception as exc:  # noqa: BLE001 - report and try the next provider
            errors[provider.name] = str(exc)

    status = "NOT_CONFIGURED" if not errors else "DEGRADED"
    return AIResult(text="", provider="none", status=status, errors=errors)
