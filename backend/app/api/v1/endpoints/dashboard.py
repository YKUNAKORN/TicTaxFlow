"""Dashboard Summary API endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.database.database import supabase
from app.core.security import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary", summary="Get dashboard summary for the current user")
async def get_dashboard_summary(user_id: str = Depends(get_current_user_id)):
    """
    Get comprehensive dashboard summary for a user
    
    Returns:
    - Total deductible amount (verified transactions only)
    - Total transactions count
    - Status breakdown (verified, needs_review, rejected)
    - Recent transactions (last 5)
    - Category breakdown (deductible by category)
    """
    
    try:
        # Get all transactions for the user, ordered by creation time
        all_transactions = supabase.table("transactions").select(
            "id, merchant_name, transaction_date, total_amount, deductible_amount, status, create_at, receipt_image_url, rule_id, user_id, ai_reasoning"
        ).eq("user_id", user_id).order("create_at", desc=True).execute()

        transactions_data = all_transactions.data if all_transactions.data else []

        logger.debug("Dashboard summary: %d transactions found", len(transactions_data))

        # Get all tax rules to map categories
        try:
            tax_rules_response = supabase.table("tax_rules").select(
                "id, category_name, max_limit"
            ).eq("is_active", True).execute()

            tax_rules_map = {rule["id"]: rule for rule in (tax_rules_response.data or [])}
        except Exception as e:
            logger.warning("Failed to fetch tax rules: %s", e)
            tax_rules_map = {}
        
        # Calculate total deductible (verified only)
        total_deductible = sum(
            float(t.get("deductible_amount", 0) or 0)
            for t in transactions_data 
            if t.get("status") == "verified"
        )
        
        # Count by status
        status_counts = {"verified": 0, "needs_review": 0, "rejected": 0, "not_deductible": 0}
        for t in transactions_data:
            status = t.get("status", "needs_review")
            if status in status_counts:
                status_counts[status] += 1
        
        # Get recent transactions (last 5) with category names
        recent_transactions = []
        for tx in transactions_data[:5]:
            rule_id = tx.get("rule_id")
            status = tx.get("status", "needs_review")
            category_name = "Unknown"
            if rule_id and rule_id in tax_rules_map:
                category_name = tax_rules_map[rule_id]["category_name"]
            elif status == "not_deductible":
                category_name = "Not Deductible"
            
            recent_transactions.append({
                "id": str(tx.get("id", "")),
                "merchant_name": str(tx.get("merchant_name", "Unknown")),
                "transaction_date": str(tx.get("transaction_date", "")),
                "total_amount": float(tx.get("total_amount", 0) or 0),
                "deductible_amount": float(tx.get("deductible_amount", 0) or 0),
                "status": str(tx.get("status", "needs_review")),
                "created_at": str(tx.get("create_at", "")),
                "receipt_image_url": str(tx.get("receipt_image_url", "") if tx.get("receipt_image_url") else ""),
                "category": category_name,
                "ai_reasoning": str(tx.get("ai_reasoning", "") if tx.get("ai_reasoning") else "")
            })
        
        # Category breakdown
        try:
            transactions_with_rules = supabase.table("transactions").select(
                "rule_id, deductible_amount"
            ).eq("user_id", user_id).eq("status", "verified").execute()

            transactions_with_rules_data = transactions_with_rules.data if transactions_with_rules.data else []
        except Exception as e:
            logger.warning("Failed to fetch transactions with rules: %s", e)
            transactions_with_rules_data = []
        
        category_breakdown = {}
        for t in transactions_with_rules_data:
            rule_id = t.get("rule_id")
            deductible = float(t.get("deductible_amount", 0) or 0)
            
            if rule_id and rule_id in tax_rules_map:
                category_name = tax_rules_map[rule_id]["category_name"]
                max_limit = float(tax_rules_map[rule_id]["max_limit"] or 0)
                
                if category_name not in category_breakdown:
                    category_breakdown[category_name] = {
                        "total_deductible": 0,
                        "max_limit": max_limit,
                        "remaining": max_limit,
                        "is_capped": False
                    }

                category_breakdown[category_name]["total_deductible"] += deductible
                category_breakdown[category_name]["remaining"] = max(
                    0,
                    max_limit - category_breakdown[category_name]["total_deductible"]
                )
                # max_limit == 0 means an income-based cap (e.g. donations), not a fixed one.
                category_breakdown[category_name]["is_capped"] = (
                    max_limit > 0
                    and category_breakdown[category_name]["total_deductible"] >= max_limit
                )
        
        return {
            "success": True,
            "data": {
                "total_deductible_amount": total_deductible,
                "total_transactions": len(transactions_data),
                "status_breakdown": status_counts,
                "recent_transactions": recent_transactions,
                "category_breakdown": category_breakdown
            }
        }
        
    except Exception as e:
        logger.exception("Error in get_dashboard_summary")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch dashboard summary: {str(e)}"
        )


@router.get("/stats", summary="Get quick stats for dashboard cards")
async def get_dashboard_stats(user_id: str = Depends(get_current_user_id)):
    """
    Get quick statistics for dashboard summary cards
    Optimized for fast loading
    """
    
    try:
        # Get verified transactions only
        verified_response = supabase.table("transactions").select(
            "deductible_amount"
        ).eq("user_id", user_id).eq("status", "verified").execute()
        
        # Get all transactions count
        all_response = supabase.table("transactions").select(
            "id"
        ).eq("user_id", user_id).execute()
        
        total_deductible = sum(t.get("deductible_amount", 0) for t in verified_response.data or [])
        total_count = len(all_response.data or [])
        
        return {
            "success": True,
            "data": {
                "total_deductible": total_deductible,
                "total_documents": total_count,
                "verified_count": len(verified_response.data or [])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch dashboard stats: {str(e)}"
        )
