"""POST /income/sync: period auto-resolution, and the enriched response
(tax_estimate + deduction_suggestions) that comes from routing through the
compiled workflow instead of calling the services by hand.
"""
from unittest.mock import patch

from app.api.v1.endpoints.income import _resolve_period
from app.core.security import get_current_user_id
from main import app

SELLER_ID = "seller-1"


def test_resolve_period_uses_requested_period_verbatim():
    assert _resolve_period(SELLER_ID, "2026") == "2026"


def test_resolve_period_falls_back_to_prior_year_when_current_year_empty():
    # No fixture data is seeded for year 2099, so resolution must fall
    # back to the prior year rather than syncing an empty period.
    with patch("app.api.v1.endpoints.income.datetime") as mock_datetime:
        mock_datetime.now.return_value.year = 2099
        assert _resolve_period(SELLER_ID, None) == "2098"


def test_sync_income_returns_tax_estimate_and_suggestions(client):
    app.dependency_overrides[get_current_user_id] = lambda: SELLER_ID

    try:
        with patch("app.agents.accountant.get_active_tax_rules", return_value=[]), \
             patch("app.api.v1.endpoints.income.supabase") as mock_supabase:
            mock_supabase.table.return_value.upsert.return_value.execute.return_value = None

            response = client.post("/api/v1/income/sync", json={"period": "2026"})

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["period"] == "2026"
        assert data["grand_total"]["record_count"] > 0
        assert "tax_due" in data["tax_estimate"]
        assert data["tax_estimate"]["brackets_verified"] is True
        assert data["deduction_suggestions"] == []
    finally:
        app.dependency_overrides.pop(get_current_user_id, None)
