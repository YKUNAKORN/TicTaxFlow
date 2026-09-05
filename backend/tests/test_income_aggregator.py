"""aggregate_income: merges 3 mock providers, dedupes overlapping
order_ids, and totals correctly. Uses the seeded fixtures under
backend/data/fixtures/ -- no network calls.
"""
from app.services.income_aggregator import (
    aggregate_income,
    MockShopeeProvider,
    MockLazadaProvider,
    MockTikTokShopProvider,
)

SELLER_ID = "seller-1"
PERIOD = "2025"


def _raw_record_count(period: str) -> int:
    providers = [MockShopeeProvider(), MockLazadaProvider(), MockTikTokShopProvider()]
    return sum(len(p.fetch_sales(SELLER_ID, period)) for p in providers)


def test_aggregate_income_merges_all_three_providers():
    result = aggregate_income(SELLER_ID, PERIOD)

    assert set(result["platform_totals"].keys()) == {"Shopee", "Lazada", "TikTokShop"}
    for totals in result["platform_totals"].values():
        assert totals["record_count"] > 0


def test_aggregate_income_dedupes_same_platform_duplicate_order_id():
    """shopee_sales.json seeds one exact duplicate row (SHP-2025-1004,
    simulating a provider re-sending the same order on pagination overlap).
    It must be collapsed to a single record."""
    result = aggregate_income(SELLER_ID, PERIOD)

    raw_count = _raw_record_count(PERIOD)
    assert raw_count - result["grand_total"]["record_count"] == 1

    shopee_order_ids = [
        r.order_id for r in result["records"] if r.platform == "Shopee"
    ]
    assert shopee_order_ids.count("SHP-2025-1004") == 1


def test_aggregate_income_keeps_cross_platform_coincidental_order_id_distinct():
    """Lazada and TikTok Shop each seed a row with order_id "2025-000777" --
    two different marketplaces coincidentally minting the same id. Dedup key
    is (platform, order_id), so both real sales must survive."""
    result = aggregate_income(SELLER_ID, PERIOD)

    matches = [r for r in result["records"] if r.order_id == "2025-000777"]
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
