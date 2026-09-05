"""estimate_pit: pure progressive PIT calculation against PIT_BRACKETS.

PIT_BRACKETS is now VERIFIED against the Revenue Department's official
English site (https://rd.go.th/english/6045.html, retrieved 2026-09-05) --
see backend/SOURCES.md. These hand-computed cases check the bracket-walking
arithmetic against the REAL figures.
"""
import pytest

from app.services.tax_estimator import estimate_pit, PIT_BRACKETS, BRACKETS_VERIFIED


def test_income_within_first_bracket_only():
    # 0-150,000 @ 0%: entirely inside the exempt bracket.
    result = estimate_pit(80_000)

    assert result["tax_due"] == 0.0


def test_income_spanning_two_brackets_hand_computed():
    # 250,000 taxable:
    #   0-150,000            @0%  -> 0
    #   150,000-250,000 (100,000) @5%  -> 5,000
    # total = 5,000
    result = estimate_pit(250_000)

    assert result["tax_due"] == 5_000.0


def test_income_spanning_four_brackets_hand_computed():
    # 750,000 taxable (lands exactly on the 500k-750k / 750k-1M edge, so the
    # 20% bracket contributes 0):
    #   0-150,000             @0%  -> 0
    #   150,000-300,000 (150,000) @5%  -> 7,500
    #   300,000-500,000 (200,000) @10% -> 20,000
    #   500,000-750,000 (250,000) @15% -> 37,500
    # total = 65,000
    result = estimate_pit(750_000)

    assert result["tax_due"] == 65_000.0


def test_boundary_exactly_at_bracket_edge_has_zero_in_next_bracket():
    # Exactly at the 150,000 edge: no income falls into the 150k-300k slice yet.
    result = estimate_pit(150_000)

    assert result["tax_due"] == 0.0


def test_boundary_one_unit_above_bracket_edge():
    # tax_due is rounded to the nearest cent (money), so the offset must be
    # large enough to survive that rounding: 1 baht into the 5% bracket.
    result = estimate_pit(150_001)

    assert result["tax_due"] == pytest.approx(0.05)


def test_breakdown_lists_every_bracket_with_amount_and_tax():
    result = estimate_pit(750_000)
    breakdown = result["breakdown"]

    assert len(breakdown) == len(PIT_BRACKETS) == 8
    assert breakdown[0]["tax_for_bracket"] == 0.0
    assert breakdown[1]["tax_for_bracket"] == 7_500.0
    assert breakdown[2]["tax_for_bracket"] == 20_000.0
    assert breakdown[3]["tax_for_bracket"] == 37_500.0
    assert breakdown[4]["tax_for_bracket"] == 0.0
    assert sum(b["tax_for_bracket"] for b in breakdown) == result["tax_due"]


def test_income_spanning_into_25_percent_bracket_hand_computed():
    # 1,500,000 taxable:
    #   0-150,000                @0%  -> 0
    #   150,000-300,000 (150,000)     @5%  -> 7,500
    #   300,000-500,000 (200,000)     @10% -> 20,000
    #   500,000-750,000 (250,000)     @15% -> 37,500
    #   750,000-1,000,000 (250,000)   @20% -> 50,000
    #   1,000,000-1,500,000 (500,000) @25% -> 125,000
    # total = 240,000
    result = estimate_pit(1_500_000)

    assert result["tax_due"] == 240_000.0


def test_income_spanning_top_35_percent_bracket_hand_computed():
    # 5,000,000 taxable:
    #   0-150,000                    @0%  -> 0
    #   150,000-300,000 (150,000)         @5%  -> 7,500
    #   300,000-500,000 (200,000)         @10% -> 20,000
    #   500,000-750,000 (250,000)         @15% -> 37,500
    #   750,000-1,000,000 (250,000)       @20% -> 50,000
    #   1,000,000-2,000,000 (1,000,000)   @25% -> 250,000
    #   2,000,000-4,000,000 (2,000,000)   @30% -> 600,000
    #   4,000,000-5,000,000 (1,000,000)   @35% -> 350,000
    # total = 1,315,000
    result = estimate_pit(5_000_000)

    assert result["tax_due"] == 1_315_000.0


def test_negative_income_rejected():
    with pytest.raises(ValueError):
        estimate_pit(-1)


def test_brackets_are_verified_before_shipping():
    assert BRACKETS_VERIFIED is True
