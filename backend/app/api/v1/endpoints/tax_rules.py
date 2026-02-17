"""Tax Rules API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from app.database.database import supabase

router = APIRouter()


class TaxRuleResponse(BaseModel):
    id: str
    category_name: str
    max_limit: float
    tax_year: int
    is_active: bool
    created_at: Optional[str] = None


@router.get("/", summary="Get all tax rules")
async def get_all_tax_rules(
    tax_year: Optional[int] = None,
    is_active: Optional[bool] = True
):
    """
    Retrieve all tax rules
    - Optional filter by tax_year
    - Optional filter by is_active (default: True)
    """
    try:
        query = supabase.table("tax_rules").select("*")
        
        if tax_year:
            query = query.eq("tax_year", tax_year)
        
        if is_active is not None:
            query = query.eq("is_active", is_active)
        
        response = query.order("category_name").execute()
        
        return {
            "success": True,
            "data": response.data,
            "count": len(response.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tax rules: {str(e)}")


@router.get("/{rule_id}", summary="Get a specific tax rule by ID")
async def get_tax_rule_by_id(rule_id: str):
    """
    Retrieve a single tax rule by ID
    """
    try:
        response = supabase.table("tax_rules").select("*").eq("id", rule_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Tax rule not found")
        
        return {
            "success": True,
            "data": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tax rule: {str(e)}")


@router.get("/category/{category_name}", summary="Get tax rule by category name")
async def get_tax_rule_by_category(category_name: str, tax_year: Optional[int] = 2026):
    """
    Retrieve tax rule by category name and tax year
    Default tax_year: 2026
    """
    try:
        query = supabase.table("tax_rules").select("*").eq("category_name", category_name).eq("is_active", True)
        
        if tax_year:
            query = query.eq("tax_year", tax_year)
        
        response = query.execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail=f"Tax rule for category '{category_name}' not found")
        
        return {
            "success": True,
            "data": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tax rule: {str(e)}")
