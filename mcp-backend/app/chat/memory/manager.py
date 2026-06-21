"""Stub memory manager.

Placeholder implementation so imports succeed. No real logic yet.
"""
from __future__ import annotations

from typing import Any, Dict, List


class MemoryManager:
    def add_to_memory(self, session_id: str, role: str, content: str) -> None:
        return None

    def get_memory(self, session_id: str) -> List[Dict[str, Any]]:
        return []

    def summarize_memory(self, session_id: str) -> None:
        return None
