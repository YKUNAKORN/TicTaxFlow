"""Inspector JSON parsing, including a ```json fenced response from Gemini.

Mocks the Gemini call itself so this never hits the real API.
"""
from unittest.mock import MagicMock, patch

from app.agents import inspector


def test_extract_receipt_handles_json_code_fence():
    fake_response = MagicMock()
    fake_response.text = (
        '```json\n'
        '{"date": "2026-01-15", "amount": 500.0, "tax_id": "1234567890123", '
        '"merchant_name": "Test Store"}\n'
        '```'
    )

    with patch.object(inspector.genai_client.models, "generate_content", return_value=fake_response):
        result = inspector.extract_receipt_from_bytes(b"fake-image-bytes", mime_type="image/jpeg")

    assert result == {
        "date": "2026-01-15",
        "amount": 500.0,
        "tax_id": "1234567890123",
        "merchant_name": "Test Store",
    }


def test_extract_receipt_handles_plain_json_without_fence():
    fake_response = MagicMock()
    fake_response.text = (
        '{"date": "2026-01-15", "amount": 500.0, "tax_id": "1234567890123", '
        '"merchant_name": "Test Store"}'
    )

    with patch.object(inspector.genai_client.models, "generate_content", return_value=fake_response):
        result = inspector.extract_receipt_from_bytes(b"fake-image-bytes", mime_type="image/jpeg")

    assert result["merchant_name"] == "Test Store"
    assert "error" not in result
