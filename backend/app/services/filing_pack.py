"""Filing-pack builder for ภ.ง.ด.94 (mid-year) and ภ.ง.ด.90 (annual).

INTEGRITY RULE: this feature prepares a pack of figures the user copies
into RD's own e-Filing site themselves. It never files, submits, or sends
anything to the Revenue Department, and never claims to. Do not add
"auto-file"/"submit for you"/"e-filing integration" language anywhere in
this codebase (grep for it before shipping any change here).

Only ภ.ง.ด.94 and ภ.ง.ด.90 are supported -- NOT ภ.ง.ด.91 (salary-only,
Section 40(1)), which is out of scope: this product's users are Section
40(8) online sellers who file 94 and 90.
"""
import logging
from datetime import date, datetime
from enum import Enum
from typing import Optional

from app.core import tax_constants
from app.core.tax_constants import TAX_CONSTANTS_VERIFIED
from app.services import advisor
from app.services.filing_box_map import get_box_map
from app.services.income_aggregator import aggregate_income
from app.services.tax_estimator import BRACKETS_VERIFIED, estimate_pit
from app.services.taxable_income import compare_expense_methods

logger = logging.getLogger(__name__)


class FormType(str, Enum):
    PND94 = "PND94"  # mid-year, Section 40(5)-(8) income, Jan-Jun
    PND90 = "PND90"  # annual, Section 40(1)-(8)


DISCLAIMER = (
    "TicTaxFlow is not affiliated with, endorsed by, or connected to the Thai Revenue "
    "Department. This filing pack is a preparation aid that organises figures for you to "
    "review and copy into RD's own e-Filing site (or a paper form) yourself -- it is not "
    "tax advice, and TicTaxFlow does not file, submit, or transmit anything to the Revenue "
    "Department on your behalf. You are responsible for verifying every figure before you "
    "submit your own return."
)


def period_range_for_form(form_type: FormType, tax_year: int) -> tuple[str, str]:
    """Inclusive ISO (YYYY-MM-DD, YYYY-MM-DD) date range covered by
    `form_type` for `tax_year` (Christian-Era calendar year -- see
    app/api/v1/endpoints/filing.py's docstring for the BE/CE convention
    used at the API boundary). Sourced from app.core.tax_constants
    (fact #2/#3) -- the one canonical place this range is computed.
    """
    if form_type == FormType.PND94:
        start = f"{tax_year:04d}-{tax_constants.PND94_PERIOD_START_MONTH:02d}-{tax_constants.PND94_PERIOD_START_DAY:02d}"
        end = f"{tax_year:04d}-{tax_constants.PND94_PERIOD_END_MONTH:02d}-{tax_constants.PND94_PERIOD_END_DAY:02d}"
        return start, end
    if form_type == FormType.PND90:
        return f"{tax_year:04d}-01-01", f"{tax_year:04d}-12-31"
    raise ValueError(f"Unsupported form_type: {form_type!r}")


def filing_deadline(form_type: FormType, tax_year: int) -> dict:
    """Paper + online filing deadlines (ISO dates), plus days-remaining /
    overdue status computed at request time from `date.today()` -- never
    hardcoded (per task spec)."""
    if form_type == FormType.PND94:
        deadline_date = (
            f"{tax_year:04d}-{tax_constants.PND94_PAPER_DEADLINE_MONTH:02d}-"
            f"{tax_constants.PND94_PAPER_DEADLINE_DAY:02d}"
        )
        online_deadline_date = (
            f"{tax_year:04d}-{tax_constants.PND94_ONLINE_DEADLINE_MONTH:02d}-"
            f"{tax_constants.PND94_ONLINE_DEADLINE_DAY:02d}"
        )
    elif form_type == FormType.PND90:
        following_year = tax_year + 1
        deadline_date = (
            f"{following_year:04d}-{tax_constants.PND90_PAPER_DEADLINE_MONTH:02d}-"
            f"{tax_constants.PND90_PAPER_DEADLINE_DAY:02d}"
        )
        online_deadline_date = (
            f"{following_year:04d}-{tax_constants.PND90_ONLINE_DEADLINE_MONTH:02d}-"
            f"{tax_constants.PND90_ONLINE_DEADLINE_DAY:02d}"
        )
    else:
        raise ValueError(f"Unsupported form_type: {form_type!r}")

    deadline_dt = date.fromisoformat(deadline_date)
    today = datetime.now().date()
    days_remaining = (deadline_dt - today).days

    return {
        "form_type": form_type.value,
        "deadline_date": deadline_date,
        "online_deadline_date": online_deadline_date,
        "days_remaining": days_remaining,
        "is_overdue": days_remaining < 0,
    }


def _documented_expenses(user_id: str) -> tuple[float, str]:
    """Try to source actual documented business expenses for `user_id` from
    the existing schema. The current `transactions` table models RECEIPT
    DEDUCTIONS against personal tax_rules categories (health insurance,
    donations, Easy E-Receipt, ...) -- there is no table/column tagging a
    transaction as a Section 40(8) BUSINESS expense (cost of goods,
    marketplace subscription fees, shipping supplies, etc.), so there is
    nothing safe to sum here yet without adding a new table.

    Returns (0.0, "none_recorded") so the caller can flag the actual-method
    column as empty rather than showing a real 0 THB of expenses.
    """
    return 0.0, "none_recorded"


