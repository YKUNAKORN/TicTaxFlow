"""Shared test setup.

Importing app.agents.accountant constructs a Supabase client at module
load time and requires SUPABASE_URL / SUPABASE_KEY to be set. These
placeholder values let the module import cleanly in tests without ever
making a network call: the DB-hitting functions (get_tax_rule_by_category,
get_category_used_amount) are monkeypatched out wherever a test needs them.
"""
import os

os.environ.setdefault("SUPABASE_URL", "https://example.invalid.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-placeholder-key")
os.environ.setdefault("GEMINI_API_KEY", "test-placeholder-key")
