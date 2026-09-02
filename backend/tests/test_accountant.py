"""Tests for the cumulative per-user + category + tax_year deduction cap.

Reproduces the bug from the roadmap: two Life Insurance receipts of
80,000 THB each against a 100,000 THB cap must together deduct exactly
100,000 THB, not the raw sum of 160,000 THB.

None of these tests hit a real Supabase project. The pure cumulative-cap
math (compute_deductible_amount) is tested directly with injected
already_used/max_limit values, and calculate_deductible_amount is tested
with its DB lookups monkeypatched out.
"""
from app.agents import accountant


class TestComputeDeductibleAmount:
    """Pure cumulative-cap math, no I/O."""

    def test_first_receipt_under_cap_is_fully_deductible(self):
        result = accountant.compute_deductible_amount(
            total_amount=80_000, max_limit=100_000, already_used=0
        )
        assert result["amount"] == 80_000
        assert result["is_capped"] is False
        assert result["over_limit"] is False

    def test_two_receipts_together_equal_the_cap_not_the_raw_sum(self):
        # The bug: each receipt used to be capped against max_limit in
        # isolation, so two 80,000 THB receipts each deducted 80,000 THB
        # (raw sum 160,000 THB) against a 100,000 THB cap.
        first = accountant.compute_deductible_amount(
            total_amount=80_000, max_limit=100_000, already_used=0
        )
        second = accountant.compute_deductible_amount(
            total_amount=80_000, max_limit=100_000, already_used=first["amount"]
        )

        assert first["amount"] == 80_000
        assert second["amount"] == 20_000
        assert second["is_capped"] is True

        total_deductible = first["amount"] + second["amount"]
        assert total_deductible == 100_000

    def test_receipt_when_category_already_at_cap_is_over_limit(self):
        result = accountant.compute_deductible_amount(
            total_amount=50_000, max_limit=100_000, already_used=100_000
        )
        assert result["amount"] == 0
        assert result["is_capped"] is True
        assert result["over_limit"] is True

    def test_already_used_beyond_cap_floors_deductible_at_zero(self):
        result = accountant.compute_deductible_amount(
            total_amount=10_000, max_limit=100_000, already_used=150_000
        )
        assert result["amount"] == 0
        assert result["over_limit"] is True

    def test_exact_fit_is_not_flagged_as_capped(self):
        result = accountant.compute_deductible_amount(
            total_amount=20_000, max_limit=100_000, already_used=80_000
        )
        assert result["amount"] == 20_000
        assert result["is_capped"] is False
        assert result["over_limit"] is False


class TestCalculateDeductibleAmountCumulative:
    """calculate_deductible_amount with the Supabase-backed lookups
    (get_tax_rule_by_category, get_category_used_amount) monkeypatched."""

    def _patch_tax_rule(self, monkeypatch, max_limit=100_000):
        tax_rule = {
            "id": "rule-life-insurance-2026",
            "category_name": "Life Insurance",
            "max_limit": max_limit,
        }
        monkeypatch.setattr(
            accountant, "get_tax_rule_by_category",
            lambda category_name, tax_year=None: tax_rule
        )
        return tax_rule

    def test_two_receipts_together_do_not_exceed_the_category_cap(self, monkeypatch):
        self._patch_tax_rule(monkeypatch, max_limit=100_000)

        # Simulates the "already_used" total growing as each receipt is
        # verified and saved, without touching a real database.
        already_used = {"value": 0}
        monkeypatch.setattr(
            accountant, "get_category_used_amount",
            lambda user_id, rule_id, exclude_transaction_id=None: already_used["value"]
        )

        first = accountant.calculate_deductible_amount(80_000, "Life Insurance", user_id="user-1")
        already_used["value"] = first["amount"]
        second = accountant.calculate_deductible_amount(80_000, "Life Insurance", user_id="user-1")

        total_deductible = first["amount"] + second["amount"]

        assert total_deductible == 100_000
        assert first["is_capped"] is False
        assert second["is_capped"] is True
        assert second["over_limit"] is False  # partially capped, not yet fully blocked

        already_used["value"] = 100_000
        third = accountant.calculate_deductible_amount(80_000, "Life Insurance", user_id="user-1")
        assert third["amount"] == 0
        assert third["over_limit"] is True

    def test_unknown_category_returns_zero_without_crashing(self, monkeypatch):
        monkeypatch.setattr(
            accountant, "get_tax_rule_by_category",
            lambda category_name, tax_year=None: None
        )
        result = accountant.calculate_deductible_amount(1_000, "Not A Real Category", user_id="user-1")
        assert result == {"amount": 0.0, "is_capped": False, "max_limit": 0.0}

    def test_income_based_category_is_not_cumulatively_capped(self, monkeypatch):
        # max_limit == 0 means an income-based limit (e.g. general donations);
        # the fixed cumulative cap does not apply.
        self._patch_tax_rule(monkeypatch, max_limit=0)
        result = accountant.calculate_deductible_amount(5_000, "Life Insurance", user_id="user-1")
        assert result["amount"] == 5_000
        assert result["is_capped"] is False
