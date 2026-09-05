"""Verified Thai tax figures for the ภ.ง.ด.94 / ภ.ง.ด.90 filing-pack feature
(PHASE 3A). Every figure here was checked against an official Revenue
Department (RD) source (or, where noted, RD's own FAQ/press explanation
plus corroborating current professional-accounting sources) on 2026-09-05.

This module holds ONLY filing-pack-specific constants (fact #2-#6 from the
Phase 3A verification pass). The PIT bracket table (fact #1) stays in
`app/services/tax_estimator.py` (`PIT_BRACKETS`, `BRACKETS_VERIFIED`) --
not duplicated here.

Do not hand-edit a number in this file without updating `backend/SOURCES.md`
to match, and vice versa -- they must always agree per CLAUDE.md's tax-domain
rule ("Read limits from the tax_rules table [or, for figures with no DB
table, an auditable constant with a source+year comment]; verify all figures
before any demo").
"""
TAX_CONSTANTS_VERIFIED: bool = True


# ---------------------------------------------------------------------------
# Fact #4: Section 40(8) flat-rate (เหมา) expense deduction.
# Source: Royal Decree No. 629 (B.E. 2560 / 2017), reported by Prachachat
# (https://www.prachachat.net/finance/news-50328) and corroborated by
# current (2568/2569) accounting-firm guides (PEAK, iTAX). In effect since
# tax year 2560, still current for 2568/2569. Retrieved 2026-09-05.
# Base is GROSS assessable income, NOT net of marketplace/platform fees --
# platform fees are a private commercial cost, not part of RD's statutory
# expense-allowance calculation base.
PND94_FLAT_EXPENSE_RATE: float = 0.60

# ---------------------------------------------------------------------------
# Fact #5: mid-year (PND94) allowances are HALVED relative to the annual
# PND90 form (e.g. personal allowance 30,000 THB on PND94 vs 60,000 THB
# annual; per-child allowance 15,000 THB on PND94 vs 30,000 THB annual).
# Source: https://www.rd.go.th/60580.html, retrieved 2026-09-05.
PND94_ALLOWANCE_HALVING_FACTOR: float = 0.5

# ---------------------------------------------------------------------------
# Fact #3: ภ.ง.ด.94 filing-obligation income threshold (Section 40(5)-(8)
# income only, Jan-Jun half). Source: https://www.rd.go.th/60580.html
# (RD official FAQ), retrieved 2026-09-05.
PND94_SINGLE_THRESHOLD: float = 60_000
PND94_MARRIED_THRESHOLD: float = 120_000

# ---------------------------------------------------------------------------
# Fact #2: filing windows.
#
# ภ.ง.ด.90 (annual, Section 40(1)-(8) income): paper filing 1 Jan - 31 Mar
# of the year following the tax year; e-Filing extension to 8 Apr.
# Source: https://www.rd.go.th/46202.html (RD's recurring annual extension
# announcement pattern), corroborated by 2569 news coverage (Thairath,
# Thansettakij, Sep 2026) confirming e-Filing deadline 8 Apr 2569 for tax
# year 2568 returns. Retrieved 2026-09-05.
PND90_PAPER_START_MONTH: int = 1
PND90_PAPER_START_DAY: int = 1
PND90_PAPER_DEADLINE_MONTH: int = 3
PND90_PAPER_DEADLINE_DAY: int = 31
PND90_ONLINE_DEADLINE_MONTH: int = 4
PND90_ONLINE_DEADLINE_DAY: int = 8

# ภ.ง.ด.94 (mid-year, Section 40(5)-(8) income only, covering Jan-Jun):
# paper filing 1 Jul - 30 Sep of the SAME tax year; e-Filing extension to
# ~8 Oct. Source: RD FAQ https://www.rd.go.th/60580.html and RD's historical
# extension-announcement pattern (same 8-day online extension convention as
# PND90/91), corroborated by current-year (2568) filing guides (Krungsri,
# KTC) stating online extension to 8 Oct. Retrieved 2026-09-05.
PND94_PERIOD_START_MONTH: int = 1
PND94_PERIOD_START_DAY: int = 1
PND94_PERIOD_END_MONTH: int = 6
PND94_PERIOD_END_DAY: int = 30
PND94_PAPER_START_MONTH: int = 7
PND94_PAPER_START_DAY: int = 1
PND94_PAPER_DEADLINE_MONTH: int = 9
PND94_PAPER_DEADLINE_DAY: int = 30
PND94_ONLINE_DEADLINE_MONTH: int = 10
PND94_ONLINE_DEADLINE_DAY: int = 8

# ---------------------------------------------------------------------------
# Fact #6: penalties for late/non-filing (same Revenue Code regime for both
# PND90 and PND94). Source: https://www.rd.go.th/37392.html, retrieved
# 2026-09-05.
LATE_FILING_FINE_MAX: float = 2_000  # มาตรา 35 criminal fine, up to this amount
LATE_PAYMENT_SURCHARGE_MONTHLY_RATE: float = 0.015  # เงินเพิ่ม, per month/part-month of unpaid tax
PENALTY_MAX_MULTIPLIER: float = 2.0  # เบี้ยปรับ can be up to 2x the tax due

# NOTE: period_range_for_form() / filing deadline computation live in
# app/services/filing_pack.py (the one canonical place), not here, so that
# this module stays a leaf (no import of FormType, which lives in
# filing_pack.py, avoiding a circular import).
