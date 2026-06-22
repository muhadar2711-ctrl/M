from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.chat.context.builder import build_context
from app.chat.memory.manager import MemoryManager
from app.chat.prompt.orchestrator import get_system_prompt
from app.chat.validator.response_validator import validate_response
from app.services.ai_provider import generate_chat_response


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = Field(default_factory=list)
    images_base64: List[str] = Field(default_factory=list)
    mode: Optional[str] = "standard"
    session_id: Optional[str] = None


def _summarize_context(context: Dict[str, Any]) -> str:
    market = context.get("live_market_data", {})
    knowledge = context.get("retrieved_knowledge", [])
    status = context.get("system_status", {})
    lines = [
        f"Symbol: {context.get('symbol') or 'N/A'}",
        f"Market status: {market.get('status', 'UNKNOWN')}",
        f"Knowledge matches: {len(knowledge)}",
        f"Config status: {status}",
    ]
    return "\n".join(lines)


def _fallback_response(req: ChatRequest, context: Dict[str, Any]) -> str:
    """Generate a truthful fallback when no AI provider returns content."""
    knowledge = context.get("retrieved_knowledge", [])
    market = context.get("live_market_data", {})
    parts = [
        "Chat backend berjalan tanpa model generatif aktif.",
        f"Topik: {req.message.strip()}",
        f"Status market: {market.get('status', 'UNAVAILABLE')}",
    ]
    if market.get("quote"):
        quote = market["quote"]
        parts.append(
            f"Quote {quote.get('symbol')}: price={quote.get('price')} timestamp={quote.get('timestamp')}"
        )
    if knowledge:
        first = knowledge[0]
        parts.append(
            f"RAG teratas: {first.get('path')} | {str(first.get('snippet', ''))[:220]}"
        )
    parts.append("Gunakan ini sebagai dasar analisis manual dan risk check.")
    return "\n".join(parts)


def _build_intermediate_steps(
    context: Dict[str, Any], memory: MemoryManager
) -> List[Dict[str, str]]:
    """Build honest intermediate steps reflecting actual backend activity."""
    steps = [
        {"agent": "ContextBuilder", "content": "Context assembled from live status and RAG"},
    ]
    # Report memory honestly
    memory_note = (
        "Conversation stored in-memory (SQLite not connected)"
        if not getattr(memory, "_persist", False)
        else "Conversation persisted to SQLite"
    )
    steps.append({"agent": "MemoryManager", "content": memory_note})
    steps.append({"agent": "Validator", "content": "Response validated for unsafe claims"})
    return steps


@router.post("/completions")
async def chat_completions(req: ChatRequest):
    memory = MemoryManager()
    session_id = req.session_id or str(uuid.uuid4())

    memory.add_to_memory(session_id, "user", req.message)

    context = await build_context(req.message, req.history)
    system_prompt = get_system_prompt(
        live_data=context["live_market_data"],
        system_status=context["system_status"],
        rag_knowledge=context["retrieved_knowledge"],
    )
    context["system_prompt_compiled"] = system_prompt

    history = [{"role": msg.role, "content": msg.content} for msg in req.history]
    ai_result = await generate_chat_response(
        message=req.message,
        history=history,
        system_prompt=system_prompt,
        images_base64=req.images_base64 if req.images_base64 else None,
    )
    ai_response = ai_result.text
    provider_status = ai_result.status

    if not ai_response or not ai_response.strip():
        ai_response = _fallback_response(req, context)

    safe_answer = validate_response(ai_response, context)
    memory.add_to_memory(session_id, "assistant", safe_answer)
    memory.summarize_memory(session_id)

    return {
        "success": True,
        "session_id": session_id,
        "response": safe_answer,
        "provider_status": provider_status,
        "context_summary": _summarize_context(context),
        "intermediate_steps": _build_intermediate_steps(context, memory),
    }