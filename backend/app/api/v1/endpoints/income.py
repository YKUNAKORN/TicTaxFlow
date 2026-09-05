"""Income sync endpoint. Aggregates SEEDED multi-platform sample data via
mock provider adapters (see app/services/income_aggregator.py) -- not a
live Shopee/Lazada/TikTok Shop integration.
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user_id
from app.database.database import supabase
from app.services.income_aggregator import aggregate_income
from app.services.workflow import run_income_workflow

logger = logging.getLogger(__name__)

router = APIRouter()


class IncomeSyncRequest(BaseModel):
    period: Optional[str] = None


def _resolve_period(seller_id: str, requested_period: Optional[str]) -> str:
    """Pick the period to sync. When the caller doesn't pin one, prefer the
    current calendar year and fall back to the prior year -- the seeded
    demo fixtures are dated for a fixed year, so this keeps the dashboard
    showing real data after that year turns over instead of an empty sync.
    """
    if requested_period:
        return requested_period

    current_year = str(datetime.now().year)
    current_records = aggregate_income(seller_id, current_year)["grand_total"]["record_count"]
    if current_records > 0:
        return current_year

    return str(datetime.now().year - 1)


@router.post("/sync", summary="Sync multi-platform income for the current user")
async def sync_income(
    request: IncomeSyncRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Aggregate Shopee/Lazada/TikTok Shop sample sales for `user_id`,
    persist a deduplicated per-platform + grand total summary, and return
    the resulting PIT estimate + deduction-optimisation suggestions.

    Runs through the compiled LangGraph workflow (income -> estimate_tax
    -> advisor) rather than calling those services by hand, per
    CLAUDE.md's orchestration rule.
    """
    period = _resolve_period(user_id, request.period)
    state = run_income_workflow(user_id, period)

    income_result = state["income_data"]
    tax_estimate = state.get("tax_estimate", {})
    deduction_suggestions = state.get("deduction_suggestions", [])

    summary_row = {
        "user_id": user_id,
        "period": period,
        "platform_totals": income_result["platform_totals"],
        "total_gross": income_result["grand_total"]["gross_amount"],
        "total_fee": income_result["grand_total"]["fee"],
        "total_net": income_result["grand_total"]["net_amount"],
        "record_count": income_result["grand_total"]["record_count"],
    }

    try:
        supabase.table("income_summary").upsert(
            summary_row, on_conflict="user_id,period"
        ).execute()
    except Exception:
        logger.exception("Failed to persist income summary")
        raise HTTPException(status_code=500, detail="Failed to persist income summary")

    return {
        "success": True,
        "period": period,
        "platform_totals": income_result["platform_totals"],
        "grand_total": income_result["grand_total"],
        "tax_estimate": tax_estimate,
        "deduction_suggestions": deduction_suggestions,
    }
