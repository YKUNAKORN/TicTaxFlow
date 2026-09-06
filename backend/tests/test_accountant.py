"""Cumulative deduction cap (roadmap Phase 1.3 / CLAUDE.md: caps are
cumulative per user + category + tax_year, never per single receipt).
"""
from types import SimpleNamespace
from unittest.mock import patch

from app.agents import accountant

FAKE_LIFE_INSURANCE_RULE = {
    "id": "rule-life-insurance",
    "category_name": "Life Insurance",
    "max_limit": 100000.0,
}


def test_calculate_deductible_amount_caps_at_remaining_limit_when_already_used():
    """Two 80,000 THB receipts in the same 100,000 THB category: the second
    must be capped at the 20,000 THB remaining headroom, not stored as a
    fresh 80,000 THB (which would make the cumulative total 160,000)."""
    with patch.object(accountant, "get_tax_rule_by_category", return_value=FAKE_LIFE_INSURANCE_RULE):
        result = accountant.calculate_deductible_amount(
            total_amount=80000.0,
            category_name="Life Insurance",
            already_used=80000.0,
        )

    assert result["amount"] == 20000.0
    assert result["is_capped"] is True
    assert result["max_limit"] == 100000.0


def test_calculate_deductible_amount_under_limit_is_not_capped():
    with patch.object(accountant, "get_tax_rule_by_category", return_value=FAKE_LIFE_INSURANCE_RULE):
        result = accountant.calculate_deductible_amount(
            total_amount=30000.0,
            category_name="Life Insurance",
            already_used=40000.0,
        )

    assert result["amount"] == 30000.0
    assert result["is_capped"] is False


def test_calculate_deductible_amount_returns_zero_once_category_is_full():
    with patch.object(accountant, "get_tax_rule_by_category", return_value=FAKE_LIFE_INSURANCE_RULE):
        result = accountant.calculate_deductible_amount(
            total_amount=10000.0,
            category_name="Life Insurance",
            already_used=100000.0,
        )

    assert result["amount"] == 0.0
    assert result["is_capped"] is True


# --- Edit path: the cumulative cap must apply on update, not only on upload ---


class _FakeTable:
    """Minimal Supabase query-builder stand-in over an in-memory store."""

    def __init__(self, name, store, recorder):
        self._name = name
        self._store = store
        self._recorder = recorder
        self._mode = "select"
        self._payload = None
        self._eq = []
        self._neq = []

    def select(self, *_args, **_kwargs):
        self._mode = "select"
        return self

    def update(self, payload):
        self._mode = "update"
        self._payload = payload
        return self

    def eq(self, col, val):
        self._eq.append((col, val))
        return self

    def neq(self, col, val):
        self._neq.append((col, val))
        self._recorder.append(("neq", self._name, col, val))
        return self

    def execute(self):
        rows = [dict(r) for r in self._store.get(self._name, [])]
        for col, val in self._eq:
            rows = [r for r in rows if r.get(col) == val]
        for col, val in self._neq:
            rows = [r for r in rows if r.get(col) != val]
        if self._mode == "update":
            rows = [{**r, **self._payload} for r in rows]
        return SimpleNamespace(data=rows)


class _FakeSupabase:
    def __init__(self, store):
        self.store = store
        self.neq_calls = []

    def table(self, name):
        return _FakeTable(name, self.store, self.neq_calls)


def test_get_used_deductible_amount_excludes_named_transaction():
    store = {
        "transactions": [
            {"id": "a", "user_id": "u1", "rule_id": "r1", "status": "verified", "deductible_amount": 30000.0},
            {"id": "b", "user_id": "u1", "rule_id": "r1", "status": "verified", "deductible_amount": 25000.0},
        ]
    }
    fake = _FakeSupabase(store)

    with patch.object(accountant, "supabase", fake):
        total = accountant.get_used_deductible_amount("u1", "r1", exclude_transaction_id="a")

    assert total == 25000.0
    assert ("neq", "transactions", "id", "a") in fake.neq_calls


