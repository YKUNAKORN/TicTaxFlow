"""Deduction optimisation advisor: marginal-saving math, headroom lookup
(reusing accountant.py's cumulative-cap logic), and ranked suggestions.
"""
from unittest.mock import patch

from app.agents import accountant
from app.services import advisor


# --- compute_marginal_saving: pure math, fixed rate + known headroom ---


def test_compute_marginal_saving_multiplies_headroom_by_marginal_rate():
    # 40,000 THB of remaining headroom at a fixed 20% marginal rate.
    assert advisor.compute_marginal_saving(40000.0, 0.20) == 8000.0


def test_compute_marginal_saving_zero_headroom_saves_nothing():
    assert advisor.compute_marginal_saving(0.0, 0.20) == 0.0


def test_compute_marginal_saving_zero_rate_saves_nothing():
    assert advisor.compute_marginal_saving(40000.0, 0.0) == 0.0


def test_compute_marginal_saving_negative_headroom_clamped_to_zero():
    # A category that is already over its cap must never report a
    # negative "saving".
    assert advisor.compute_marginal_saving(-5000.0, 0.20) == 0.0


# --- get_category_headroom: reuses accountant.py's cap logic, not re-implemented ---


FAKE_RULES = [
    {"id": "rule-life", "category_name": "Life Insurance", "max_limit": 100000.0},
    {"id": "rule-provident", "category_name": "Provident Fund", "max_limit": 10000.0},
    {"id": "rule-donation", "category_name": "Donation (General)", "max_limit": 0.0},
]


def _used_by_rule(rule_id_to_used):
    def _fake_get_used(user_id, rule_id, exclude_transaction_id=None):
        return rule_id_to_used.get(rule_id, 0.0)
    return _fake_get_used


def test_get_category_headroom_computes_remaining_via_cap_logic():
    with patch.object(accountant, "get_active_tax_rules", return_value=FAKE_RULES), \
         patch.object(
             accountant,
             "get_used_deductible_amount",
             side_effect=_used_by_rule({"rule-life": 60000.0, "rule-provident": 10000.0}),
         ):
        headroom = advisor.get_category_headroom("user-1")

    by_category = {h["category_name"]: h for h in headroom}

    assert by_category["Life Insurance"]["remaining"] == 40000.0
    assert by_category["Provident Fund"]["remaining"] == 0.0
    # Income-based cap (max_limit == 0) has no fixed headroom to top up.
    assert "Donation (General)" not in by_category


# --- suggest_deduction_optimizations: ranked, numerically-correct suggestions ---


def test_suggest_deduction_optimizations_ranks_biggest_saving_first():
    """Seeded user: Life Insurance has 40,000 THB headroom, Provident Fund
    has 5,000 THB headroom. At a fixed 20% marginal bracket, Life Insurance
    must rank first with an exact 8,000 THB estimated saving."""
    with patch.object(accountant, "get_active_tax_rules", return_value=FAKE_RULES), \
         patch.object(
             accountant,
             "get_used_deductible_amount",
             side_effect=_used_by_rule({"rule-life": 60000.0, "rule-provident": 5000.0}),
         ), \
         patch("app.services.advisor.get_marginal_rate", return_value=0.20), \
         patch.object(advisor, "_rule_reference", return_value=""):
        suggestions = advisor.suggest_deduction_optimizations("user-1", taxable_income=750000.0)

    assert len(suggestions) >= 1
    assert suggestions[0]["category_name"] == "Life Insurance"
    assert suggestions[0]["top_up_amount"] == 40000.0
    assert suggestions[0]["marginal_rate"] == 0.20
    assert suggestions[0]["estimated_tax_saving"] == 8000.0

    # Ranked biggest saving first.
    savings = [s["estimated_tax_saving"] for s in suggestions]
    assert savings == sorted(savings, reverse=True)


def test_suggest_deduction_optimizations_skips_categories_already_full():
    with patch.object(accountant, "get_active_tax_rules", return_value=FAKE_RULES), \
         patch.object(
             accountant,
             "get_used_deductible_amount",
             side_effect=_used_by_rule({"rule-life": 100000.0, "rule-provident": 10000.0}),
         ), \
         patch("app.services.advisor.get_marginal_rate", return_value=0.20):
        suggestions = advisor.suggest_deduction_optimizations("user-1", taxable_income=750000.0)

    assert suggestions == []
