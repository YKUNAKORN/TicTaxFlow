"""LangGraph income path: seller_id+period -> aggregate_income ->
estimate_pit, so a synced income run ends with a tax estimate attached to
state. Uses the same seeded fixtures as test_income_aggregator.py."""
from unittest.mock import patch

from app.services.income_aggregator import aggregate_income
from app.services.tax_estimator import estimate_pit
from app.services.workflow import compiled_graph

SELLER_ID = "seller-1"
PERIOD = "2025"


def _base_state(**overrides):
    state = {
        "question": "",
        "image_path": None,
        "image_bytes": None,
        "image_url": None,
        "receipt_data": {},
        "tax_analysis": {},
        "tax_advice": "",
        "needs_human_input": False,
        "missing_fields": [],
        "status": "",
        "accountant_result": {},
        "user_id": "demo-user-id",
        "seller_id": None,
        "period": None,
        "income_data": {},
        "tax_estimate": {},
        "messages": [],
    }
    state.update(overrides)
    return state


def test_income_sync_flows_through_to_tax_estimate():
    # Advisor node runs after estimate_tax; stub its category lookup so
    # this test never hits real Supabase (see conftest.py).
    with patch("app.agents.accountant.get_active_tax_rules", return_value=[]):
        result = compiled_graph.invoke(
            _base_state(seller_id=SELLER_ID, period=PERIOD)
        )

    assert result["status"] == "completed"
    assert result["income_data"]["grand_total"]["record_count"] > 0

    expected_income = aggregate_income(SELLER_ID, PERIOD)
    expected_estimate = estimate_pit(expected_income["grand_total"]["net_amount"])

    assert result["tax_estimate"]["tax_due"] == expected_estimate["tax_due"]
    assert result["tax_estimate"]["breakdown"] == expected_estimate["breakdown"]
    assert result["deduction_suggestions"] == []


def test_no_seller_id_still_routes_to_tax_question_not_income():
    with patch(
        "app.services.workflow.ask_tax_question",
        return_value="Easy E-Receipt deducts up to a set cap per year.",
    ):
        result = compiled_graph.invoke(
            _base_state(question="What is Easy E-Receipt?")
        )

    assert result["income_data"] == {}
    assert result["tax_estimate"] == {}
    assert result["tax_advice"] != ""
