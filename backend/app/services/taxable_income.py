"""Taxable-income calculation for Section 40(8) online-seller income.

Pure functions only -- no I/O, no DB, no LangGraph imports here (mirrors
tax_estimator.py). Fixes the bug where `estimate_tax_node` in workflow.py
fed `net_amount` (gross minus marketplace fees) straight into `estimate_pit`
as if it were taxable income: that skips the Section 40(8) statutory expense
deduction entirely AND every personal allowance.

Expense deduction methods (fact #4, backend/SOURCES.md):
  - "flat": 60% of GROSS income (tax_constants.PND94_FLAT_EXPENSE_RATE) --
    NOT net-of-marketplace-fees. Marketplace fees are a private commercial
    cost, not part of the Revenue Department's statutory expense base.
  - "actual": documented, retained receipts for actual necessary and
    reasonable expenses, used instead of the flat rate when they are larger.
"""
from typing import Literal

from app.core import tax_constants
from app.services.tax_estimator import estimate_pit

ExpenseMethod = Literal["flat", "actual"]


def _validate_non_negative(value: float, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")


def expense_deduction_flat(gross_income: float) -> float:
    """60% flat (เหมา) expense deduction against GROSS Section 40(8) income
    (fact #4 -- base is gross, not net of marketplace fees)."""
    _validate_non_negative(gross_income, "gross_income")
    return round(gross_income * tax_constants.PND94_FLAT_EXPENSE_RATE, 2)


def expense_deduction_actual(documented_expenses: float) -> float:
    """Actual documented expense deduction: returns `documented_expenses`
    as-is once validated non-negative. Any "is this actually necessary and
    reasonable" judgment happens outside this pure function (RD's rule, not
    ours to arbitrate)."""
    _validate_non_negative(documented_expenses, "documented_expenses")
    return round(documented_expenses, 2)


def compute_taxable_income(
    gross_income: float,
    expense_method: ExpenseMethod,
    documented_expenses: float,
    total_allowances: float,
) -> dict:
    """Taxable income = gross income - expense deduction - allowances,
    floored at 0 (Thai PIT taxable income cannot go negative).

    `total_allowances` is expected to already be the correct figure for the
    form in question -- e.g. for PND94, the caller applies
    tax_constants.PND94_ALLOWANCE_HALVING_FACTOR before passing it in here
    (fact #5). This function does not know or care which form it's for.
    """
    _validate_non_negative(gross_income, "gross_income")
    _validate_non_negative(documented_expenses, "documented_expenses")
    _validate_non_negative(total_allowances, "total_allowances")

    if expense_method == "flat":
        expense_deduction = expense_deduction_flat(gross_income)
    elif expense_method == "actual":
        expense_deduction = expense_deduction_actual(documented_expenses)
    else:
        raise ValueError(f"Unknown expense_method: {expense_method!r}")

    taxable_income = max(0.0, gross_income - expense_deduction - total_allowances)
    taxable_income = round(taxable_income, 2)

    return {
        "gross_income": gross_income,
        "expense_method": expense_method,
        "expense_deduction": expense_deduction,
        "total_allowances": total_allowances,
        "taxable_income": taxable_income,
    }


def compare_expense_methods(
    gross_income: float,
    documented_expenses: float,
    total_allowances: float,
) -> dict:
    """Compute taxable income and tax due under BOTH expense methods and
    report which is cheaper for the taxpayer.

    When "actual" wins, attaches a warning: a taxpayer who elects the
    actual-expense method without retained receipts/bookkeeping to back it
    up is worse off than they think -- RD can disallow undocumented actual
    expenses on audit, which would fall back to a smaller (or zero)
    deduction than the flat 60% they gave up.
    """
    _validate_non_negative(gross_income, "gross_income")
    _validate_non_negative(documented_expenses, "documented_expenses")
    _validate_non_negative(total_allowances, "total_allowances")

    flat_result = compute_taxable_income(gross_income, "flat", 0.0, total_allowances)
    actual_result = compute_taxable_income(gross_income, "actual", documented_expenses, total_allowances)

    flat_tax = estimate_pit(flat_result["taxable_income"])
    actual_tax = estimate_pit(actual_result["taxable_income"])

    flat_due = flat_tax["tax_due"]
    actual_due = actual_tax["tax_due"]

    if actual_due < flat_due:
        cheaper_method = "actual"
    elif flat_due < actual_due:
        cheaper_method = "flat"
    else:
        cheaper_method = "flat"  # tie: flat requires no bookkeeping, so it wins ties

    difference = round(abs(flat_due - actual_due), 2)

    warning = None
    if cheaper_method == "actual":
        warning = (
            "The actual-expense method only saves tax if you can produce documented, "
            "retained receipts for every claimed expense. Without bookkeeping to back it "
            "up, Revenue Department can disallow the deduction on audit, leaving you worse "
            "off than if you had used the 60% flat rate."
        )

    return {
        "flat": {
            "expense_deduction": flat_result["expense_deduction"],
            "taxable_income": flat_result["taxable_income"],
            "tax_due": flat_due,
        },
        "actual": {
            "expense_deduction": actual_result["expense_deduction"],
            "taxable_income": actual_result["taxable_income"],
            "tax_due": actual_due,
        },
        "cheaper_method": cheaper_method,
        "baht_difference": difference,
        "recordkeeping_warning": warning,
    }
