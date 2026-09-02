# CLAUDE.md — TicTaxFlow

Persistent context for Claude Code. Keep this file small and stable — it loads into every session. Time-boxed task plans live in separate roadmap/prompt files, not here.

## What this project is
TicTaxFlow is an AI-agent tax assistant for Thailand. v1 handles the **deduction** side: upload a receipt, extract fields, classify the deduction category, validate against limits, show a dashboard. v2 adds an **income** side: aggregate sales across marketplaces, estimate tax owed, and advise how to use remaining deduction allowance. Differentiator vs iTAX: an agent that *reads and decides* on both sides, not a manual calculator.

## Stack
- Backend: FastAPI, Python 3.11. LLM/Vision via `google-genai` (`from google import genai`), model `gemini-2.5-flash` (see `core/config.py`). Multi-agent orchestration via **LangGraph**. RAG via **Chroma** (PersistentClient at `backend/data/embeddings`). Data + auth + file storage via **Supabase**.
- Frontend: React + TypeScript + Vite + Tailwind. API layer in `frontend/src/api/`.

## Layout
- `backend/app/agents/` — inspector (Gemini Vision OCR), tax_expert (RAG classifier + Q&A), accountant (DB writes + deduction math).
- `backend/app/services/` — `workflow.py` (LangGraph graph), retrieval/RAG.
- `backend/app/api/v1/endpoints/` — auth, receipts, dashboard, transactions, tax_rules, profile, agent.
- `backend/app/core/` — config, security. `backend/app/database/` — Supabase clients.
- `frontend/src/` — `pages/`, `components/`, `api/`, `types/`.

## Commands
- Backend (from `backend/`): `uvicorn main:app --reload`. Tests: `pytest`.
- Frontend (from `frontend/`): `npm run dev`, `npm run build`, `npm run lint`.
- Env vars: `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY` (see `.env.example`). Never commit `.env`.

## Architecture rules (do not violate)
- **All agent orchestration goes through `services/workflow.py` (LangGraph).** Endpoints call the compiled graph; they do not chain agents by hand. Compile the graph once at startup, never per request.
- **Auth: every data endpoint derives `user_id` from the Bearer token** via the shared dependency in `core/security.py`. Never accept `user_id` from the client (form, body, or path). The correct pattern lives in `endpoints/agent.py`.
- **Deduction caps are cumulative** per user + category + tax_year. Never cap a single receipt in isolation.

## Tax-domain rules
- Never hardcode tax bracket figures or deduction category limits from memory. Read limits from the `tax_rules` table; source bracket rates from the Revenue Department and keep them in one config constant with a comment citing source + year, so they are auditable. Verify all figures before any demo.
- Thai tax years are Buddhist Era (BE = CE + 543). Confirm whether the `tax_rules.tax_year` column stores BE or CE before writing year-filtered queries.

## Conventions
- Use the `logging` module, not `print`. Do not log full user IDs at INFO.
- Pin dependency versions in `requirements.txt`.
- Detect file MIME type; never hardcode `image/jpeg`.

## Integrity rule for the pitch/demo
Marketplace sync runs on **seeded sample data through a real adapter interface** (`Mock*Provider` classes). Do not present it, in code comments or demo copy, as a live Shopee/Lazada integration. Live marketplace APIs are a v3 item.

## Known gotchas
- `google-generativeai` in requirements is unused; the code uses `google-genai`. Don't reintroduce it.
- There were historically two Chroma stores; `data/embeddings` is the real one. `chroma_persistent_storage/` is dead.
- Chroma uses the default embedding function (MiniLM), which is weak on Thai. If retrieval quality is poor, switch to a multilingual embedding function rather than assuming the RAG content is wrong.
