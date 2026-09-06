"""Multi-platform income aggregation.

DEMO / TESTING NOTE: `MockShopeeProvider`, `MockLazadaProvider`, and
`MockTikTokShopProvider` read seeded sample data from
`backend/data/fixtures/*_sales.json`. They are stand-ins behind a real
`SalesProvider` adapter interface, not live Shopee/Lazada/TikTok Shop
integrations. Swapping in a real OAuth-backed provider later means adding a
new class that implements `SalesProvider` -- callers of `aggregate_income`
do not change.
"""
import json
import logging
from datetime import date
from pathlib import Path
from typing import Optional, Protocol

from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)

FIXTURES_DIR = settings.DATA_DIR / "fixtures"


class SaleRecord(BaseModel):
    """One normalised sale, regardless of source marketplace."""
    order_id: str
    platform: str
    date: str
    gross_amount: float
    fee: float
    net_amount: float


class SalesProvider(Protocol):
    """Adapter interface a marketplace sales source must implement."""

    def fetch_sales(
        self, seller_id: str, period: str, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> list[SaleRecord]:
        ...


def _load_fixture(
    path: Path,
    platform: str,
    period: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[SaleRecord]:
    """Load a platform's fixture file, filtered to `period` (a 4-digit CE
    year prefix, e.g. "2026", matched against each row's ISO date). The
    seeded rows are regenerated per tax year by
    scripts/generate_sample_fixtures.py.

    When `date_from`/`date_to` are given (inclusive ISO YYYY-MM-DD), rows
    are further filtered to that range -- used for half-year (ภ.ง.ด.94)
    syncs. When both are None, behaviour is unchanged from before this
    parameter existed.
    """
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)

    matched = [
        SaleRecord(platform=platform, **row)
        for row in rows
        if row["date"].startswith(period)
    ]

    if date_from is None and date_to is None:
        return matched

    lo = date.fromisoformat(date_from) if date_from else None
    hi = date.fromisoformat(date_to) if date_to else None

    def _in_range(record: SaleRecord) -> bool:
        record_date = date.fromisoformat(record.date)
        if lo is not None and record_date < lo:
            return False
        if hi is not None and record_date > hi:
            return False
        return True

    return [r for r in matched if _in_range(r)]


class MockShopeeProvider:
    """Reads seeded Shopee-shaped sample data. NOT a live Shopee integration."""

    PLATFORM = "Shopee"

    def fetch_sales(
        self, seller_id: str, period: str, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> list[SaleRecord]:
        # seller_id is unused: the fixture is shared demo data, not scoped
        # to individual sellers.
        return _load_fixture(FIXTURES_DIR / "shopee_sales.json", self.PLATFORM, period, date_from, date_to)


class MockLazadaProvider:
    """Reads seeded Lazada-shaped sample data. NOT a live Lazada integration."""

    PLATFORM = "Lazada"

    def fetch_sales(
        self, seller_id: str, period: str, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> list[SaleRecord]:
        return _load_fixture(FIXTURES_DIR / "lazada_sales.json", self.PLATFORM, period, date_from, date_to)


class MockTikTokShopProvider:
    """Reads seeded TikTok Shop-shaped sample data. NOT a live TikTok Shop integration."""

    PLATFORM = "TikTokShop"

    def fetch_sales(
        self, seller_id: str, period: str, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> list[SaleRecord]:
        return _load_fixture(FIXTURES_DIR / "tiktok_sales.json", self.PLATFORM, period, date_from, date_to)


def aggregate_income(
    seller_id: str,
    period: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """Fetch sales from every mock provider, dedupe, and total per platform.

    `date_from`/`date_to` (inclusive ISO YYYY-MM-DD) narrow the year-scoped
    `period` down to a sub-range -- e.g. Jan-Jun for a ภ.ง.ด.94 half-year
    sync. When both are None, behaviour is unchanged from before this
    parameter existed (full `period` year, as used by POST /income/sync).

    Dedup key is (platform, order_id): a marketplace occasionally re-sends
    the same order (pagination overlap), but two different marketplaces can
    mint the same order_id independently, and those must NOT be collapsed
    into one sale.
    """
    providers: list[SalesProvider] = [
        MockShopeeProvider(),
        MockLazadaProvider(),
        MockTikTokShopProvider(),
    ]

    all_records: list[SaleRecord] = []
    for provider in providers:
        all_records.extend(provider.fetch_sales(seller_id, period, date_from, date_to))

    seen: set[tuple[str, str]] = set()
    deduped: list[SaleRecord] = []
    for record in all_records:
        key = (record.platform, record.order_id)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)

    platform_totals: dict[str, dict] = {}
    for record in deduped:
        totals = platform_totals.setdefault(record.platform, {
            "gross_amount": 0.0,
            "fee": 0.0,
            "net_amount": 0.0,
            "record_count": 0,
        })
        totals["gross_amount"] += record.gross_amount
        totals["fee"] += record.fee
        totals["net_amount"] += record.net_amount
        totals["record_count"] += 1

    for totals in platform_totals.values():
        totals["gross_amount"] = round(totals["gross_amount"], 2)
        totals["fee"] = round(totals["fee"], 2)
        totals["net_amount"] = round(totals["net_amount"], 2)

    grand_total = {
        "gross_amount": round(sum(t["gross_amount"] for t in platform_totals.values()), 2),
        "fee": round(sum(t["fee"] for t in platform_totals.values()), 2),
        "net_amount": round(sum(t["net_amount"] for t in platform_totals.values()), 2),
        "record_count": len(deduped),
    }

    logger.info(
        "aggregate_income: period=%s platforms=%s records=%d",
        period, list(platform_totals.keys()), len(deduped),
    )

    return {
        "seller_id": seller_id,
        "period": period,
        "platform_totals": platform_totals,
        "grand_total": grand_total,
        "records": deduped,
    }


def resolve_data_year(current_year: int, *, max_lookback: int = 5) -> int:
    """Newest year at or before `current_year` (within `max_lookback`
    years) that the seeded fixtures actually have rows for; falls back to
    `current_year` when none in range does.

    The fixtures are dated one tax year at a time
    (scripts/generate_sample_fixtures.py) while
    settings.DEFAULT_TAX_YEAR tracks the current calendar year, so those
    agree only in the year the fixtures were last generated for. Callers
    (the filing-pack default, POST /income/sync) use this so a new calendar
    year does not silently zero out every downstream figure before the
    fixtures are regenerated. An explicit caller-supplied year always wins
    over this.
    """
    for year in range(current_year, current_year - max_lookback, -1):
        # seller_id is unused by the mock providers (shared demo fixtures).
        if aggregate_income("", str(year))["grand_total"]["record_count"] > 0:
            return year
    return current_year
