"""aggregate_income: merges 3 mock providers, dedupes overlapping
order_ids, and totals correctly. Uses the seeded fixtures under
backend/data/fixtures/ -- no network calls.
"""
from app.core.config import settings
from app.services.income_aggregator import (
    aggregate_income,
    resolve_data_year,
    MockShopeeProvider,
    MockLazadaProvider,
    MockTikTokShopProvider,
)

SELLER_ID = "seller-1"
PERIOD = "2026"


def _raw_record_count(period: str) -> int:
    providers = [MockShopeeProvider(), MockLazadaProvider(), MockTikTokShopProvider()]
    return sum(len(p.fetch_sales(SELLER_ID, period)) for p in providers)


def test_aggregate_income_merges_all_three_providers():
    result = aggregate_income(SELLER_ID, PERIOD)

    assert set(result["platform_totals"].keys()) == {"Shopee", "Lazada", "TikTokShop"}
    for totals in result["platform_totals"].values():
        assert totals["record_count"] > 0


def test_aggregate_income_dedupes_same_platform_duplicate_order_id():
    """shopee_sales.json seeds one exact duplicate row (SHP-2026-1004,
    simulating a provider re-sending the same order on pagination overlap).
    It must be collapsed to a single record."""
    result = aggregate_income(SELLER_ID, PERIOD)

    raw_count = _raw_record_count(PERIOD)
    assert raw_count - result["grand_total"]["record_count"] == 1

    shopee_order_ids = [
        r.order_id for r in result["records"] if r.platform == "Shopee"
    ]
    assert shopee_order_ids.count(f"SHP-{PERIOD}-1004") == 1


def test_aggregate_income_keeps_cross_platform_coincidental_order_id_distinct():
    """Lazada and TikTok Shop each seed a row with order_id "2026-000777" --
    two different marketplaces coincidentally minting the same id. Dedup key
    is (platform, order_id), so both real sales must survive."""
    result = aggregate_income(SELLER_ID, PERIOD)

    matches = [r for r in result["records"] if r.order_id == f"{PERIOD}-000777"]
    assert len(matches) == 2
    assert {r.platform for r in matches} == {"Lazada", "TikTokShop"}


def test_aggregate_income_totals_are_internally_consistent():
    """Every seeded row satisfies gross_amount == fee + net_amount, so the
    aggregated totals must too -- an invariant check independent of any
    hardcoded grand-total figure."""
    result = aggregate_income(SELLER_ID, PERIOD)
    grand_total = result["grand_total"]

    assert grand_total["gross_amount"] == round(
        grand_total["fee"] + grand_total["net_amount"], 2
    )

    expected_gross = round(
        sum(t["gross_amount"] for t in result["platform_totals"].values()), 2
    )
    assert grand_total["gross_amount"] == expected_gross
    assert grand_total["record_count"] == sum(
        t["record_count"] for t in result["platform_totals"].values()
    )


def test_aggregate_income_filters_by_period():
    result = aggregate_income(SELLER_ID, "2099")

    assert result["platform_totals"] == {}
    assert result["grand_total"]["record_count"] == 0


# --- resolve_data_year: keeps the filing pack / income sync off empty years ---


def test_resolve_data_year_returns_that_year_when_fixtures_cover_it():
    # The committed fixtures are dated for PERIOD, so asking for PERIOD is a
    # no-op.
    assert aggregate_income(SELLER_ID, str(PERIOD))["grand_total"]["record_count"] > 0
    assert resolve_data_year(int(PERIOD)) == int(PERIOD)

    # From the app's current tax year it always lands on a year that has
    # data (PERIOD itself while the fixtures are current; the walk-back
    # otherwise -- see the next test).
    resolved = resolve_data_year(settings.DEFAULT_TAX_YEAR)
    assert aggregate_income("", str(resolved))["grand_total"]["record_count"] > 0


def test_resolve_data_year_walks_back_to_the_most_recent_year_with_data():
    # A later calendar year (before the fixtures are regenerated) must not
    # resolve to an empty year -- it walks back to the seeded one.
    assert resolve_data_year(int(PERIOD) + 2) == int(PERIOD)


def test_resolve_data_year_falls_back_to_input_when_nothing_in_range():
    assert resolve_data_year(2099, max_lookback=3) == 2099
