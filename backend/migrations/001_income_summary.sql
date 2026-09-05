-- income_summary table for POST /income/sync.
-- Checked live Supabase schema on 2026-09-05: table does not exist yet
-- (PGRST205 "Could not find the table 'public.income_summary'"). Run this
-- manually in the Supabase SQL editor before /income/sync is exercised
-- against the real database.

create table if not exists public.income_summary (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    period text not null,
    platform_totals jsonb not null default '{}'::jsonb,
    total_gross numeric not null default 0,
    total_fee numeric not null default 0,
    total_net numeric not null default 0,
    record_count integer not null default 0,
    synced_at timestamptz not null default now(),
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