def test_update_transaction_applies_cumulative_cap_excluding_edited_row():
    """Editing a transaction's total_amount must cap the recalculated
    deductible against the category's remaining headroom, and must exclude
    the edited row itself from the already-used sum (Phase 1.3 on the edit
    path). Without the fix, already_used defaults to 0 and the edit would be
    stored at its full 50,000; counting its own old 80,000 row would instead
    force it to 0."""
    store = {
        "transactions": [
            {"id": "txn-edit", "user_id": "u1", "rule_id": "rule-life-insurance",
             "status": "verified", "deductible_amount": 80000.0, "total_amount": 80000.0},
            {"id": "txn-other", "user_id": "u1", "rule_id": "rule-life-insurance",
             "status": "verified", "deductible_amount": 60000.0, "total_amount": 60000.0},
        ],
        "tax_rules": [
            {"id": "rule-life-insurance", "category_name": "Life Insurance", "max_limit": 100000.0},
        ],
    }
    fake = _FakeSupabase(store)

    with patch.object(accountant, "supabase", fake), \
         patch.object(accountant, "get_tax_rule_by_category", return_value=FAKE_LIFE_INSURANCE_RULE):
        result = accountant.update_transaction("txn-edit", {"total_amount": 50000.0})

    assert result["success"] is True
    # already_used = 60,000 (txn-other only) -> remaining headroom = 40,000,
    # so the 50,000 edit is capped at 40,000.
    assert result["transaction"]["deductible_amount"] == 40000.0
    assert ("neq", "transactions", "id", "txn-edit") in fake.neq_calls


def test_update_transaction_recaps_deductible_when_row_is_verified():
    """Promoting a needs_review row to verified must re-cap its deductible
    against the category's remaining headroom. get_used_deductible_amount
    only sums verified rows, so several pending rows can each hold a
    deductible computed against a smaller verified-only total -- verifying
    them without this re-check would blow the cumulative cap."""
    store = {
        "transactions": [
            {"id": "txn-pending", "user_id": "u1", "rule_id": "rule-life-insurance",
             "status": "needs_review", "deductible_amount": 90000.0, "total_amount": 90000.0},
            {"id": "txn-verified", "user_id": "u1", "rule_id": "rule-life-insurance",
             "status": "verified", "deductible_amount": 60000.0, "total_amount": 60000.0},
        ],
        "tax_rules": [
            {"id": "rule-life-insurance", "category_name": "Life Insurance", "max_limit": 100000.0},
        ],
    }
    fake = _FakeSupabase(store)

    with patch.object(accountant, "supabase", fake), \
         patch.object(accountant, "get_tax_rule_by_category", return_value=FAKE_LIFE_INSURANCE_RULE):
        result = accountant.update_transaction("txn-pending", {"status": "verified"})

    assert result["success"] is True
    # already_used = 60,000 (txn-verified) -> remaining headroom = 40,000, so
    # the 90,000 row is capped down to 40,000 as it becomes verified.
    assert result["transaction"]["deductible_amount"] == 40000.0
    assert result["transaction"]["status"] == "verified"


def test_update_transaction_status_change_without_rule_is_a_plain_update():
    """A status change on a row with no rule_id (not deductible / no
    matching category) must not blow up trying to recompute a deductible."""
    store = {
        "transactions": [
            {"id": "txn-nr", "user_id": "u1", "rule_id": None,
             "status": "needs_review", "deductible_amount": 0.0, "total_amount": 1000.0},
        ],
        "tax_rules": [],
    }
    fake = _FakeSupabase(store)

    with patch.object(accountant, "supabase", fake):
        result = accountant.update_transaction("txn-nr", {"status": "verified"})

    assert result["success"] is True
    assert result["transaction"]["deductible_amount"] == 0.0
