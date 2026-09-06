-- TicTaxFlow — Supabase schema
-- =============================================================================
-- Run this ONCE in the Supabase SQL editor (or `supabase db push`) against a
-- fresh project, before starting the backend. It creates every table the API
-- reads or writes and enables Row Level Security on each.
--
-- Columns here are derived from how the code actually uses each table
-- (backend/app/api/v1/endpoints/*, backend/app/agents/accountant.py,
-- backend/scripts/seed_demo.py). Anything the code never reads back is marked
-- TODO(owner) — confirm or drop before treating this as authoritative.
--
-- AUTH NOTE: the backend authenticates with the Supabase SERVICE ROLE key
-- (it calls auth.admin.* and writes rows on the user's behalf). service_role
-- BYPASSES RLS, so the policies below do not gate the backend — they exist so
-- the anon key cannot read/write these tables, and as defense-in-depth if a
-- client ever talks to Supabase directly. Keep RLS enabled.
--
-- EMAIL CONFIRMATION: for the demo, disable "Confirm email" in
-- Authentication > Providers > Email (or confirm each user manually).
-- Login via auth.sign_in_with_password fails for unconfirmed users.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- users  (mirror of auth.users; app writes on register, reads only `username`)
-- -----------------------------------------------------------------------------
create table if not exists public.users (
    id         uuid primary key references auth.users (id) on delete cascade,
    username   text,
    email      text,
    -- Vestigial. Supabase Auth is the real (and only) credential store; the
    -- app no longer writes or reads this column (register + seed_demo both
    -- omit it). Kept nullable so old rows don't break.
    -- TODO(owner): drop this column once no environment still has data in it.
    password   text,
    -- TODO(owner): not read by any code path; kept for convenience. Drop if unused.
    created_at timestamptz not null default now()
);

alter table public.users enable row level security;

create policy "Users can read their own row"
    on public.users for select
    using (auth.uid() = id);

create policy "Users can update their own row"
    on public.users for update
    using (auth.uid() = id);

-- -----------------------------------------------------------------------------
-- tax_rules  (reference data: deduction categories + cumulative caps)
-- -----------------------------------------------------------------------------
create table if not exists public.tax_rules (
    id            uuid primary key default gen_random_uuid(),
    category_name text not null,
    max_limit     numeric not null default 0,
    -- Calendar-era (CE) year, e.g. 2026. Matches
    -- settings.DEFAULT_TAX_YEAR = datetime.now().year and the tax_rules
    -- endpoint's `tax_year: Optional[int] = 2026` default. NOT Buddhist Era.
    tax_year      integer not null,
    is_active     boolean not null default true,
    created_at    timestamptz not null default now()
);

create index if not exists tax_rules_lookup_idx
    on public.tax_rules (category_name, tax_year, is_active);

alter table public.tax_rules enable row level security;

create policy "Authenticated users can read tax rules"
    on public.tax_rules for select
    to authenticated
    using (true);

-- TODO(owner): tax_rules starts EMPTY. The app has zero deduction categories
-- until you seed it. Insert one row per category your tax_expert classifier
-- can emit (at minimum: Health Insurance, Life Insurance, SSF; also RMF,
-- Provident Fund, Thai ESG, donation categories as used by the classifier).
-- Take every max_limit figure from backend/SOURCES.md + backend/app/core/
-- tax_constants.py — do NOT invent limits. Example shape only:
--
--   insert into public.tax_rules (category_name, max_limit, tax_year, is_active)
--   values ('Health Insurance', <from SOURCES.md>, 2026, true),
--          ('Life Insurance',   <from SOURCES.md>, 2026, true),
--          ('SSF',              <from SOURCES.md>, 2026, true);

-- -----------------------------------------------------------------------------
-- transactions  (one row per receipt / manual entry)
-- -----------------------------------------------------------------------------
create table if not exists public.transactions (
    id                uuid primary key default gen_random_uuid(),
    user_id           uuid not null references auth.users (id) on delete cascade,
    -- Nullable: set to NULL when the receipt is not deductible or its category
    -- has no matching tax_rules row (accountant.insert_transaction).
    rule_id           uuid references public.tax_rules (id) on delete set null,
    receipt_image_url text,
    merchant_name     text,
    merchant_tax_id   text,
    transaction_date  date,
    total_amount      numeric not null default 0,
    deductible_amount numeric not null default 0,
    -- Observed values: 'needs_review', 'verified', 'not_deductible', 'rejected'.
    status            text not null default 'needs_review',
    ai_reasoning      text,
    -- NOTE: the column name is literally "create_at" (missing the 'd').
    -- accountant.get_user_transactions orders by it and dashboard.py selects
    -- it. Renaming to created_at REQUIRES changing those call sites too.
    create_at         timestamptz not null default now()
);

create index if not exists transactions_user_idx
    on public.transactions (user_id);
create index if not exists transactions_user_rule_status_idx
    on public.transactions (user_id, rule_id, status);

alter table public.transactions enable row level security;

create policy "Users can read their own transactions"
    on public.transactions for select
    using (auth.uid() = user_id);

create policy "Users can insert their own transactions"
    on public.transactions for insert
    with check (auth.uid() = user_id);

create policy "Users can update their own transactions"
    on public.transactions for update
    using (auth.uid() = user_id);

create policy "Users can delete their own transactions"
    on public.transactions for delete
    using (auth.uid() = user_id);

-- -----------------------------------------------------------------------------
-- income_summary  (v2 — POST /income/sync). Identical to
-- backend/migrations/001_income_summary.sql; included here so a fresh project
-- gets the full schema in one run. Not needed for login, needed for /income/sync.
-- -----------------------------------------------------------------------------
create table if not exists public.income_summary (
    id              uuid primary key default gen_random_uuid(),
    user_id         uuid not null references auth.users (id) on delete cascade,
    period          text not null,
    platform_totals jsonb not null default '{}'::jsonb,
    total_gross     numeric not null default 0,
    total_fee       numeric not null default 0,
    total_net       numeric not null default 0,
    record_count    integer not null default 0,
    synced_at       timestamptz not null default now(),
    unique (user_id, period)
);

alter table public.income_summary enable row level security;

create policy "Users can read their own income summaries"
    on public.income_summary for select
    using (auth.uid() = user_id);

create policy "Users can upsert their own income summaries"
    on public.income_summary for insert
    with check (auth.uid() = user_id);

create policy "Users can update their own income summaries"
    on public.income_summary for update
    using (auth.uid() = user_id);
