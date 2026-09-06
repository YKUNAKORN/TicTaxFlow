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
classifier maps every receipt to "no matching rule" and the dashboard shows no
categories.

Insert one row per deduction category the classifier can output (at minimum:
`Health Insurance`, `Life Insurance`, `SSF`; plus `RMF`, `Provident Fund`,
`Thai ESG`, and the donation categories if your knowledge base uses them).
Take every `max_limit` figure from [`../backend/SOURCES.md`](../backend/SOURCES.md)
and `backend/app/core/tax_constants.py` — do not invent limits. Use the current
calendar year (CE, e.g. `2026`) for `tax_year`.

```sql
insert into public.tax_rules (category_name, max_limit, tax_year, is_active) values
  ('Health Insurance', /* SOURCES.md */, 2026, true),
  ('Life Insurance',   /* SOURCES.md */, 2026, true),
  ('SSF',              /* SOURCES.md */, 2026, true);
```

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

- **users** — `id` (= `auth.users.id`), `username`, `email`, `password`
  (write-only mirror, real credentials live in Supabase Auth), `created_at`.
- **tax_rules** — `id`, `category_name`, `max_limit`, `tax_year` (CE),
  `is_active`, `created_at`.
- **transactions** — `id`, `user_id`, `rule_id` (nullable FK → `tax_rules`),
  `receipt_image_url`, `merchant_name`, `merchant_tax_id`, `transaction_date`,
  `total_amount`, `deductible_amount`, `status`
  (`needs_review` | `verified` | `not_deductible` | `rejected`), `ai_reasoning`,
  `create_at` (**sic** — column name is missing the 'd'; code depends on it).
- **income_summary** — see `schema.sql` / `backend/migrations/001_income_summary.sql`.
