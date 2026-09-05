"""Progressive Thai Personal Income Tax (PIT) estimation.

Pure calculation only -- no I/O, no DB, no LangChain/LangGraph imports here.
`estimate_pit` is called from `services/workflow.py` as a graph node.
"""
from typing import Optional

# ---------------------------------------------------------------------------
# PIT_BRACKETS -- PLACEHOLDER, NOT VERIFIED.
#
# DO NOT use these figures for any real estimate or demo. They exist only
# so estimate_pit()'s bracket-walking arithmetic can be unit tested before
# the real numbers are available.
#
# TODO(owner): replace with figures confirmed against the Revenue
# Department (https://www.rd.go.th) for the target tax year (note: RD
# personal income tax rates have been stable for several years, but must
# be re-confirmed, not assumed), then flip BRACKETS_VERIFIED to True and
# delete/update test_brackets_are_verified_before_shipping in
# tests/test_tax_estimator.py.
#
# Each entry: (bracket_min, bracket_max_or_None_for_unbounded, rate).
PIT_BRACKETS: list[tuple[float, Optional[float], float]] = [
    (0, 100_000, 0.00),
    (100_000, 300_000, 0.05),
    (300_000, 600_000, 0.10),
    (600_000, None, 0.20),
]

BRACKETS_VERIFIED = False


def estimate_pit(taxable_income: float) -> dict:
    """Apply PIT_BRACKETS to `taxable_income` and return tax due plus a
    per-bracket breakdown. Pure function: same input always gives same
    output, no side effects.
    """
    if taxable_income < 0:
        raise ValueError("taxable_income must be non-negative")

    breakdown = []
    tax_due = 0.0

    for bracket_min, bracket_max, rate in PIT_BRACKETS:
        upper = bracket_max if bracket_max is not None else taxable_income
        taxable_at_rate = max(0.0, min(taxable_income, upper) - bracket_min)
        tax_for_bracket = taxable_at_rate * rate

        breakdown.append({
            "bracket_min": bracket_min,
            "bracket_max": bracket_max,
            "rate": rate,
            "taxable_at_rate": round(taxable_at_rate, 2),
            "tax_for_bracket": round(tax_for_bracket, 2),
        })
        tax_due += tax_for_bracket

    return {
        "taxable_income": taxable_income,
        "tax_due": round(tax_due, 2),
        "brackets_verified": BRACKETS_VERIFIED,
        "breakdown": breakdown,
    }


def get_marginal_rate(taxable_income: float) -> float:
    """Rate of the top bracket `taxable_income` actually reaches -- the
    rate that applies to (and would be saved on) the next baht of
    deduction. Reuses `estimate_pit`'s breakdown instead of re-walking
    PIT_BRACKETS, so the two never disagree on which bracket an income
    falls into.
    """
    breakdown = estimate_pit(taxable_income)["breakdown"]
    active_brackets = [b for b in breakdown if b["taxable_at_rate"] > 0]

    if not active_brackets:
        return breakdown[0]["rate"]

    return active_brackets[-1]["rate"]
