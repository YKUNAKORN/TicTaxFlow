"""estimate_pit: pure progressive PIT calculation against PIT_BRACKETS.

NOTE: PIT_BRACKETS is currently a PLACEHOLDER (see tax_estimator.py) --
these hand-computed cases verify the bracket-walking ARITHMETIC is correct
against whatever figures live in that constant, not that the figures
themselves are the real Revenue Department numbers. `BRACKETS_VERIFIED`
must stay False, and test_brackets_are_verified_before_shipping below must
keep failing (xfail), until real figures replace the placeholder.
"""
import pytest

from app.services.tax_estimator import estimate_pit, PIT_BRACKETS, BRACKETS_VERIFIED


def test_income_within_first_bracket_only():
    # 0-100,000 @ 0% (placeholder): entirely inside the exempt bracket.
    result = estimate_pit(80_000)

    assert result["tax_due"] == 0.0


def test_income_spanning_three_brackets_hand_computed():
    # Placeholder brackets: (0-100k @0%), (100k-300k @5%), (300k-600k @10%), (600k+ @20%)
    # 250,000 taxable:
    #   0-100,000   @0%  -> 0
    #   100,000-250,000 (150,000) @5% -> 7,500
    # total = 7,500
    result = estimate_pit(250_000)

    assert result["tax_due"] == 7_500.0


def test_income_spanning_top_unbounded_bracket_hand_computed():
    # 750,000 taxable:
    #   0-100,000 @0%          -> 0
    #   100,000-300,000 @5%    -> 10,000
    #   300,000-600,000 @10%   -> 30,000
    #   600,000-750,000 @20%   -> 30,000
    # total = 70,000
    result = estimate_pit(750_000)

    assert result["tax_due"] == 70_000.0


def test_boundary_exactly_at_bracket_edge_has_zero_in_next_bracket():
    # Exactly at the 100,000 edge: no income falls into the 100k-300k slice yet.
    result = estimate_pit(100_000)

    assert result["tax_due"] == 0.0


def test_boundary_one_unit_above_bracket_edge():
    # tax_due is rounded to the nearest cent (money), so the offset must be
    # large enough to survive that rounding: 1 baht into the 5% bracket.
    result = estimate_pit(100_001)

    assert result["tax_due"] == pytest.approx(0.05)


def test_breakdown_lists_every_bracket_with_amount_and_tax():
    result = estimate_pit(750_000)
    breakdown = result["breakdown"]

    assert len(breakdown) == len(PIT_BRACKETS)
    assert breakdown[0]["tax_for_bracket"] == 0.0
    assert breakdown[1]["tax_for_bracket"] == 10_000.0
    assert breakdown[2]["tax_for_bracket"] == 30_000.0
    assert breakdown[3]["tax_for_bracket"] == 30_000.0
    assert sum(b["tax_for_bracket"] for b in breakdown) == result["tax_due"]


def test_negative_income_rejected():
    with pytest.raises(ValueError):
        estimate_pit(-1)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "PIT_BRACKETS is a PLACEHOLDER, not verified against the Revenue "
        "Department. This test must keep failing until real figures are "
        "confirmed and BRACKETS_VERIFIED is flipped to True -- if it ever "
        "passes by accident, strict=True turns that into a hard failure "
        "so unverified figures can't ship silently."
    ),
)
def test_brackets_are_verified_before_shipping():
    assert BRACKETS_VERIFIED is True
