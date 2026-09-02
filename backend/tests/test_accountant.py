"""Cumulative deduction cap (roadmap Phase 1.3 / CLAUDE.md: caps are
cumulative per user + category + tax_year, never per single receipt).
"""
from unittest.mock import patch

from app.agents import accountant

FAKE_LIFE_INSURANCE_RULE = {
    "id": "rule-life-insurance",
    "category_name": "Life Insurance",
    "max_limit": 100000.0,
}


def test_calculate_deductible_amount_caps_at_remaining_limit_when_already_used():
    """Two 80,000 THB receipts in the same 100,000 THB category: the second
    must be capped at the 20,000 THB remaining headroom, not stored as a
    fresh 80,000 THB (which would make the cumulative total 160,000)."""
    with patch.object(accountant, "get_tax_rule_by_category", return_value=FAKE_LIFE_INSURANCE_RULE):
        result = accountant.calculate_deductible_amount(
            total_amount=80000.0,
            category_name="Life Insurance",
            already_used=80000.0,
        )

    assert result["amount"] == 20000.0
    assert result["is_capped"] is True
    assert result["max_limit"] == 100000.0


def test_calculate_deductible_amount_under_limit_is_not_capped():
    with patch.object(accountant, "get_tax_rule_by_category", return_value=FAKE_LIFE_INSURANCE_RULE):
        result = accountant.calculate_deductible_amount(
            total_amount=30000.0,
            category_name="Life Insurance",
            already_used=40000.0,
        )

    assert result["amount"] == 30000.0
    assert result["is_capped"] is False


def test_calculate_deductible_amount_returns_zero_once_category_is_full():
    with patch.object(accountant, "get_tax_rule_by_category", return_value=FAKE_LIFE_INSURANCE_RULE):
        result = accountant.calculate_deductible_amount(
            total_amount=10000.0,
            category_name="Life Insurance",
            already_used=100000.0,
        )

    assert result["amount"] == 0.0
    assert result["is_capped"] is True
