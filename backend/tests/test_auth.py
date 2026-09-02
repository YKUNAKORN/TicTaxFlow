"""Data endpoints must reject requests with no Bearer token (see core/security.py)."""


def test_dashboard_summary_without_token_returns_401(client):
    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code == 401


def test_dashboard_summary_with_malformed_token_returns_401(client):
    response = client.get(
        "/api/v1/dashboard/summary",
        headers={"Authorization": "not-a-bearer-token"},
    )

    assert response.status_code == 401
