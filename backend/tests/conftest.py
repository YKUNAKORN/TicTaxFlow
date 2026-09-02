"""Shared pytest fixtures for the backend smoke test suite.

These tests must never hit real Gemini or Supabase services. Dummy
credentials are set here, before any `app.*` module is imported, so that
`app.core.config` / `app.database.database` (which raise at import time if
SUPABASE_URL/SUPABASE_KEY are unset) succeed with fake values instead of
picking up real secrets from a developer's local .env file.
"""
import os

os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-supabase-key")

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
