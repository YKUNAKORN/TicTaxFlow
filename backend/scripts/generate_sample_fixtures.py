"""Deterministic generator for the seeded multi-platform sales fixtures.

Writes backend/data/fixtures/{shopee,lazada,tiktok}_sales.json -- the sample
data behind `Mock*Provider` in app/services/income_aggregator.py. NOT a live
marketplace integration; see that module's docstring and CLAUDE.md's
integrity rule.

Run once (or whenever the demo numbers need to change), from backend/:

    python scripts/generate_sample_fixtures.py

Design goals baked into the numbers below:
  * DATED FOR THE CURRENT TAX YEAR. `settings.DEFAULT_TAX_YEAR` is
    datetime.now().year (CE). The income-sync path and the filing pack both
    query fixtures for that year, so the rows must carry it or every figure
    downstream collapses to 0. Re-run this each Jan (or set TAX_YEAR).
  * Rows span Jan-Dec so ภ.ง.ด.94's Jan-Jun half-year scoping is actually
    exercised (roughly 55-65% of each platform's orders land in H1).
  * Grand total GROSS ~= 2,500,000 THB/year. After the Section 40(8) flat
    60% expense deduction that is ~1,000,000 THB taxable -> a non-trivial
    PIT figure and a 20% marginal rate for the optimisation advisor to work
    against. (A smaller total falls under the 150k 0%-bracket ceiling once
    the 60% deduction is applied, which is what made the old ~200k fixtures
    show 0 tax / 0 suggestions.)
  * Per-platform commission rates differ (Shopee 7%, Lazada 6%, TikTok 8%)
    so `fee` / `net_amount` are not all the same ratio.
  * Two deliberate dedup cases, asserted in tests/test_income_aggregator.py:
      - Shopee re-sends SHP-<year>-1004 (exact duplicate row, pagination
        overlap) -> must collapse to one record.
      - Lazada and TikTok Shop each mint order_id "<year>-000777"
        independently -> dedup key is (platform, order_id), so BOTH survive.
"""
import json
import logging
import sys
from pathlib import Path

# Allow `python scripts/generate_sample_fixtures.py` from backend/ (like
# scripts/seed_demo.py) by putting backend/ on sys.path so `app.*` resolves.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("generate_sample_fixtures")

# CE calendar year the rows are dated for. Defaults to the same value the app
# uses everywhere else (settings.DEFAULT_TAX_YEAR = datetime.now().year).
TAX_YEAR = settings.DEFAULT_TAX_YEAR

OUT_DIR = settings.DATA_DIR / "fixtures"

# Cross-platform coincidental order id (see module docstring).
COINCIDENTAL_ORDER_ID = f"{TAX_YEAR}-000777"

# (order_id_suffix, "MM-DD", gross_amount). order_id becomes
# "<PREFIX>-<TAX_YEAR>-<suffix>" unless the suffix is already a full id.
SHOPEE_ROWS = [
    ("1001", "01-14", 42000),
    ("1002", "01-27", 31000),
    ("1003", "02-09", 73000),
    ("1004", "02-23", 74000),   # re-sent below as an exact duplicate row
    ("1005", "03-06", 39000),
    ("1006", "03-20", 82000),
    ("1007", "04-03", 47000),
    ("1008", "04-19", 100000),
    ("1009", "05-07", 110000),
    ("1010", "06-13", 52000),
    ("1011", "07-21", 61000),
    ("1012", "08-29", 44000),
    ("1013", "10-12", 95000),
    ("1014", "11-24", 85000),
    ("1015", "12-19", 65000),
]

LAZADA_ROWS = [
    ("2001", "01-09", 38000),
    ("2002", "01-30", 54000),
    ("2003", "02-14", 26000),
    ("2004", "03-02", 130000),
    ("2005", "03-27", 17000),
    ("2006", "04-11", 81000),
    ("2007", "05-05", 36000),
    ("2008", "06-01", 90000),
    ("2009", "06-28", 49000),
    ("2010", "07-15", 58000),
    ("2011", "08-09", 110000),
    ("2012", "09-14", 44000),
    ("2013", "10-22", 42000),
    (COINCIDENTAL_ORDER_ID, "11-06", 36000),
    ("2014", "12-18", 39000),
]

TIKTOK_ROWS = [
    ("3001", "01-20", 28000),
    ("3002", "02-05", 44000),
    ("3003", "02-27", 15000),
    ("3004", "03-15", 90000),
    ("3005", "04-08", 22000),
    ("3006", "04-29", 73000),
    ("3007", "05-19", 31000),
    ("3008", "06-10", 85000),
    ("3009", "07-02", 25000),
    ("3010", "07-26", 40000),
    ("3011", "08-17", 66000),
    ("3012", "09-09", 18000),
    (COINCIDENTAL_ORDER_ID, "11-06", 41000),
    ("3013", "11-30", 42000),
    ("3014", "12-27", 30000),
]

PLATFORMS = [
    ("shopee", "SHP", 0.07, SHOPEE_ROWS),
    ("lazada", "LAZ", 0.06, LAZADA_ROWS),
    ("tiktok", "TT", 0.08, TIKTOK_ROWS),
]


def _row(order_id: str, prefix: str, mm_dd: str, gross: float, fee_rate: float) -> dict:
    # A suffix like "1004" gets the "<PREFIX>-<YEAR>-" prefix; an already
    # fully-formed id (the coincidental "<YEAR>-000777", which contains "-")
    # is used verbatim.
    full_id = order_id if "-" in order_id else f"{prefix}-{TAX_YEAR}-{order_id}"
    fee = round(gross * fee_rate, 2)
    return {
        "order_id": full_id,
        "date": f"{TAX_YEAR}-{mm_dd}",
        "gross_amount": round(float(gross), 2),
        "fee": fee,
        "net_amount": round(gross - fee, 2),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    grand_gross = 0.0
    grand_rows = 0

    for filename, prefix, fee_rate, rows in PLATFORMS:
        out_rows = [_row(oid, prefix, mm_dd, gross, fee_rate) for oid, mm_dd, gross in rows]

        # Shopee re-sends order 1004 once (pagination overlap). Insert the
        # exact same row again right after the original.
        if prefix == "SHP":
            dup = next(r for r in out_rows if r["order_id"] == f"SHP-{TAX_YEAR}-1004")
            out_rows.insert(out_rows.index(dup) + 1, dict(dup))

        path = OUT_DIR / f"{filename}_sales.json"
        path.write_text(json.dumps(out_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        unique_rows = {r["order_id"]: r for r in out_rows}.values()
        platform_gross = sum(r["gross_amount"] for r in unique_rows)
        grand_gross += platform_gross
        grand_rows += len(out_rows)
        logger.info(
            "%-18s %2d rows (%2d unique)  gross %s THB",
            path.name, len(out_rows), len(unique_rows), f"{platform_gross:,.2f}",
        )

    logger.info("-" * 60)
    logger.info("TAX_YEAR=%s  raw rows=%d  grand unique gross ~= %s THB", TAX_YEAR, grand_rows, f"{grand_gross:,.2f}")


if __name__ == "__main__":
    main()
