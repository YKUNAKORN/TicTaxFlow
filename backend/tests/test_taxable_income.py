"""compute_taxable_income / compare_expense_methods: pure arithmetic, hand
computed against the verified PND94_FLAT_EXPENSE_RATE (60%, fact #4) and
the real PIT_BRACKETS (fact #1). No DB/network/LangGraph involved.
"""
import pytest

from app.services.taxable_income import (
    expense_deduction_flat,
    expense_deduction_actual,
    compute_taxable_income,
    compare_expense_methods,
)


def test_expense_deduction_flat_is_60_percent_of_gross():
    # 60% of gross, NOT net-of-fees (fact #4's base is gross income).
    assert expense_deduction_flat(100_000) == 60_000.0
    assert expense_deduction_flat(1_000_000) == 600_000.0


def test_expense_deduction_actual_returns_documented_amount():
    assert expense_deduction_actual(75_000) == 75_000.0


def test_flat_method_taxable_income_floors_at_zero():
    # gross=100,000: flat expense=60,000, allowances=60,000 -> would be
    # negative (100,000 - 60,000 - 60,000 = -20,000), floored to 0.
    result = compute_taxable_income(100_000, "flat", 0.0, 60_000)

    assert result["expense_deduction"] == 60_000.0
    assert result["taxable_income"] == 0.0


def test_flat_method_taxable_income_hand_computed():
    # gross=1,000,000: flat expense = 600,000 (60%).
    # taxable = 1,000,000 - 600,000 - 60,000 (allowances) = 340,000.
    result = compute_taxable_income(1_000_000, "flat", 0.0, 60_000)

    assert result["expense_deduction"] == 600_000.0
    assert result["taxable_income"] == 340_000.0


def test_actual_method_taxable_income_hand_computed():
    # gross=1,000,000, documented actual expenses=750,000, allowances=60,000.
    # taxable = 1,000,000 - 750,000 - 60,000 = 190,000.
    result = compute_taxable_income(1_000_000, "actual", 750_000, 60_000)

    assert result["expense_deduction"] == 750_000.0
    assert result["taxable_income"] == 190_000.0


def test_compare_expense_methods_flat_wins_hand_computed():
    # gross=500,000, documented actual expenses=100,000 (small), allowances=60,000.
    #   flat:   expense=300,000 (60%) -> taxable=140,000 -> tax=0 (within 0-150k @0%)
    #   actual: expense=100,000       -> taxable=340,000 -> tax:
    #       0-150k@0%=0; 150k-300k(150k)@5%=7,500; 300k-340k(40k)@10%=4,000
    #       total = 11,500
    # flat is cheaper by exactly 11,500.
    result = compare_expense_methods(500_000, 100_000, 60_000)

    assert result["flat"]["tax_due"] == 0.0
    assert result["actual"]["tax_due"] == 11_500.0
    assert result["cheaper_method"] == "flat"
    assert result["baht_difference"] == 11_500.0
    assert result["recordkeeping_warning"] is None


def test_compare_expense_methods_actual_wins_hand_computed():
    # gross=1,000,000, documented actual expenses=900,000, allowances=60,000.
    #   flat:   expense=600,000 (60%) -> taxable=340,000 -> tax=11,500 (as above)
    #   actual: expense=900,000       -> taxable=40,000  -> tax=0 (within 0-150k @0%)
    # actual is cheaper by exactly 11,500, and must carry the recordkeeping warning.
    result = compare_expense_methods(1_000_000, 900_000, 60_000)

    assert result["flat"]["tax_due"] == 11_500.0
    assert result["actual"]["tax_due"] == 0.0
    assert result["cheaper_method"] == "actual"
    assert result["baht_difference"] == 11_500.0
    assert result["recordkeeping_warning"] is not None
    assert "receipts" in result["recordkeeping_warning"] or "records" in result["recordkeeping_warning"]


def test_zero_income_and_zero_expenses_do_not_raise():
    result = compute_taxable_income(0.0, "flat", 0.0, 0.0)
    assert result["taxable_income"] == 0.0

    compare = compare_expense_methods(0.0, 0.0, 0.0)
    assert compare["flat"]["tax_due"] == 0.0
    assert compare["actual"]["tax_due"] == 0.0
    assert compare["baht_difference"] == 0.0


def test_negative_gross_income_raises():
    with pytest.raises(ValueError):
        compute_taxable_income(-1.0, "flat", 0.0, 0.0)


def test_negative_documented_expenses_raises():
    with pytest.raises(ValueError):
        compute_taxable_income(100_000, "actual", -1.0, 0.0)


def test_negative_allowances_raises():
    with pytest.raises(ValueError):
        compute_taxable_income(100_000, "flat", 0.0, -1.0)


def test_compare_expense_methods_rejects_negative_inputs():
    with pytest.raises(ValueError):
        compare_expense_methods(-1.0, 0.0, 0.0)
    with pytest.raises(ValueError):
        compare_expense_methods(0.0, -1.0, 0.0)
    with pytest.raises(ValueError):
        compare_expense_methods(0.0, 0.0, -1.0)
