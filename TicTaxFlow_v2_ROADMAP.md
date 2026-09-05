# TicTaxFlow v2.0.0 — Development Roadmap (for Claude Code)

**Context:** v1.0.0 is a working full-stack MVP (FastAPI + React/TS + Chroma RAG + 3 agents).
This roadmap takes it to v2.0.0 for the SWU Startup Pitching final round.

**Decisions locked with the founder:**
- v2 scope = **both axes, shallow but complete story**: deepen the *deduction* side AND add an *income* side, enough to tell one end-to-end narrative.
- Demo format = **pre-recorded video / screenshots**. Therefore: build a believable **adapter layer with mock/seed data** for platform integrations. Do NOT build live Shopee/Lazada OAuth — that is out of scope for v2 and belongs in v3.
- Timebox = **3 days**. Phase 1 ≈ 1 day, Phase 2 ≈ 2 days. Not everything must reach 100%; see the CUT LINE at the end.

**The pitch narrative v2 must support (differentiator vs iTAX):**
> iTAX = a static calculator you fill in by hand.
> TicTaxFlow = an **AI agent** that *reads, classifies, and decides for you* — on BOTH sides of the tax equation: expenses (deductions) and income (multi-platform sales), then advises how to legally minimise tax owed.

**Integrity rule (non-negotiable):** In the recorded demo and in Q&A, be explicit that platform sync runs on **sample/seeded data through a real adapter interface**, and that live marketplace APIs are the v3 step. Do not claim a live Shopee/Lazada integration that does not exist. An honest "we built the adapter layer; live API is next" is a *stronger* engineering answer than an overclaim that collapses under one judge question.

---

## PHASE 1 — Refactor & Harden (≈1 day)

Goal: fix the holes that undercut the pitch and make the codebase safe to build on.
Do these in order. Each task lists file(s), the change, and a Definition of Done (DoD).

### 1.1 Wire the LangGraph workflow into the real request path — HIGHEST PRIORITY
**Why:** `services/workflow.py` is currently dead code. Nothing imports it (verified by grep). The live `/upload` endpoint calls `inspector → tax_expert → accountant` sequentially by hand. The headline pitch — "multi-agent LangGraph orchestration" — is therefore not actually running. This must become true.

- Files: `services/workflow.py`, `api/v1/endpoints/receipts.py`, `main.py`
- Change:
  - Compile the graph **once at app startup** (FastAPI lifespan / module-level singleton), not per request. Currently `build_workflow()` recompiles every call.
  - Refactor `/upload` and `/upload-base64` to invoke the compiled graph (`run_tax_assistant` / `app.invoke(...)`) instead of the manual chain.
  - Keep the manual chain only as a fallback if you must, but the default path goes through the graph.
- DoD: uploading a receipt produces the same result as before, but the trace clearly shows it flowed through the graph nodes (Inspector → Validator → Tax Expert → Accountant). You can point Claude Code / a judge at one file (`workflow.py`) as the single source of orchestration truth.

### 1.2 Fix authentication on ALL endpoints (IDOR / broken access control)
**Why:** `/receipts/upload`, `/upload-base64`, `/process-image`, `/dashboard/summary/{user_id}`, `/dashboard/stats/{user_id}` trust a client-supplied `user_id` with no token check. Any caller can read or write any user's tax data. Only `/agent/chat` authenticates correctly.

- Files: new `core/security.py`; `endpoints/receipts.py`, `endpoints/dashboard.py`, `endpoints/transactions.py`, `endpoints/profile.py`
- Change:
  - Move `extract_user_id_from_token` out of `agent.py` into `core/security.py` as a reusable FastAPI dependency, e.g. `def get_current_user_id(authorization: str = Header(None)) -> str`.
  - Every endpoint that acts on a user's data derives `user_id` from the token via `Depends(get_current_user_id)`. Remove `user_id` from form/body/path.
  - **Delete or lock down `/process-image`** — it opens an arbitrary client-supplied filesystem path (path-traversal / local file read). If kept for testing, guard it behind a debug flag and never expose it in prod routing.
- DoD: calling any data endpoint without a valid Bearer token returns 401. A token for user A cannot read or write user B's rows.

