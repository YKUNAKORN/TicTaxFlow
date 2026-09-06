# DEMO.md — Recorded pitch shot list

Reproduces the 8-shot list from `TicTaxFlow_v2_ROADMAP.md` from a clean
state. Read the whole file once before recording — the manual setup section
has items that silently break the demo if skipped (RAG index, `tax_rules`
seed, Gemini quota).

## One-time / per-machine manual setup

1. **Backend `.env`** (`backend/.env`, copied from `backend/.env.example`)
   has `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY` (Supabase **service
   role** key — the seed script uses the Supabase admin API).
2. **Supabase project is set up** per [`docs/supabase-setup.md`](docs/supabase-setup.md):
   - `supabase/schema.sql` run once (creates `users`, `tax_rules`,
     `transactions`, `income_summary`, all with RLS);
   - `supabase/seed_tax_rules.sql` run once — **`tax_rules` starts empty**,
     and until it has rows every classified receipt is stored
     `needs_review` with `deductible_amount` 0 and the dashboard/advisor
     show no categories;
   - **Confirm email** turned off (Authentication → Providers → Email).
3. **Sample sales fixtures are dated for the current tax year.**
   `backend/data/fixtures/{shopee,lazada,tiktok}_sales.json` are dated for
   `datetime.now().year`. If the calendar year has rolled over since they
   were last generated, re-run from `backend/`:
   ```bash
   python scripts/generate_sample_fixtures.py
   ```
   (The income-sync dashboard falls back to the most recent year with data,
   and `GET /filing/forms` resolves the same way, so a stale year degrades
   rather than zeroes — but regenerating keeps ภ.ง.ด.94's Jan–Jun scoping
   meaningful.)
4. **Gemini free-tier quota.** `gemini-2.5-flash` free tier is capped at
   **20 requests/day/project**. Each receipt upload costs 2 calls (Inspector
   vision extraction + Tax Expert classification), so shots 1–3 cost ~4
   calls — but that budget disappears fast if you rehearse, and
   `GET /health/deep` spends one call per hit. **Do a full dry run once,
   then record the real take without re-rehearsing the upload shots**, or
   switch the project to a paid tier before recording. A `429
   RESOURCE_EXHAUSTED` mid-take is this quota, not a bug.
5. **PIT figures are verified; the estimate is still labelled an estimate.**
   `app/services/tax_estimator.py` ships the real 8-bracket Revenue
   Department table (`rd.go.th/english/6045.html`, retrieved 2026-09-05)
   with `BRACKETS_VERIFIED = True`, and `app/core/tax_constants.py` figures
   are cited in `backend/SOURCES.md`. The number shown in shots 5–7 is still
   an **estimate** because the fixed personal/spouse/child allowances are
   not modelled yet (see "Known limits" below) — say "estimated tax, before
   personal allowances" if asked, not "unverified".
6. Backend running (`uvicorn main:app --reload` from `backend/`), frontend
   running (`npm run dev` from `frontend/`).

## Seed the demo user

From `backend/`, with the venv active and `.env` pointed at the project:

```bash
python scripts/seed_demo.py
```

Safe to re-run — it deletes and recreates only its own demo user and rows.
It also auto-populates the Chroma RAG store from `backend/data/documents/`
if empty (that store is gitignored, so a fresh clone starts with **zero**
vectors — without this step, Tax Expert classification silently returns
category "None" for every receipt and shots 2–3 stall). First run downloads
the embedding model (~500 MB) and needs internet; later runs are offline.

Output gives you the login:
- email: `demo@tictaxflow.app`
- password: `DemoPitch2026!`

State after seeding (deduction caps read live from `tax_rules`, not
hardcoded):

| Category | Used | Cap | Headroom |
|---|---|---|---|
| Health Insurance | 0 | 25,000 | full — untouched, for a fresh live upload |
| Life Insurance | 90,000 | 100,000 | 10,000 — one receipt over this fires the cap warning |
| SSF | 120,000 | 200,000 | 80,000 — gives the Advisor something to suggest |

Mock sales fixtures (`backend/data/fixtures/{shopee,lazada,tiktok}_sales.json`)
need no per-user wiring — `MockShopeeProvider` / `MockLazadaProvider` /
`MockTikTokShopProvider` return the same seeded period for any authenticated
caller (see `income_aggregator.py`). Combined figures for the current tax
year:

- **~2,500,000 THB gross / ~2,327,000 THB net** across **45 orders**, 3
  platforms (Shopee ~1.0M, Lazada ~0.85M, TikTok Shop ~0.65M).
