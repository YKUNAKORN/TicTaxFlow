"""Income sync endpoint. Aggregates SEEDED multi-platform sample data via
mock provider adapters (see app/services/income_aggregator.py) -- not a
live Shopee/Lazada/TikTok Shop integration.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user_id
from app.database.database import supabase
from app.services.income_aggregator import aggregate_income

logger = logging.getLogger(__name__)

router = APIRouter()


class IncomeSyncRequest(BaseModel):
    period: str


@router.post("/sync", summary="Sync multi-platform income for the current user")
async def sync_income(
    request: IncomeSyncRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Aggregate Shopee/Lazada/TikTok Shop sample sales for `user_id` and
    persist a deduplicated per-platform + grand total summary."""
    result = aggregate_income(seller_id=user_id, period=request.period)

    summary_row = {
        "user_id": user_id,
        "period": request.period,
        "platform_totals": result["platform_totals"],
        "total_gross": result["grand_total"]["gross_amount"],
        "total_fee": result["grand_total"]["fee"],
        "total_net": result["grand_total"]["net_amount"],
        "record_count": result["grand_total"]["record_count"],
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
        "period": request.period,
        "platform_totals": result["platform_totals"],
        "grand_total": result["grand_total"],
    }
