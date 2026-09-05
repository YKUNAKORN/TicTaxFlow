"""Deduction optimisation advisor.

Ranks "top up X in category Y -> save ~Z THB" suggestions from:
  - remaining headroom per deduction category, via the cumulative-cap
    logic already in app.agents.accountant (never re-implemented here);
  - the marginal PIT rate implied by the user's estimated taxable
    income, via app.services.tax_estimator.

Category limits come from the `tax_rules` table (accountant.py) and any
descriptive reference text comes from the RAG knowledge base
(app.services.retrieval) -- never hardcoded prose about what a category
means, per CLAUDE.md.
"""
import logging
from typing import Any, Optional

from app.agents import accountant
from app.services import retrieval
from app.services.tax_estimator import get_marginal_rate

logger = logging.getLogger(__name__)

MAX_SUGGESTIONS = 3


def compute_marginal_saving(remaining_headroom: float, marginal_rate: float) -> float:
    """Estimated tax saved by topping up `remaining_headroom` THB of
    deduction at `marginal_rate`.

    Linear approximation: the saving is the top-up amount taxed away at
    the single marginal rate, which holds as long as the top-up itself
    doesn't cross the user into a lower bracket.
    """
    return round(max(0.0, remaining_headroom) * marginal_rate, 2)


def get_category_headroom(user_id: str, tax_year: Optional[int] = None) -> list[dict[str, Any]]:
    """Used/remaining per deduction category for `user_id`, reusing the
    cumulative-cap logic in accountant.py.

    Categories with max_limit == 0 (income-based caps, e.g. general
    donations) are skipped: there is no fixed headroom to "top up".
    """
    headroom = []

    for rule in accountant.get_active_tax_rules(tax_year):
        max_limit = float(rule.get("max_limit") or 0)
        if max_limit <= 0:
            continue

        used = accountant.get_used_deductible_amount(user_id, rule["id"])
        remaining = max(0.0, max_limit - used)

        headroom.append({
            "category_name": rule["category_name"],
            "rule_id": rule["id"],
            "max_limit": max_limit,
            "used": used,
            "remaining": remaining,
        })

    return headroom


def _rule_reference(category_name: str) -> str:
    """Short RAG snippet describing the category's rule, grounding the
    suggestion's copy in the knowledge base instead of hardcoded prose."""
    try:
        chunks = retrieval.retrieve_context(f"{category_name} หักลดหย่อน", n_results=1)
        return chunks[0] if chunks else ""
    except Exception as e:
        logger.error("Error fetching rule reference for %s: %s", category_name, e)
        return ""


def suggest_deduction_optimizations(
    user_id: str,
    taxable_income: float,
    tax_year: Optional[int] = None,
) -> list[dict[str, Any]]:
    """Rank deduction top-up suggestions by estimated tax saving, biggest
    first. Returns at most MAX_SUGGESTIONS entries.
    """
    marginal_rate = get_marginal_rate(taxable_income)

    suggestions = []
    for category in get_category_headroom(user_id, tax_year):
        remaining = category["remaining"]
        if remaining <= 0:
            continue

        saving = compute_marginal_saving(remaining, marginal_rate)
        if saving <= 0:
            continue

        suggestions.append({
            "category_name": category["category_name"],
            "top_up_amount": remaining,
            "marginal_rate": marginal_rate,
            "estimated_tax_saving": saving,
            "rule_reference": _rule_reference(category["category_name"]),
        })

    suggestions.sort(key=lambda s: s["estimated_tax_saving"], reverse=True)
    return suggestions[:MAX_SUGGESTIONS]
