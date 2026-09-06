"""POST /agent/chat: auth boundary, and that the conversational Q&A is
routed through the compiled LangGraph (run_tax_question_workflow -> Router
-> Tax Q&A node), not a direct agent call (CLAUDE.md orchestration rule).
"""
from unittest.mock import patch

from app.core.security import get_current_user_id
from main import app

USER = "user-x"


def test_chat_without_token_returns_401(client):
    response = client.post("/api/v1/agent/chat", json={"message": "hi"})
    assert response.status_code == 401


def test_chat_routes_through_workflow_tax_question_node(client):
    app.dependency_overrides[get_current_user_id] = lambda: USER
    try:
        with patch(
            "app.services.workflow.ask_tax_question",
            return_value="Easy E-Receipt deducts up to 50,000 THB.",
        ) as mock_qa:
            response = client.post(
                "/api/v1/agent/chat", json={"message": "Easy E-Receipt limit?"}
            )

        assert response.status_code == 200
        body = response.json()
        assert body["response"] == "Easy E-Receipt deducts up to 50,000 THB."
        assert "timestamp" in body
        mock_qa.assert_called_once()
    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


def test_chat_rejects_blank_message(client):
    app.dependency_overrides[get_current_user_id] = lambda: USER
    try:
        response = client.post("/api/v1/agent/chat", json={"message": "   "})
        assert response.status_code == 400
    finally:
        app.dependency_overrides.pop(get_current_user_id, None)
