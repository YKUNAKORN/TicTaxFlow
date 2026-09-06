# Supabase setup

Every deployment needs its **own** Supabase project. Nothing here is shared;
the repo ships no Supabase credentials.

## 1. Create the project

1. https://supabase.com/dashboard → **New project**. Pick a region near your
   users. Save the database password somewhere safe.
2. Wait for provisioning to finish.

## 2. Run the schema

1. Open **SQL Editor** in the Supabase dashboard.
2. Paste the full contents of [`../supabase/schema.sql`](../supabase/schema.sql)
   and run it.
3. It creates `users`, `tax_rules`, `transactions`, and `income_summary`, with
   Row Level Security enabled on all four.

The `supabase/` CLI layout is also compatible with `supabase db push` if you
prefer that.

## 3. Grab the credentials

**Settings → API**:

| Value | Goes into `.env` as | Notes |
|---|---|---|
| Project URL | `SUPABASE_URL` | `https://<ref>.supabase.co` |
| `service_role` secret key | `SUPABASE_KEY` | **Not** the `anon` key. See below. |

### Why service_role and not anon

The backend:

- calls the admin API — `auth.admin.create_user`, `update_user_by_id`,
  `list_users`, `delete_user` (register, change-password, profile update,
  `scripts/seed_demo.py`);
- writes `transactions` / `users` / `income_summary` rows on the user's behalf
  from a client that has no end-user session attached.

The `anon` key can do neither — the admin calls fail outright, and the row
writes are blocked by RLS. `service_role` bypasses RLS, so keep it secret and
server-side only. It is never exposed to the frontend (the frontend only ever
talks to the backend API, never to Supabase directly).

## 4. Disable email confirmation (for the demo)

**Authentication → Providers → Email** → turn **Confirm email** off.

`POST /api/v1/auth/login` calls `sign_in_with_password`, which rejects users
whose email is not confirmed. With confirmation on, every newly registered
account can't log in until it clicks an email link. For a demo/eval, turn it
off. (Alternative: leave it on and confirm each user manually in
**Authentication → Users**.)

`scripts/seed_demo.py` already sets `email_confirm: True` on the demo user it
creates, so the seeded `demo@tictaxflow.app` login works regardless of this
setting.

## 5. Seed `tax_rules`

`schema.sql` creates `tax_rules` **empty**. Until it has rows, the tax-expert
classifier maps every receipt to "no matching rule" — each classified receipt
is stored `needs_review` with `deductible_amount` 0, and the dashboard
category breakdown and the deduction advisor have nothing to show.

Run [`../supabase/seed_tax_rules.sql`](../supabase/seed_tax_rules.sql) in the
SQL editor. It inserts the 12 demo deduction categories (Health/Life/Pension
Insurance, SSF, RMF, Thai ESG, Home Loan Interest, Social Security, Easy
E-Receipt, and the two income-based donation categories) for `tax_year = 2026`.

The `max_limit` values mirror the "Base Knowledge" block in
`backend/app/agents/tax_expert.py` so the classifier and the DB agree. They
are **demo scaffolding** — re-verify each against the current Revenue
Department source (https://rd.go.th) before any non-demo use, and keep this
table as the single source of truth (do not hardcode the numbers elsewhere).
The seed is idempotent (it replaces that year's rows); bump the year in it
when the calendar year rolls over.

## 6. (Optional) seed the demo user

From `backend/`, venv active, `.env` pointed at this project:

```bash
python scripts/seed_demo.py
```

Creates `demo@tictaxflow.app` / `DemoPitch2026!` with two verified
transactions. Safe to re-run. See [`../DEMO.md`](../DEMO.md).

## Table reference

Columns are derived from code usage. `TODO(owner)` items in `schema.sql` are
columns the code never reads back — confirm or drop them.

- **users** — `id` (= `auth.users.id`), `username`, `email`, `created_at`.
  (`password` column is vestigial and no longer written — Supabase Auth is
  the credential store.)
- **tax_rules** — `id`, `category_name`, `max_limit`, `tax_year` (CE),
  `is_active`, `created_at`.
- **transactions** — `id`, `user_id`, `rule_id` (nullable FK → `tax_rules`),
  `receipt_image_url`, `merchant_name`, `merchant_tax_id`, `transaction_date`,
  `total_amount`, `deductible_amount`, `status`
  (`needs_review` | `verified` | `not_deductible` | `rejected`), `ai_reasoning`,
  `create_at` (**sic** — column name is missing the 'd'; code depends on it).
- **income_summary** — see `schema.sql` / `backend/migrations/001_income_summary.sql`.