def _total_allowances(user_id: str, form_type: FormType, tax_year: int) -> tuple[float, str]:
    """Total allowance/deduction amount to subtract when computing taxable
    income, plus a note on how it was derived.

    JUDGMENT CALL (see final report): the existing schema only models
    receipt-backed deduction categories (app.agents.accountant / tax_rules
    table) -- there is no separate table for the fixed statutory personal/
    spouse/child allowance. This function sums each category's USED amount
    (accountant.get_used_deductible_amount, via advisor.get_category_headroom)
    as a stand-in for "total allowances claimed so far this tax year", and
    for PND94 applies tax_constants.PND94_ALLOWANCE_HALVING_FACTOR to that
    whole sum (fact #5: "personal and MOST other allowances are halved" on
    the mid-year form) rather than modelling the fixed personal/spouse/child
    allowance amounts as separate line items. This is an approximation, not
    a verified fact -- flagged here and in the filing pack's `deductions`
    section.
    """
    headroom = advisor.get_category_headroom(user_id, tax_year)
    used_total = round(sum(c["used"] for c in headroom), 2)

    if form_type == FormType.PND94:
        used_total = round(used_total * tax_constants.PND94_ALLOWANCE_HALVING_FACTOR, 2)
        note = (
            "PND94 (mid-year): allowances halved per fact #5 (rd.go.th/60580.html) — applied "
            "as a single halving factor over the sum of this year's used deduction categories, "
            "since the current schema does not separately model the fixed personal/spouse/child "
            "allowance amounts. Approximation, not a verified per-allowance figure."
        )
    else:
        note = (
            "PND90 (annual): full-year sum of this year's used deduction categories "
            "(app.agents.accountant cumulative-cap logic). Does not include the fixed "
            "personal/spouse/child allowance amounts, which are not yet modelled in the schema."
        )

    return used_total, note


def build_filing_pack(user_id: str, form_type: FormType, tax_year: int) -> dict:
    """Assemble the full filing pack for `user_id` / `form_type` / `tax_year`.

    `tax_year` is Christian Era (CE), matching app.core.config.DEFAULT_TAX_YEAR
    and the convention already used by app.agents.accountant's tax_rules
    queries (see app/api/v1/endpoints/filing.py docstring).
    """
    logger.info("build_filing_pack: user=%s form=%s tax_year=%s", user_id, form_type.value, tax_year)

    date_from, date_to = period_range_for_form(form_type, tax_year)
    income = aggregate_income(user_id, str(tax_year), date_from, date_to)
    gross_income = income["grand_total"]["gross_amount"]

    documented_expenses, documented_expenses_source = _documented_expenses(user_id)
    total_allowances, allowances_note = _total_allowances(user_id, form_type, tax_year)

    expense_comparison = compare_expense_methods(gross_income, documented_expenses, total_allowances)
    expense_comparison = {
        **expense_comparison,
        "documented_expenses": documented_expenses,
        "documented_expenses_source": documented_expenses_source,
    }

    winning_method = expense_comparison["cheaper_method"]
    winning_taxable_income = expense_comparison[winning_method]["taxable_income"]
    tax_due = estimate_pit(winning_taxable_income)

    deductions = advisor.get_category_headroom(user_id, tax_year)

    box_map = get_box_map(form_type.value)
    computed_values = {
        "gross_income": gross_income,
        "expense_deduction": expense_comparison[winning_method]["expense_deduction"],
        "total_allowances": total_allowances,
        "taxable_income": winning_taxable_income,
        "tax_due": tax_due["tax_due"],
    }
    box_mapping = [
        {
            "label_th": row["label_th"],
            "label_en": row["label_en"],
            "form_item": row["form_item"],
            "value": computed_values.get(row["field"]),
            "note": row["note"],
        }
        for row in box_map
    ]

    platforms = list(income["platform_totals"].keys())
    document_checklist = [
        f"Platform payout statement -- {platform}" for platform in platforms
    ] + [
        f"Receipts backing your \"{category['category_name']}\" deduction claims"
        for category in deductions
        if category["used"] > 0
    ] + [
        "Withholding tax certificate(s) (50 ทวิ), if any customer/platform withheld tax at source",
    ]
    if winning_method == "actual":
        document_checklist.append(
            "Documented receipts/bookkeeping for every actual business expense claimed "
            "(required to support the actual-expense method on audit)"
        )

    deadline = filing_deadline(form_type, tax_year)

    unverified = not (BRACKETS_VERIFIED and TAX_CONSTANTS_VERIFIED)

    return {
        "user_id": user_id,
        "form_type": form_type.value,
        "tax_year": tax_year,
        "income": income,
        "expense_comparison": expense_comparison,
        "deductions": {
            "categories": deductions,
            "total_allowances_used": total_allowances,
            "note": allowances_note,
        },
        "tax_due": tax_due,
        "box_mapping": box_mapping,
        "document_checklist": document_checklist,
        "deadline": deadline,
        "disclaimer": DISCLAIMER,
        "verification_status": {
            "brackets_verified": BRACKETS_VERIFIED,
            "tax_constants_verified": TAX_CONSTANTS_VERIFIED,
            "unverified": unverified,
        },
    }
