from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from pydantic import BaseModel

from app.agents.accountant import (
    insert_transaction,
    update_transaction,
    get_user_transactions,
    save_receipt_from_inspector
)
from app.core.security import get_current_user_id
from app.database.database import supabase

router = APIRouter()


def _get_owned_transaction(transaction_id: str, user_id: str) -> dict:
    """Fetch a transaction and verify it belongs to user_id, else raise 404."""
    response = supabase.table("transactions").select("*").eq("id", transaction_id).execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction = response.data[0]
    if transaction.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


class TransactionCreate(BaseModel):
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
async def create_transaction(
    transaction: TransactionCreate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new transaction manually
    """
    result = insert_transaction(
        user_id=user_id,
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


@router.get("/user", summary="Get all transactions for the current user")
async def get_transactions(status: Optional[str] = None, user_id: str = Depends(get_current_user_id)):
    """
    Retrieve all transactions for the authenticated user
    Optional: Filter by status (verified, needs_review, rejected)
    """
    result = get_user_transactions(user_id, status)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to fetch transactions"))

    return result


@router.get("/summary", summary="Get transaction summary for the current user")
async def get_transaction_summary(user_id: str = Depends(get_current_user_id)):
    """
    Get summary statistics for the authenticated user's transactions
    Returns: total deductible amount, count by status, count by category
    """
    try:
        # Get all verified transactions
        verified_response = supabase.table("transactions").select(
            "deductible_amount, status"
        ).eq("user_id", user_id).eq("status", "verified").execute()

        # Get all transactions for counts
        all_response = supabase.table("transactions").select(
            "id, status"
        ).eq("user_id", user_id).execute()

        verified_rows = verified_response.data or []
        all_rows = all_response.data or []

        # Calculate total deductible. Supabase numerics can come back as
        # strings, so coerce before summing (same as dashboard.py).
        total_deductible = sum(float(t.get("deductible_amount", 0) or 0) for t in verified_rows)

        # Count by status
        status_counts = {"verified": 0, "needs_review": 0, "rejected": 0}
        for t in all_rows:
            status = t.get("status", "needs_review")
            if status in status_counts:
                status_counts[status] += 1

        return {
            "success": True,
            "data": {
                "total_deductible_amount": total_deductible,
                "total_transactions": len(all_rows),
                "status_breakdown": status_counts
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {str(e)}")


@router.post("/save-receipt", summary="Save transaction from receipt data")
async def save_receipt(
    date: str = Form(...),
    amount: float = Form(...),
    tax_id: str = Form(...),
    merchant_name: str = Form("Unknown Merchant"),
    category_name: str = Form("Health Insurance"),
    user_id: str = Depends(get_current_user_id)
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


@router.get("/{transaction_id}", summary="Get a specific transaction by ID")
async def get_transaction_by_id(transaction_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Retrieve a single transaction by ID. Only the owning user may access it.
    """
    try:
        transaction = _get_owned_transaction(transaction_id, user_id)
        return {
            "success": True,
            "data": transaction
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch transaction: {str(e)}")


@router.put("/{transaction_id}", summary="Update an existing transaction")
async def update_transaction_endpoint(
    transaction_id: str,
    updates: TransactionUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Update transaction details. Only the owning user may update it.
    """
    _get_owned_transaction(transaction_id, user_id)

    update_dict = updates.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = update_transaction(transaction_id, update_dict)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to update transaction"))

    return result


@router.delete("/{transaction_id}", summary="Delete a transaction")
async def delete_transaction(transaction_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Delete a transaction by ID. Only the owning user may delete it.
    """
    try:
        _get_owned_transaction(transaction_id, user_id)

        supabase.table("transactions").delete().eq("id", transaction_id).execute()

        return {
            "success": True,
            "message": "Transaction deleted successfully",
            "transaction_id": transaction_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete transaction: {str(e)}")