- One same-platform duplicate order (`SHP-<year>-1004`, re-sent) and one
  cross-platform coincidental order id (`<year>-000777` on both Lazada and
  TikTok Shop) — both deliberate, to prove the dedup logic on camera (see
  `tests/test_income_aggregator.py`).
- After the Section 40(8) flat **60%** expense deduction that is
  **~1,000,000 THB taxable → ~115,000 THB estimated PIT**, a **20% marginal
  rate** — enough headroom for the Advisor to rank real, high-value
  suggestions.

Sample receipts to upload live during recording (synthetic, clearly
labelled "SAMPLE RECEIPT" on the image, not real invoices):
`backend/data/fixtures/sample_receipts/health_insurance_receipt.png` and
`life_insurance_topup_receipt.png`. Regenerate with
`python scripts/generate_sample_receipts.py` (`pip install Pillow` first —
not a runtime dependency).

## Shot list

1. **Upload a receipt.** Log in as the demo user, upload
   `health_insurance_receipt.png`. Watch the agent extract Date
   (2026-08-20) / Amount (8,500.00) / Tax ID / Merchant
   ("Bangkok Health Insurance Co., Ltd.").
2. **Auto-classify.** Same response: Tax Expert flags it `Health
   Insurance`, `is_deductible: true`, within the 25,000 THB cap, and the
   transaction is auto-verified (AI-classified receipts with a concrete
   category are stored `verified` — see "Known limits").
3. **Cap warning.** Upload `life_insurance_topup_receipt.png` (15,000 THB,
   classified `Life Insurance`). The category already has 90,000 of 100,000
   used, so this receipt is capped at the remaining 10,000 THB and the
   response message reads "capped at 100,000.00 THB limit" — proves the
   cumulative-cap logic.
4. **`/income/sync`.** Trigger sync. Response merges Shopee + Lazada +
   TikTok Shop into one deduplicated total (~2,500,000 THB gross / 45
   orders). State on camera: *seeded sample data via a real adapter
   interface, not a live marketplace integration.*
5. **Tax Estimator.** Same response's `tax_estimate`: PIT on the GROSS
   income after the 60% flat expense deduction — **~115,000 THB** on
   ~1,000,000 THB taxable, progressive 8-bracket table, `brackets_verified:
   true`. Say "estimated, before personal allowances" if asked about
   precision.
6. **Optimisation Advisor.** Same response's `deduction_suggestions`,
   ranked by estimated saving at the 20% marginal rate. Top entry with the
   seeded state is **RMF — ~500,000 THB of unused headroom, ≈100,000 THB
   saved**; next are Thai ESG (~60,000) and Pension Insurance (~40,000).
   Read the top "top up X → save ~Y" line out loud. (The advisor suggests
   the full remaining headroom; a real user tops up what they can afford.)
7. **Dashboard v2.** Open the dashboard: income by platform, deductions
   used vs. remaining, and estimated tax in one view; Life Insurance shown
   at its cap. Note the income figure on the overview chart is **net**
   (~2,327,000 THB, after marketplace fees) while the tax estimate is on
   gross-minus-60% — they are different bases on purpose.
8. **Q&A: show the graph.** Open `backend/app/services/workflow.py` and
   point at `build_workflow()` — the single compiled LangGraph that all of
   shots 1–7 ran through (Inspector → Validator → Tax Expert → Accountant
   for receipts; Income → Estimate Tax → Advisor for sync).

## Known limits to state honestly if asked

- **Platform sync is seeded sample data** through a real adapter interface
  (`Mock*Provider`); live marketplace (Shopee/Lazada/TikTok Shop) APIs are
  a v3 item (roadmap integrity rule).
- **The tax estimate applies the 60% flat expense deduction but not the
  fixed personal/spouse/child allowances** — those are not modelled in the
  schema yet, so the estimate slightly *overstates* tax. The filing pack
  approximates "allowances" as the sum of the user's used receipt-backed
  deduction categories (halved for ภ.ง.ด.94); see
  `filing_pack._total_allowances()`.
- **Donation categories are not capped at 10% of net income.** For
  `Donation (General)` / `Donation (Education/Sports)`,
  `accountant.calculate_deductible_amount` uses the amount-based path (or 2×
  for e-Donation education/sports) with no statutory 10%-of-income ceiling —
  a documented gap. The demo does not upload a donation receipt.
- **AI-classified receipts auto-verify.** A receipt the Tax Expert maps to
  a concrete category with `is_deductible: true` is stored `verified` and
  counts toward the deduction total immediately, with no human review step.
  Routing low-confidence classifications to `needs_review` is a v-next
  refinement.
- Customer insight is still thin — keep Problem/Insight claims grounded in
  law and public data, not in user research that has not happened
  (roadmap's own note; affects the 15-pt "Problem & Customer Insight"
  criterion).
