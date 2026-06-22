"""Prompt orchestrator — builds system prompt from context.

Currently returns a minimal default prompt. RAG-enhanced prompt building
will be added when knowledge retrieval is connected to a vector store.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

_DEFAULT_SYSTEM_PROMPT = """You are SMC Trading Assistant, an AI helper for Smart Money Concepts trading.
You help with market analysis, trade execution, sentiment analysis, and news updates.
Always use the provided market data and context to give accurate, timely responses.
Be concise but thorough. Do not fabricate data — if you don't know, say so.
Risk disclaimer: Trading involves risk. Always do your own analysis."""


def get_system_prompt(
    live_data: Optional[Dict[str, Any]] = None,
    system_status: Optional[Dict[str, Any]] = None,
    rag_knowledge: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Build system prompt from live data, status, and optional RAG knowledge.

    Parameters
    ----------
    live_data:
        Current market data snapshot (quote, status, etc.).
    system_status:
        Environment variable readiness flags.
    rag_knowledge:
        Retrieved knowledge chunks from RAG (empty list if not connected).

    Returns
    -------
    str
        System prompt string. Empty string if no context is ready.
    """
    # If no live data or status is available, return default
    if not live_data and not system_status:
        return _DEFAULT_SYSTEM_PROMPT

    parts = [_DEFAULT_SYSTEM_PROMPT]

    if live_data and live_data.get("status") == "ONLINE":
        quote = live_data.get("quote", {})
        parts.append(
            f"\n[LIVE MARKET DATA]\n"
            f"Symbol: {quote.get('symbol', 'N/A')}\n"
            f"Price: {quote.get('close', 'N/A')}\n"
            f"Change: {quote.get('change', 'N/A')} ({quote.get('percent_change', 'N/A')})\n"
            f"Market open: {quote.get('is_market_open', 'N/A')}"
        )

    if rag_knowledge:
        rag_section = "\n[RETRIEVED KNOWLEDGE]\n"
        for i, chunk in enumerate(rag_knowledge[:3], 1):
            snippet = str(chunk.get("snippet", chunk.get("content", "")))[:300]
            rag_section += f"{i}. {snippet}\n"
        parts.append(rag_section)

    return "\n".join(parts)