"""Stub prompt orchestrator.

Placeholder implementation so imports succeed. No real logic yet.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def get_system_prompt(
    live_data: Optional[Dict[str, Any]] = None,
    system_status: Optional[Dict[str, Any]] = None,
    rag_knowledge: Optional[List[Dict[str, Any]]] = None,
) -> str:
    return ""
