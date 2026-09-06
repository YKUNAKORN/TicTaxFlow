"""Seed ONE demo user for the recorded pitch, from a clean state.

Run from backend/, with the venv active and .env pointed at the target
Supabase project:

    python scripts/seed_demo.py

What it does (see DEMO.md for the full shot-by-shot recording script):
  1. Makes sure the Chroma RAG store is populated. It is gitignored
     (backend/.gitignore) so a fresh clone starts with zero vectors --
     without this, Tax Expert classification silently returns category
     "None" for every receipt (RAG context comes back empty) and the
     whole demo stalls at shot 2.
  2. Creates (or resets) one demo user via the Supabase admin API.
  3. Seeds two VERIFIED transactions directly into `transactions` for
     that user:
       - Life Insurance: 90,000 THB used, 10,000 THB headroom left out of
         the category's 100,000 THB cap (from `tax_rules`, not hardcoded).
         Uploading the bundled `life_insurance_topup_receipt.png` sample
         (15,000 THB) live during recording pushes it over the cap and
         fires the validation warning -- shot 3.
       - SSF: 120,000 THB used out of its cap, so the Optimisation
         Advisor has real headroom to suggest topping up -- shot 6.
     Health Insurance is deliberately left untouched so shots 1-2 show a
     completely fresh upload -> extract -> classify with headroom to spare.
  4. Does NOT touch income data: the mock Shopee/Lazada/TikTok Shop
     fixtures under backend/data/fixtures/ are seller_id-agnostic (see
     app/services/income_aggregator.py), so /income/sync already returns
     a merged, deduplicated total for any authenticated user with no
     per-user wiring needed.

Safe to re-run: it deletes and recreates the demo user's own rows only,
never touches any other user's data.
"""
import logging
import sys
from pathlib import Path

# Allow running as `python scripts/seed_demo.py` from backend/ (not just
# `python -m scripts.seed_demo`) by putting backend/ on sys.path so `app.*`
# resolves the same way it does for uvicorn and pytest.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("seed_demo")

from app.database.database import supabase, get_auth_client  # noqa: E402
from app.agents import accountant  # noqa: E402
from app.services import retrieval  # noqa: E402
from app.services import document_indexer  # noqa: E402

DEMO_EMAIL = "demo@tictaxflow.app"
DEMO_PASSWORD = "DemoPitch2026!"
DEMO_FULL_NAME = "Demo Seller"

# (category_name, amount already used, transaction_date) -- amounts and
# caps are read from the live `tax_rules` table below, never hardcoded.
SEED_TRANSACTIONS = [
    {
        "category_name": "Life Insurance",
        "merchant_name": "Muang Thai Life Insurance PCL",
        "merchant_tax_id": "0107537000001",
        "transaction_date": "2026-03-10",
        "total_amount": 90000.0,
        "ai_reasoning": "Seed data: prior verified Life Insurance premium, leaves 10,000 THB headroom for the live demo upload to push over the 100,000 THB cap.",
    },
    {
        "category_name": "SSF",
        "merchant_name": "SCB Super Savings Fund",
        "merchant_tax_id": "0107536000002",
        "transaction_date": "2026-02-15",
        "total_amount": 120000.0,
        "ai_reasoning": "Seed data: prior verified SSF contribution, leaves headroom for the Optimisation Advisor to suggest a top-up.",
    },
]


def ensure_rag_index() -> None:
    collection = retrieval.get_collection()
    if collection.count() > 0:
        logger.info("RAG store already populated (%d chunks)", collection.count())
        return

    logger.warning("RAG store is empty -- indexing backend/data/documents now")
    documents = document_indexer.load_pdf_documents()
    if not documents:
        logger.error("No source PDFs found in backend/data/documents; Tax Expert classification will fail")
        return
    document_indexer.index_documents(documents)


def reset_demo_user() -> str:
    """Delete any existing demo user (auth + rows) and recreate it fresh.
    Returns the new user's id."""
    auth_client = get_auth_client()

    existing = [u for u in supabase.auth.admin.list_users() if u.email == DEMO_EMAIL]
    for u in existing:
        logger.info("Removing existing demo user %s (%s)", DEMO_EMAIL, u.id)
        supabase.table("transactions").delete().eq("user_id", u.id).execute()
        supabase.table("income_summary").delete().eq("user_id", u.id).execute()
        supabase.auth.admin.delete_user(u.id)

    created = supabase.auth.admin.create_user({
        "email": DEMO_EMAIL,
        "password": DEMO_PASSWORD,
        "email_confirm": True,
        "user_metadata": {"full_name": DEMO_FULL_NAME},
    })
    user_id = created.user.id
    logger.info("Created demo user %s (%s)", DEMO_EMAIL, user_id)

    try:
        # Mirror into public.users for the app's `username` read. Credentials
        # live only in Supabase Auth; the vestigial `password` column is not
        # written (same as endpoints/auth.py register).
        supabase.table("users").insert({
            "id": user_id,
            "username": DEMO_FULL_NAME,
            "email": DEMO_EMAIL,
        }).execute()
    except Exception:
        logger.warning("Could not mirror demo user into public.users (non-fatal)")

    return user_id


def seed_transactions(user_id: str) -> None:
    for spec in SEED_TRANSACTIONS:
        rule = accountant.get_tax_rule_by_category(spec["category_name"])
        if not rule:
            logger.error("No active tax rule found for category '%s' -- skipping", spec["category_name"])
            continue

        already_used = accountant.get_used_deductible_amount(user_id, rule["id"])
        calc = accountant.calculate_deductible_amount(
            spec["total_amount"], spec["category_name"], already_used=already_used,
        )

        row = {
            "user_id": user_id,
            "rule_id": rule["id"],
            "receipt_image_url": None,
            "merchant_name": spec["merchant_name"],
            "merchant_tax_id": spec["merchant_tax_id"],
            "transaction_date": spec["transaction_date"],
            "total_amount": spec["total_amount"],
            "deductible_amount": calc["amount"],
            "status": "verified",
            "ai_reasoning": spec["ai_reasoning"],
        }
        supabase.table("transactions").insert(row).execute()
        logger.info(
            "Seeded %s: %.2f THB total, %.2f THB deductible (cap %.2f THB)",
            spec["category_name"], spec["total_amount"], calc["amount"], rule["max_limit"],
        )


def main() -> int:
    ensure_rag_index()
    user_id = reset_demo_user()
    seed_transactions(user_id)

    logger.info("Demo user ready.")
    logger.info("  email:    %s", DEMO_EMAIL)
    logger.info("  password: %s", DEMO_PASSWORD)
    logger.info("Sample receipts to upload live during recording: backend/data/fixtures/sample_receipts/")
    logger.info("See DEMO.md for the full shot list.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
