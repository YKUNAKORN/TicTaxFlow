# DEMO.md — Recorded pitch shot list

Reproduces the 8-shot list from `TicTaxFlow_v2_ROADMAP.md` from a clean
state. Read the whole file once before recording — the manual setup
section has two items (RAG index, Gemini quota) that silently break the
demo if skipped.

## One-time / per-machine manual setup

1. **Backend `.env`** has `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`
   (service role — the seed script uses the Supabase admin API).
2. **`income_summary` table exists in Supabase.** Run
   `backend/migrations/001_income_summary.sql` once in the Supabase SQL
   editor if it hasn't been applied to this project yet (checked
   2026-09-05: it already has been on the current dev project).
3. **Gemini free-tier quota.** `gemini-2.5-flash` free tier is capped at
   **20 requests/day/project**. Each receipt upload costs 2 calls
   (Inspector vision extraction + Tax Expert classification), so the two
   uploads in shots 1–3 cost ~4 calls total — but that budget disappears
   fast if you rehearse. **Do a full dry run once, then record the actual
   take without re-rehearsing the upload shots**, or switch the project to
   a paid tier before recording. If you see `429 RESOURCE_EXHAUSTED`
   mid-take, that's this quota, not a bug — wait for the daily reset or
   switch API keys.
4. **PIT bracket figures are UNVERIFIED.** `backend/app/services/tax_estimator.py`
   ships `BRACKETS_VERIFIED = False` with placeholder figures (a
   deliberately simplified 4-bracket table) and a `TODO` to confirm them
   against the Revenue Department before any real number is quoted. The
   `tax_estimate.tax_due` shown in shots 5–6 is directionally correct
   arithmetic but **do not state it as an official/verified figure in the
   pitch or Q&A** until that TODO is resolved — say "estimated, pending
   final bracket verification" if asked.
5. Backend running (`uvicorn main:app --reload` from `backend/`), frontend
   running (`npm run dev` from `frontend/`).

## Seed the demo user

From `backend/`, with the venv active:

```bash
python scripts/seed_demo.py
```

Safe to re-run — it deletes and recreates only its own demo user and rows.
It also auto-populates the Chroma RAG store from `backend/data/documents/`
if empty (that store is gitignored, so a fresh clone starts with **zero**
vectors — without this step, Tax Expert classification silently returns
category "None" for every receipt and shots 2–3 stall).

Output gives you the login:
- email: `demo@tictaxflow.app`
- password: `DemoPitch2026!`

State after seeding (all amounts read from the live `tax_rules` table, not
hardcoded):
| Category | Used | Cap | Headroom |
|---|---|---|---|
| Health Insurance | 0 | 25,000 | full — untouched for a fresh live upload |
| Life Insurance | 90,000 | 100,000 | 10,000 — one receipt over this fires the cap warning |
| SSF | 120,000 | 200,000 | 80,000 — gives the Advisor something to suggest |

Mock sales fixtures (`backend/data/fixtures/{shopee,lazada,tiktok}_sales.json`)
need no per-user wiring — `MockShopeeProvider` / `MockLazadaProvider` /
`MockTikTokShopProvider` return the same seeded period for any
authenticated caller (see `income_aggregator.py`). Combined 2025 total:
~203,595 THB gross / ~189,389 THB net across 45 orders (one intentional
same-platform duplicate order and one intentional cross-platform
coincidental order-id, both there to prove the dedup logic on camera —
see `tests/test_income_aggregator.py`), which lands in the 5% PIT
bracket — enough for the Advisor to produce a nonzero suggestion.

Sample receipts to upload live during recording (synthetic, clearly
labelled "SAMPLE RECEIPT" on the image, not real invoices):
`backend/data/fixtures/sample_receipts/health_insurance_receipt.png` and
`life_insurance_topup_receipt.png`. Regenerate them with
`python scripts/generate_sample_receipts.py` (`pip install Pillow` first —
not a runtime dependency of the app, only needed to regenerate these).

## Shot list

1. **Upload a receipt.** Log in as the demo user, upload
   `health_insurance_receipt.png`. Watch the agent extract Date
   (2026-08-20) / Amount (8,500.00) / Tax ID / Merchant
   ("Bangkok Health Insurance Co., Ltd.").
2. **Auto-classify.** Same response: Tax Expert flags it `Health
   Insurance`, `is_deductible: true`, fully within the 25,000 THB cap.
3. **Cap warning.** Upload `life_insurance_topup_receipt.png` (15,000 THB,
   classified `Life Insurance`). Category already has 90,000 of 100,000
   used, so this receipt is capped at the remaining 10,000 THB and the
   response message reads "capped at 100,000.00 THB limit" — proves the
   cumulative-cap fix.
4. **`/income/sync`.** Trigger sync. Response merges Shopee + Lazada +
   TikTok Shop into one deduplicated total (state on camera: *seeded
   sample data via a real adapter interface, not a live marketplace
   integration*).
5. **Tax Estimator.** Same response's `tax_estimate` shows the estimated
   PIT due on that net income (progressive brackets, ~4,469 THB on
   ~189,389 THB net at time of writing — recompute after any fixture or
   bracket change). Caveat per setup item 4 above if asked about accuracy.
6. **Optimisation Advisor.** Same response's `deduction_suggestions`
   — pick the top entry (ranked by estimated saving; typically an
   underused category like Provident Fund / RMF / Thai ESG) and read the
   "top up X → save ~Y" line out loud.
7. **Dashboard v2.** Open the dashboard: income vs. deductions vs.
   estimated tax in one view, Life Insurance shown at its cap, category
   breakdown matching the API responses above.
8. **Q&A: show the graph.** Open `backend/app/services/workflow.py` and
   point at `build_workflow()` — the single compiled LangGraph that all of
   shots 1–7 actually ran through (Inspector → Validator → Tax Expert →
   Accountant for receipts; Income → Estimate Tax → Advisor for sync).

## Known limits to state honestly if asked

- Platform sync is seeded sample data through a real adapter interface;
  live marketplace APIs are v3 (roadmap integrity rule).
- PIT bracket figures are unverified placeholders (setup item 4).
- `tax_estimate` treats aggregated net sales as taxable income directly —
  it does not net out the deductions from the same response. Framing it
  as "estimated tax on this income, before the advisor's suggested
  top-ups" is accurate; do not claim it already reflects the deductions.
