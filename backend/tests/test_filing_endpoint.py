"""GET /filing/preview and /filing/forms: auth boundary, user-id scoping
from the token only (never a client-supplied parameter), and form_type
validation (PND91 explicitly out of scope).
"""
from unittest.mock import patch

from app.core.security import get_current_user_id
from main import app

USER_A = "user-a"


def test_preview_without_token_returns_401(client):
    response = client.get("/api/v1/filing/preview", params={"form_type": "PND90", "tax_year": 2025})

    assert response.status_code == 401


def test_preview_valid_token_returns_pack_scoped_to_that_user(client):
    app.dependency_overrides[get_current_user_id] = lambda: USER_A

    try:
        with patch("app.agents.accountant.get_active_tax_rules", return_value=[]):
            response = client.get(
                "/api/v1/filing/preview",
                params={"form_type": "PND90", "tax_year": 2025},
            )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["user_id"] == USER_A
    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


def test_preview_ignores_user_id_supplied_as_a_client_parameter(client):
    """user_id must come ONLY from the validated bearer token -- a
    query-string user_id (impersonation attempt) must not change whose data
    is returned, and in fact this endpoint has no such parameter at all."""
    app.dependency_overrides[get_current_user_id] = lambda: USER_A

    try:
        with patch("app.agents.accountant.get_active_tax_rules", return_value=[]):
            response = client.get(
                "/api/v1/filing/preview",
                params={"form_type": "PND90", "tax_year": 2025, "user_id": "someone-elses-id"},
            )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["user_id"] == USER_A
        assert data["user_id"] != "someone-elses-id"
    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


def test_preview_invalid_form_type_returns_422(client):
    app.dependency_overrides[get_current_user_id] = lambda: USER_A

    try:
        response = client.get(
            "/api/v1/filing/preview",
            params={"form_type": "NOT_A_FORM", "tax_year": 2025},
        )
        assert response.status_code == 422
    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


def test_preview_pnd91_explicitly_rejected(client):
    """PND91 (salary-only, Section 40(1)) is explicitly out of scope for
    this feature -- it must 422 like any other invalid enum value, not be
    silently accepted."""
    app.dependency_overrides[get_current_user_id] = lambda: USER_A

    try:
        response = client.get(
            "/api/v1/filing/preview",
            params={"form_type": "PND91", "tax_year": 2025},
        )
        assert response.status_code == 422
    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


def test_forms_without_token_returns_401(client):
    response = client.get("/api/v1/filing/forms")

    assert response.status_code == 401


def test_forms_lists_pnd94_and_pnd90_only(client):
    app.dependency_overrides[get_current_user_id] = lambda: USER_A

    try:
        response = client.get("/api/v1/filing/forms", params={"tax_year": 2025})

        assert response.status_code == 200
        forms = {f["form_type"] for f in response.json()["data"]["forms"]}
        assert forms == {"PND94", "PND90"}
    finally:
        app.dependency_overrides.pop(get_current_user_id, None)
