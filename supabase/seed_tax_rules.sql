-- TicTaxFlow — tax_rules seed (deduction categories + cumulative caps)
-- =============================================================================
-- Run this AFTER supabase/schema.sql, in the Supabase SQL editor (or via
-- `supabase db push`), against the same project your backend/.env points at.
--
-- WHY IT IS REQUIRED: schema.sql creates `tax_rules` EMPTY. Until it has rows:
--   * app/agents/accountant.py `get_tax_rule_by_category()` returns None for
--     every receipt, so each classified receipt is stored status='needs_review'
--     with deductible_amount 0 (it never counts toward a deduction total);
--   * the dashboard category breakdown and the deduction Optimisation Advisor
--     have nothing to show.
--
-- SCOPE / INTEGRITY (per CLAUDE.md's tax-domain rule): this is DEMO
-- SCAFFOLDING, not a verified statutory table. Each `max_limit` below mirrors
-- the "Base Knowledge: Thai Tax Deduction Categories" block that
-- backend/app/agents/tax_expert.py already prompts the classifier with, so the
-- classifier and the DB never disagree on camera. Before any non-demo use,
-- re-verify every figure against the current Revenue Department source
-- (https://rd.go.th) and keep this table the single source of truth — do not
-- also hardcode these numbers elsewhere.
--
-- `tax_year` is a Christian-Era (CE) calendar year, matching
-- settings.DEFAULT_TAX_YEAR (= datetime.now().year). When the calendar year
-- rolls over, re-run this with the new year (or add the new year's rows) so
-- accountant's default-year lookup keeps matching instead of falling back.
--
-- Idempotent: it replaces the rows for the target year, so it is safe to
-- re-run. Change :tax_year in one place if you need a different year.
-- =============================================================================

begin;

delete from public.tax_rules where tax_year = 2026;

insert into public.tax_rules (category_name, max_limit, tax_year, is_active) values
    ('Health Insurance',            25000,  2026, true),  -- self, health premiums
    ('Life Insurance',              100000, 2026, true),  -- 10y+ policy; combined w/ health <= 100k
    ('Pension Insurance',           200000, 2026, true),  -- annuity/retirement life premiums
    ('SSF',                         200000, 2026, true),  -- Super Savings Fund (also <= 30% income)
    ('RMF',                         500000, 2026, true),  -- Retirement Mutual Fund (also <= 30% income)
    ('Thai ESG',                    300000, 2026, true),  -- Thai ESG fund (also <= 30% income)
    ('Home Loan Interest',          100000, 2026, true),  -- mortgage interest paid
    ('Social Security',             9000,   2026, true),  -- employee SSO contributions
    ('Easy E-Receipt',              50000,  2026, true),  -- time-limited: 1 Jan 16 – 28 Feb window
    -- Income-based caps: max_limit 0 tells
    -- accountant.calculate_deductible_amount to use the amount-based path
    -- (actual amount for general donations; 2x for e-Donation education/sports),
    -- not a fixed ceiling. The statutory 10%-of-net-income cap on donations is
    -- a documented gap — see that function and DEMO.md "Known limits".
    ('Donation (General)',              0,  2026, true),
    ('Donation (Education/Sports)',     0,  2026, true);

commit;

-- Sanity check (optional): should return 12 rows.
-- select category_name, max_limit, tax_year from public.tax_rules where tax_year = 2026 order by category_name;
