"""Dashboard Summary API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.database.database import supabase

router = APIRouter()


@router.get("/summary/{user_id}", summary="Get dashboard summary for a user")
async def get_dashboard_summary(user_id: str):
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
        # Get all transactions for the user
        all_transactions = supabase.table("transactions").select(
            "id, merchant_name, transaction_date, total_amount, deductible_amount, status, created_at"
        ).eq("user_id", user_id).order("created_at", desc=True).execute()
        
        transactions_data = all_transactions.data or []
        
        # Calculate total deductible (verified only)
        total_deductible = sum(
            t.get("deductible_amount", 0) 
            for t in transactions_data 
            if t.get("status") == "verified"
        )
        
        # Count by status
        status_counts = {"verified": 0, "needs_review": 0, "rejected": 0}
        for t in transactions_data:
            status = t.get("status", "needs_review")
            if status in status_counts:
                status_counts[status] += 1
        
        # Get recent transactions (last 5)
        recent_transactions = transactions_data[:5]
        
        # Category breakdown
        # Get all tax rules to map categories
        tax_rules_response = supabase.table("tax_rules").select(
            "id, category_name, max_limit"
        ).eq("is_active", True).execute()
        
        tax_rules_map = {rule["id"]: rule for rule in tax_rules_response.data or []}
        
        # Get transactions with rule_id to calculate category breakdown
        transactions_with_rules = supabase.table("transactions").select(
            "rule_id, deductible_amount"
        ).eq("user_id", user_id).eq("status", "verified").execute()
        
        category_breakdown = {}
        for t in transactions_with_rules.data or []:
            rule_id = t.get("rule_id")
            deductible = t.get("deductible_amount", 0)
            
            if rule_id and rule_id in tax_rules_map:
                category_name = tax_rules_map[rule_id]["category_name"]
                max_limit = tax_rules_map[rule_id]["max_limit"]
                
                if category_name not in category_breakdown:
                    category_breakdown[category_name] = {
                        "total_deductible": 0,
                        "max_limit": max_limit,
                        "remaining": max_limit
                    }
                
                category_breakdown[category_name]["total_deductible"] += deductible
                category_breakdown[category_name]["remaining"] = max(
                    0, 
                    max_limit - category_breakdown[category_name]["total_deductible"]
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
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch dashboard summary: {str(e)}"
        )


@router.get("/stats/{user_id}", summary="Get quick stats for dashboard cards")
async def get_dashboard_stats(user_id: str):
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
