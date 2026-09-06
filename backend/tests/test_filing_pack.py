"""build_filing_pack: PND94 vs PND90 income scoping, expense-method
comparison, box mapping, and deadline/verification bookkeeping.

Uses the same seeded fixtures as test_income_aggregator.py (dated across
the whole current tax year, so PND94's Jan-Jun scoping is actually
exercised).
Deduction-category lookups are patched to an empty rule list so this test
never hits real Supabase (see conftest.py / test_advisor.py's pattern).
"""
from datetime import date, timedelta
from unittest.mock import patch

import pytest

from app.services import filing_pack
from app.services.filing_pack import FormType, build_filing_pack
from app.services.income_aggregator import aggregate_income

SELLER_ID = "seller-1"
TAX_YEAR = 2026


def _build(form_type, tax_year=TAX_YEAR):
    with patch("app.agents.accountant.get_active_tax_rules", return_value=[]):
        return build_filing_pack(SELLER_ID, form_type, tax_year)


def test_pnd94_income_matches_jan_jun_aggregation_and_excludes_jul_dec():
    pack = _build(FormType.PND94)

    expected = aggregate_income(SELLER_ID, str(TAX_YEAR), f"{TAX_YEAR}-01-01", f"{TAX_YEAR}-06-30")
    assert pack["income"]["grand_total"]["gross_amount"] == expected["grand_total"]["gross_amount"]
    assert pack["income"]["grand_total"]["record_count"] == expected["grand_total"]["record_count"]
    assert pack["income"]["grand_total"]["record_count"] > 0

    for record in pack["income"]["records"]:
        month = int(record.date.split("-")[1])
        assert 1 <= month <= 6


def test_pnd90_income_matches_full_year_aggregation():
    pack = _build(FormType.PND90)

    expected = aggregate_income(SELLER_ID, str(TAX_YEAR))
    assert pack["income"]["grand_total"]["gross_amount"] == expected["grand_total"]["gross_amount"]
    assert pack["income"]["grand_total"]["record_count"] == expected["grand_total"]["record_count"]

    full_year_records = expected["grand_total"]["record_count"]
    half_year = _build(FormType.PND94)["income"]["grand_total"]["record_count"]
    assert half_year < full_year_records


def test_expense_comparison_has_both_methods_and_correct_difference():
    pack = _build(FormType.PND90)
    comparison = pack["expense_comparison"]

    assert "flat" in comparison and "actual" in comparison
    assert comparison["documented_expenses_source"] == "none_recorded"

    expected_diff = round(abs(comparison["flat"]["tax_due"] - comparison["actual"]["tax_due"]), 2)
    assert comparison["baht_difference"] == expected_diff


@pytest.mark.parametrize("form_type", [FormType.PND94, FormType.PND90])
def test_box_mapping_non_empty_with_notes(form_type):
    pack = _build(form_type)

    assert len(pack["box_mapping"]) > 0
    for row in pack["box_mapping"]:
        assert row["note"]  # every row cites something, real page or cross-reference


def test_deadline_days_remaining_computed_not_hardcoded():
    pack_a = _build(FormType.PND94, tax_year=2026)
    pack_b = _build(FormType.PND94, tax_year=2030)

    # Different tax_years must produce different deadlines/days_remaining --
    # if this were hardcoded, both would collapse to the same value.
    assert pack_a["deadline"]["deadline_date"] != pack_b["deadline"]["deadline_date"]
    assert pack_a["deadline"]["days_remaining"] != pack_b["deadline"]["days_remaining"]

    expected_deadline = date(2026, 9, 30)  # PND94 paper deadline: 30 Sep of tax_year
    expected_days = (expected_deadline - date.today()).days
    assert pack_a["deadline"]["days_remaining"] == expected_days
    assert pack_a["deadline"]["is_overdue"] == (expected_days < 0)


def test_pack_flags_unverified_when_brackets_not_verified(monkeypatch):
    monkeypatch.setattr(filing_pack, "BRACKETS_VERIFIED", False)

    pack = _build(FormType.PND90)

    assert pack["verification_status"]["brackets_verified"] is False
    assert pack["verification_status"]["unverified"] is True


def test_pack_verified_when_both_flags_true():
    pack = _build(FormType.PND90)

    assert pack["verification_status"]["brackets_verified"] is True
    assert pack["verification_status"]["tax_constants_verified"] is True
    assert pack["verification_status"]["unverified"] is False


def test_disclaimer_present_and_no_filing_claims():
    pack = _build(FormType.PND90)

    assert pack["disclaimer"]
    banned_phrases = ["auto-file", "submit for you", "e-filing integration"]
    haystack = str(pack).lower()
    for phrase in banned_phrases:
        assert phrase not in haystack
