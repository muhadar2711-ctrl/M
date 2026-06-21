---
name: testing-mcp-backend
description: Boot and smoke-test the mcp-backend FastAPI server. Use when verifying backend startup, the chat endpoint, or import/module changes under mcp-backend/.
---

# Testing mcp-backend (FastAPI)

The backend lives in `mcp-backend/` (not repo root). Entry point is `mcp-backend/main.py`, app object `app`.

## Run locally
```bash
cd mcp-backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
PORT=8000 uvicorn main:app --host 0.0.0.0 --port 8000
```
A clean boot logs `Application startup complete.` Railway uses the same `Procfile` command. Runtime is Python 3.11 on Railway; local 3.12 also works.

## Key endpoints
- `GET /health` and `GET /` → `{"status":"online", ...}` health check.
- `GET /docs` → Swagger UI; fastest way to confirm startup succeeded and routers are mounted.
- `POST /api/v1/chat/completions` body `{"message":"XAUUSD analysis"}` → `200` with `success:true`, `session_id`, `response`, and `intermediate_steps` (ContextBuilder/MemoryManager/Validator). With no/invalid `GEMINI_API_KEY` it returns a deterministic Indonesian fallback response — this is expected, not a failure.
- Other routers: `/api/v1/mt5/*`, `/api/v1/data/twelvedata/quote`, `/api/v1/news/*`, `/api/v1/sentiment/twitter`.

All routes are under `settings.API_V1_STR` (`/api/v1`) except health/docs.

## Common failure mode
Startup `ModuleNotFoundError` usually means a referenced local module under `app/` doesn't exist or a package folder is missing `__init__.py`. The import chain to check: `main.py` → `app.chat.api.router` → `app.chat.context.builder` → its sibling chat submodules (`retrieval/rag_retriever`, `memory/manager`, `prompt/orchestrator`, `validator/response_validator`). Several chat features are intentionally stubbed (dummy returns) — don't expect real logic.

## Testing tips
- Best evidence of "server boots" is any successful HTTP response — if startup crashed, nothing would respond. Test via the browser at `/docs` (use "Try it out" → Execute for the chat endpoint).
- Capture the `Application startup complete.` line from the uvicorn shell as text evidence (it's not visible in a browser recording).
- No test suite or lint config exists in the repo.

## Repo note
The accessible repo for this project is `muhadar2711-ctrl/M` with the backend under `mcp-backend/`. A separately-referenced `muhadar2/mcp-backend` may return 403.

## Devin Secrets Needed
- `GEMINI_API_KEY` (optional) — only needed to exercise the live Gemini path; without it the chat endpoint uses a deterministic fallback that is sufficient for smoke testing.
