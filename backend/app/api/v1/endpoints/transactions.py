from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from pydantic import BaseModel

from app.agents.accountant import (
    insert_transaction,
    update_transaction,
    get_user_transactions,
    save_receipt_from_inspector
)

router = APIRouter()


class TransactionCreate(BaseModel):
    user_id: str
    merchant_name: str
    merchant_tax_id: str
    transaction_date: str
    total_amount: float
    category_name: str = "Health Insurance"
    receipt_image_url: Optional[str] = None
    status: str = "needs_review"


class TransactionUpdate(BaseModel):
    merchant_name: Optional[str] = None
    merchant_tax_id: Optional[str] = None
    transaction_date: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None


@router.post("/create", summary="Create a new transaction")
async def create_transaction(transaction: TransactionCreate):
    """
    Create a new transaction manually
    """
    result = insert_transaction(
        user_id=transaction.user_id,
        merchant_name=transaction.merchant_name,
        merchant_tax_id=transaction.merchant_tax_id,
        transaction_date=transaction.transaction_date,
        total_amount=transaction.total_amount,
        category_name=transaction.category_name,
        receipt_image_url=transaction.receipt_image_url,
        status=transaction.status
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create transaction"))
    
    return result


@router.put("/{transaction_id}", summary="Update an existing transaction")
async def update_transaction_endpoint(transaction_id: str, updates: TransactionUpdate):
    """
    Update transaction details
    """
    update_dict = updates.model_dump(exclude_unset=True)
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = update_transaction(transaction_id, update_dict)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to update transaction"))
    
    return result


@router.get("/user/{user_id}", summary="Get all transactions for a user")
async def get_transactions(user_id: str, status: Optional[str] = None):
    """
    Retrieve all transactions for a specific user
    Optional: Filter by status (verified, needs_review, rejected)
    """
    result = get_user_transactions(user_id, status)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to fetch transactions"))
    
    return result


@router.get("/{transaction_id}", summary="Get a specific transaction by ID")
async def get_transaction_by_id(transaction_id: str):
    """
    Retrieve a single transaction by ID
    """
    from app.database.database import supabase
    
    try:
        response = supabase.table("transactions").select("*").eq("id", transaction_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return {
            "success": True,
            "data": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch transaction: {str(e)}")


@router.delete("/{transaction_id}", summary="Delete a transaction")
async def delete_transaction(transaction_id: str):
    """
    Delete a transaction by ID
    """
    from app.database.database import supabase
    
    try:
        # Check if transaction exists
        check_response = supabase.table("transactions").select("id").eq("id", transaction_id).execute()
        
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Delete transaction
        response = supabase.table("transactions").delete().eq("id", transaction_id).execute()
        
        return {
            "success": True,
            "message": "Transaction deleted successfully",
            "transaction_id": transaction_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete transaction: {str(e)}")


@router.get("/summary/{user_id}", summary="Get transaction summary for a user")
async def get_transaction_summary(user_id: str):
    """
    Get summary statistics for user's transactions
    Returns: total deductible amount, count by status, count by category
    """
    from app.database.database import supabase
    
    try:
        # Get all verified transactions
        verified_response = supabase.table("transactions").select(
            "deductible_amount, status"
        ).eq("user_id", user_id).eq("status", "verified").execute()
        
        # Get all transactions for counts
        all_response = supabase.table("transactions").select(
            "id, status"
        ).eq("user_id", user_id).execute()
        
        # Calculate total deductible
        total_deductible = sum(t.get("deductible_amount", 0) for t in verified_response.data)
        
        # Count by status
        status_counts = {"verified": 0, "needs_review": 0, "rejected": 0}
        for t in all_response.data:
            status = t.get("status", "needs_review")
            if status in status_counts:
                status_counts[status] += 1
        
        return {
            "success": True,
            "data": {
                "total_deductible_amount": total_deductible,
                "total_transactions": len(all_response.data),
                "status_breakdown": status_counts
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {str(e)}")


@router.post("/save-receipt", summary="Save transaction from receipt data")
async def save_receipt(
    user_id: str = Form(...),
    date: str = Form(...),
    amount: float = Form(...),
    tax_id: str = Form(...),
    merchant_name: str = Form("Unknown Merchant"),
    category_name: str = Form("Health Insurance")
):
    """
    Save transaction from extracted receipt data
    This endpoint is typically called after the Inspector Agent extracts data
    """
    receipt_data = {
        "date": date,
        "amount": amount,
        "tax_id": tax_id,
        "merchant_name": merchant_name
    }
    
    result = save_receipt_from_inspector(
        user_id=user_id,
        receipt_data=receipt_data,
        category_name=category_name
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to save receipt"))
    
    return result