### 1.3 Fix cumulative deduction cap (tax-logic correctness bug)
**Why:** `accountant.calculate_deductible_amount` caps each receipt individually against the category `max_limit`, but never sums prior receipts. Two Life Insurance receipts of 80,000 each are each stored as deductible 80,000 → dashboard headline `total_deductible_amount` shows 160,000, exceeding the 100,000 cap. The category breakdown clamps `remaining` to ≥0, so the two numbers disagree. This breaks the core "Validation & Rules" feature.

- Files: `agents/accountant.py`
- Change:
  - Before computing a new receipt's deductible amount, query the user's existing verified deductible total for that `category` + `tax_year`.
  - New deductible = `min(receipt_amount, max_limit - already_used)`, floored at 0. Set an `is_capped` / `over_limit` flag when the category is already full.
  - Ensure the dashboard headline `total_deductible_amount` and the per-category `remaining` are derived from the same capped values so they always agree.
- DoD: a unit test proves that uploading receipts that together exceed a category cap yields a total deductible equal to the cap, not the raw sum.

### 1.4 Fix file-type / MIME handling
**Why:** `inspector.py` hardcodes `mime_type="image/jpeg"` in all Gemini calls. README claims PDF/PNG support; PDF and PNG are sent as JPEG and will misbehave.
- Files: `agents/inspector.py`, `endpoints/receipts.py`
- Change: detect the real MIME from the upload (content-type + magic bytes), pass the correct `mime_type`. If PDF is not actually supported end-to-end, say so explicitly in the upload validation and README rather than pretending.
- DoD: uploading a PNG works; uploading a PDF either works or is rejected with a clear message — no silent corruption.

### 1.5 Cleanup / maintainability (batch)
- `agents/inspector.py`: remove unused functions (`build_inspector_prompt`, `inspect_document`, `inspect_receipt_batch`, `extract_amount`, `extract_receipts_batch_json`) — only `extract_receipt_json` and `extract_receipt_from_bytes` are used.
- Merge `services/rag_service.py` into `tax_expert.py` retrieval, or have one shared retrieval module. Right now there are two Chroma clients + duplicate query logic.
- Collapse duplicate Supabase client creation (`database.py` vs `accountant.py`) into one shared client.
- `requirements.txt`: **pin versions**, and **remove `google-generativeai`** (unused — code imports only `google-genai`).
- Replace `print(...)` debug noise (especially the `user_id` repr dumps in `dashboard.py`) with the `logging` module at INFO/DEBUG; do not log full user IDs at INFO.
- `.gitignore`: uncomment the embeddings ignore lines (223–227) if you don't want the 17MB vector store in git — OR keep it committed intentionally so the demo runs out-of-the-box (decide and document which). Remove the unreferenced `backend/chroma_persistent_storage/` directory (config points only at `data/embeddings`).
- README: fix model name (`gemini-2.5-flash`, not "Gemini 1.5 Pro").
- Consider whether `save_receipt_from_inspector` should hardcode `status="verified"`. It auto-trusts every AI classification; the `human_input` review path only lives in the (previously dead) workflow. Decide: auto-verify, or route low-confidence to `needs_review`.

### 1.6 Minimal test + CI safety net
- Add `pytest` and 3–5 smoke tests: `/health` responds; an unauthenticated data call returns 401; the cumulative-cap function respects the limit; the JSON parser in `inspector` handles a fenced ```json block; the tax estimator (added in Phase 2) matches a hand-checked figure.
- Extend `.github/workflows/ci.yml` backend job to run `pytest` (it currently only installs deps).

**Phase 1 DoD:** no unauthenticated data access; orchestration genuinely flows through LangGraph; deduction totals are internally consistent and cap-correct; tests pass in CI.

---

## PHASE 2 — v2.0.0 Features (≈2 days)

The unifying idea: extend the SAME LangGraph so one agent system now reasons across **both** income and deductions. This is what makes the "agentic, both-sides" story real in code.

### Target agent graph (v2)
```
START → Router
  ├─ has image?      → Inspector → Validator → Tax Expert → Accountant → END      (deduction side, from v1)
  ├─ income sync?    → Revenue Analyst → Tax Estimator → Optimisation Advisor → END (income side, NEW)
  └─ free-text Q?    → Tax Q&A → END
```

### 2.A Income side — multi-platform sales aggregation (the iTAX differentiator)  [MUST]
- New module `services/income_aggregator.py`:
  - Define a `SalesProvider` protocol/interface: `fetch_sales(seller_id, period) -> list[SaleRecord]`.
  - Implement `MockShopeeProvider`, `MockLazadaProvider`, `MockTikTokShopProvider` that read realistic seeded fixtures (CSV/JSON in `backend/data/fixtures/`). Name them `Mock*` in code so nobody mistakes them for live integrations.
  - Aggregate: sum per platform, dedupe overlapping orders, normalise to one schema, produce a period total.
- New endpoint `/income/sync` (authenticated) that runs the aggregation and persists an income summary for the user.
- Storage: a lightweight `income_summary` (or reuse `transactions` with a `kind` column). Keep the schema change minimal.
- DoD: hitting `/income/sync` returns a merged sales total across 3 mock platforms for a period, deduplicated, tied to the authenticated user.

### 2.B Tax estimation  [MUST]
- New `services/tax_estimator.py`: a pure function computing estimated Thai personal income tax from taxable income using the **progressive PIT brackets**.
  - IMPORTANT: do NOT hardcode bracket figures from memory. Pull the current-year brackets from the Revenue Department source and **verify them before recording the demo**. Put the bracket table in one config constant with a comment citing the source and year, so it is easy to audit and update.
  - Function must be pure and unit-tested against at least two hand-computed incomes.
- Wire it as a graph node ("Tax Estimator") after Revenue Analyst.
- DoD: given a sample annual income, the estimator returns a tax figure that matches a manual bracket calculation in a test.

### 2.C Deduction Optimisation Advisor (the money shot)  [MUST if time, else NICE]
- New graph node "Optimisation Advisor": given (estimated tax from income) + (current deductions used per category with remaining headroom), it tells the user how much allowance is unused and what the marginal tax saving would be if they topped up (e.g. "You can still deduct X in SSF; doing so saves ≈ Y in tax"). Ground it in the RAG knowledge base + the cap logic from 1.3.
- This is precisely what iTAX's static calculator does weakly, and it is the emotional peak of the demo.
- DoD: the advisor produces at least one concrete, numerically-correct "top up X → save Y" suggestion for a seeded user.

### 2.D Dashboard v2  [MUST — this is what the camera sees]
- Files: `frontend/src/pages/DashboardPage.tsx`, `components/dashboard/*`, `api/dashboard.ts`, backend `dashboard.py`.
- Add an income-vs-deduction-vs-estimated-tax view: total income (by platform), total deductions used vs remaining (existing pie), and estimated tax owed with/without the advisor's suggestion.
- Replace any remaining mock/demo values with live API data. (Note: `mockData.ts` currently also exports TYPES used by real pages — move `Transaction` / `SummaryStat` types to `types/` and keep `mockData.ts` for seed data only, or delete it once seeding moves server-side.)
- Make it clean and legible on screen for recording — this is a scored criterion (Branding & Customer Experience, 10 pts).
- DoD: the dashboard renders entirely from real backend responses for a seeded user, and looks presentable in a screen recording.

### 2.E Polish for the recorded demo  [MUST]
- Seed one demo user with: a handful of receipts across 2–3 deduction categories (including one that hits a cap, to show the validation working), and mock sales across 3 platforms.
- Write a short **demo shot list** (below) and make sure each shot works before recording.

---

## PHASE 3A — Filing Pack ภ.ง.ด.94/90 (shipped)

Goal: turn the income/deduction estimate into a "filing pack" the user can copy into RD's own
e-Filing site, for both the mid-year (ภ.ง.ด.94) and annual (ภ.ง.ด.90) forms.

**What shipped:**
- `app/core/tax_constants.py` — every filing-window date, threshold, and penalty figure (facts
  #2-#6), each cited with a source URL + retrieval date (2026-09-05). `backend/SOURCES.md` is the
  scannable table version for a judge.
- `app/services/tax_estimator.py` — `PIT_BRACKETS` replaced with the real RD brackets
  (rd.go.th/english/6045.html), `BRACKETS_VERIFIED = True`.
- `app/services/taxable_income.py` — fixes the bug where the income-sync path fed
  net-of-marketplace-fee sales straight into the PIT calculator, skipping the Section 40(8) 60%
  flat expense deduction and all allowances entirely. Now computes taxable income from GROSS
  income, and offers a flat-vs-actual expense-method comparison with a recordkeeping warning when
  actual wins.
- `app/services/income_aggregator.py` — `aggregate_income` now accepts an optional inclusive
  `date_from`/`date_to` range, so a mid-year (Jan-Jun) sync is a real half-year query, not a
  same-year full-12-months query.
- `app/services/filing_pack.py` / `app/services/filing_box_map.py` — `build_filing_pack(user_id,
  form_type, tax_year)` assembles income, expense-method comparison, deduction headroom (reuses
  `advisor.get_category_headroom`, cap logic not reimplemented), tax due, a box-mapping table to
  real form item numbers, a document checklist, filing deadline + days-remaining (computed, not
  hardcoded), a disclaimer, and a verification-status flag.
- `GET /filing/preview` and `GET /filing/forms` (`app/api/v1/endpoints/filing.py`), both
  token-authenticated per `core/security.py`'s pattern — `user_id` is never accepted from the
  client. Only ภ.ง.ด.94 and ภ.ง.ด.90 are supported; ภ.ง.ด.91 (salary-only) is out of scope and
  422s.

**Honest gap — box_mapping sourcing:** `data/documents/Ins94_070666.pdf` (now indexed into the RAG
corpus) is RD's official PND94 instructions PDF, but for **tax year 2566 (2023)** — no 2568/2569
vintage could be found via web search. Worse, its embedded Thai font has no ToUnicode CMap, so
pdftotext/pypdf extraction of Thai item labels is unreliable for this PDF. `Ins90_241268.pdf`
extracts cleanly, so PND90's "Section 40(8) income → item 7" row in `filing_box_map.py` is a real
PDF-page citation (page 3, confirmed via `pdftotext -layout`). Every other PND90 row and every
PND94 row is instead cross-referenced against 2 independent current Thai professional-accounting
sources (itax.in.th, krungsri.com) plus the stable structural layout shared across the
2560/2562/2565/2566/2567/2568 PIT94/PIT90 form PDFs — `filing_box_map.py`'s module docstring and
each row's `note` field say exactly which citation type applies. Do not present these as verified
page citations in the demo; say "cross-referenced against current filing guides" for the PND94
rows.

**Also not modelled yet:** the fixed statutory personal/spouse/child PIT allowance amounts have no
dedicated table — `filing_pack._total_allowances()` approximates "total allowances" as the sum of
the user's used receipt-backed deduction categories (health insurance, donations, etc.), halved
for PND94 per fact #5. This is a reasonable stand-in given the current schema, not a verified
per-allowance figure — see that function's docstring.

**Not built:** persistence of a computed filing pack (the spec allowed skipping this since the
pack is cheap to recompute; no `migrations/00X_filing_pack.sql` was added). ภ.ง.ด.91 is
out-of-scope by design.

---

## Demo shot list (for the recorded video)
1. Upload a receipt → watch the agent extract Date / Amount / Tax ID / Merchant.
2. Agent auto-classifies the category and flags it deductible.
3. Upload a second receipt in the same category that pushes it over the cap → the validation warning fires (proves 1.3).
4. Trigger `/income/sync` → sales from 3 platforms merge into one income total (state clearly: seeded data via adapter layer).
5. Tax Estimator shows estimated tax owed.
6. Optimisation Advisor: "you can still deduct X → save Y".
7. Dashboard v2 ties it all together in one view.
8. (Q&A ready) Open `workflow.py` and show the real multi-agent graph orchestrating all of the above.

---

## CUT LINE (if 3 days run short, ship in this order)
Ship top-to-bottom; stop wherever time ends and the demo still tells a whole story.
1. Phase 1.1 (LangGraph wired) + 1.3 (cap fix) + 1.2 (auth) — credibility floor.
2. 2.A income sync (mock) + 2.D dashboard v2 — the visible "both sides" story.
3. 2.B tax estimator — makes the income side mean something.
4. 2.C optimisation advisor — the peak, but the demo survives without it if needed.
5. Everything else in 1.5 / 1.6 (cleanup, tests) — do as much as time allows; tests protect 1.3 and 2.B specifically, so prioritise those two tests.

## Known limits to state honestly in the pitch (do not paper over)
- Platform sync is seeded sample data through a real adapter interface; live marketplace APIs are v3.
- Customer insight is still thin: per the team's own notes, no real online sellers have been interviewed yet. Building the feature does not create the evidence — keep Problem/Insight claims grounded in law and public data, not in user research that hasn't happened. (This directly affects the 15-point "Problem & Customer Insight" criterion; a couple of real seller conversations before the final would be worth more than any extra code.)
- Tax bracket figures and category limits must be verified against the current Revenue Department source before recording — do not trust hardcoded numbers from training data.
