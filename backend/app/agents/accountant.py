"""Accountant Agent for managing transactions and tax calculations."""
from datetime import datetime
from typing import Dict, Any, Optional
from supabase import create_client, Client

from app.core.config import settings


if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def get_tax_rule_by_category(category_name: str, tax_year: int = None) -> Optional[Dict[str, Any]]:
    """Fetch tax rule from database by category name and tax year."""
    if tax_year is None:
        tax_year = settings.DEFAULT_TAX_YEAR
    
    try:
        response = supabase.table("tax_rules").select("*").eq(
            "category_name", category_name
        ).eq("tax_year", tax_year).eq("is_active", True).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        
        # Fallback: try without tax_year if not found
        response = supabase.table("tax_rules").select("*").eq(
            "category_name", category_name
        ).eq("is_active", True).execute()
        
        if response.data and len(response.data) > 0:
            print(f"Warning: Using tax rule without year filter for {category_name}")
            return response.data[0]
        
        return None
    except Exception as e:
        print(f"Error fetching tax rule: {str(e)}")
        return None


def calculate_deductible_amount(total_amount: float, category_name: str) -> Dict[str, Any]:
    """Calculate deductible amount based on tax rules.
    
    Returns:
        Dict with 'amount', 'is_capped', 'max_limit' keys
    """
    tax_rule = get_tax_rule_by_category(category_name)
    
    if not tax_rule:
        return {
            "amount": 0.0,
            "is_capped": False,
            "max_limit": 0.0
        }
    
    max_limit = tax_rule.get("max_limit", 0.0)

    # Donations with max_limit=0 means income-based limit (use actual amount)
    if max_limit == 0:
        category = tax_rule.get("category_name", "")
        if "Education" in category or "Sports" in category:
            # Education/Sports donations get 2x deduction
            deductible = total_amount * 2
        else:
            # General donations or other income-based: use actual amount
            deductible = total_amount
        return {
            "amount": deductible,
            "is_capped": False,
            "max_limit": max_limit
        }

    deductible = min(total_amount, max_limit)
    is_capped = total_amount > max_limit
    
    return {
        "amount": deductible,
        "is_capped": is_capped,
        "max_limit": max_limit
    }


def insert_transaction(
    user_id: str,
    merchant_name: str,
    merchant_tax_id: str,
    transaction_date: str,
    total_amount: float,
    category_name: str = "Health Insurance",
    receipt_image_url: Optional[str] = None,
    status: str = "needs_review",
    is_deductible: bool = True,
    ai_reasoning: Optional[str] = None
) -> Dict[str, Any]:
    """Insert a new transaction into the database.
    
    Args:
        user_id: UUID of the user
        merchant_name: Name of the merchant
        merchant_tax_id: Tax ID of the merchant
        transaction_date: Date of transaction (YYYY-MM-DD format)
        total_amount: Total amount of the transaction
        category_name: Tax category name from Tax Expert
        receipt_image_url: URL to receipt image in Supabase Storage
        status: Transaction status (default: needs_review)
        is_deductible: Whether the Tax Expert determined this is deductible
        ai_reasoning: Tax Expert's reasoning for the classification
    
    Returns:
        Dict containing success status and transaction data or error message
    """
    try:
        print(f"insert_transaction called: user_id={user_id}, category={category_name}, amount={total_amount}")
        
        # If Tax Expert says not deductible, save with zero deduction
        if not is_deductible:
            print(f"Tax Expert: not deductible, saving with deductible_amount=0")
            transaction_data = {
                "user_id": user_id,
                "rule_id": None,
                "receipt_image_url": receipt_image_url,
                "merchant_name": merchant_name,
                "merchant_tax_id": merchant_tax_id,
                "transaction_date": transaction_date,
                "total_amount": total_amount,
                "deductible_amount": 0,
                "status": "not_deductible",
                "ai_reasoning": ai_reasoning
            }

            # Try to attach a rule_id if the category exists
            tax_rule = get_tax_rule_by_category(category_name)
            if tax_rule:
                transaction_data["rule_id"] = tax_rule["id"]

            response = supabase.table("transactions").insert(transaction_data).execute()

            if response.data:
                return {
                    "success": True,
                    "transaction": response.data[0],
                    "message": f"Transaction saved as not deductible. Amount: {total_amount:,.2f} THB",
                    "is_capped": False,
                    "data": response.data[0]
                }
            return {
                "success": False,
                "error": "Failed to insert transaction - no data returned"
            }

        tax_rule = get_tax_rule_by_category(category_name)
        
        if not tax_rule:
            # Tax rule not found in DB - save transaction but flag for review
            print(f"WARNING: Tax rule not found for category: {category_name}, saving as needs_review")
            transaction_data = {
                "user_id": user_id,
                "rule_id": None,
                "receipt_image_url": receipt_image_url,
                "merchant_name": merchant_name,
                "merchant_tax_id": merchant_tax_id,
                "transaction_date": transaction_date,
                "total_amount": total_amount,
                "deductible_amount": 0,
                "status": "needs_review",
                "ai_reasoning": ai_reasoning
            }

            response = supabase.table("transactions").insert(transaction_data).execute()

            if response.data:
                return {
                    "success": True,
                    "transaction": response.data[0],
                    "message": f"Transaction saved for review. Category '{category_name}' not found in tax rules.",
                    "is_capped": False,
                    "data": response.data[0]
                }
            return {
                "success": False,
                "error": "Failed to insert transaction - no data returned"
            }
        
        rule_id = tax_rule["id"]
        print(f"Tax rule found: id={rule_id}, category={category_name}")
        
        calc_result = calculate_deductible_amount(total_amount, category_name)
        deductible_amount = calc_result["amount"]
        is_capped = calc_result["is_capped"]
        max_limit = calc_result["max_limit"]
        
        print(f"Calculated deductible: {deductible_amount} THB (capped: {is_capped})")
        
        transaction_data = {
            "user_id": user_id,
            "rule_id": rule_id,
            "receipt_image_url": receipt_image_url,
            "merchant_name": merchant_name,
            "merchant_tax_id": merchant_tax_id,
            "transaction_date": transaction_date,
            "total_amount": total_amount,
            "deductible_amount": deductible_amount,
            "status": status,
            "ai_reasoning": ai_reasoning
        }
        
        print(f"Inserting transaction: {transaction_data}")
        
        response = supabase.table("transactions").insert(transaction_data).execute()
        
        if response.data:
            if is_capped:
                message = f"Transaction saved. Amount: {total_amount:,.2f} THB, Deductible: {deductible_amount:,.2f} THB (capped at {max_limit:,.2f} THB limit)"
            else:
                message = f"Transaction saved. Deductible amount: {deductible_amount:,.2f} THB"
            
            return {
                "success": True,
                "transaction": response.data[0],
                "message": message,
                "is_capped": is_capped,
                "data": response.data[0]
            }
        else:
            print("ERROR: Supabase insert returned no data")
            return {
                "success": False,
                "error": "Failed to insert transaction - no data returned"
            }
            
    except Exception as e:
        error_msg = f"Error inserting transaction: {str(e)}"
        print(f"EXCEPTION in insert_transaction: {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": error_msg
        }


def update_transaction(
    transaction_id: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """Update an existing transaction.
    
    Args:
        transaction_id: UUID of the transaction to update
        updates: Dictionary of fields to update
    
    Returns:
        Dict containing success status and updated transaction data or error message
    """
    try:
        recalculated = False
        if "total_amount" in updates:
            current = supabase.table("transactions").select("rule_id").eq("id", transaction_id).execute()
            
            if current.data:
                rule = supabase.table("tax_rules").select("category_name").eq("id", current.data[0]["rule_id"]).execute()
                
                if rule.data:
                    category_name = rule.data[0]["category_name"]
                    calc_result = calculate_deductible_amount(
                        updates["total_amount"],
                        category_name
                    )
                    updates["deductible_amount"] = calc_result["amount"]
                    recalculated = True
        
        response = supabase.table("transactions").update(updates).eq("id", transaction_id).execute()
        
        if response.data:
            updated_transaction = response.data[0]
            message = "Transaction updated successfully"
            
            if recalculated:
                total = updated_transaction.get("total_amount", 0)
                deductible = updated_transaction.get("deductible_amount", 0)
                if total > deductible:
                    message += f" (Deductible capped at {deductible:,.2f} THB)"
            
            return {
                "success": True,
                "transaction": updated_transaction,
                "message": message
            }
        else:
            return {
                "success": False,
                "error": "Failed to update transaction"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error updating transaction: {str(e)}"
        }


def get_user_transactions(user_id: str, status: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve all transactions for a user.
    
    Args:
        user_id: UUID of the user
        status: Optional status filter (verified, needs_review, rejected)
    
    Returns:
        Dict containing success status and list of transactions
    """
    try:
        query = supabase.table("transactions").select("*").eq("user_id", user_id)
        
        if status:
            query = query.eq("status", status)
        
        response = query.order("create_at", desc=True).execute()
        
        return {
            "success": True,
            "transactions": response.data,
            "count": len(response.data)
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching transactions: {str(e)}"
        }


def save_receipt_from_inspector(
    user_id: str,
    receipt_data: Dict[str, Any],
    category_name: str = "Health Insurance",
    receipt_image_url: str = None,
    tax_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Save transaction from Inspector Agent output.
    
    Args:
        user_id: UUID of the user
        receipt_data: Dict containing date, amount, tax_id from Inspector Agent
        category_name: Tax category from Tax Expert
        receipt_image_url: URL to the receipt image in Supabase Storage
        tax_result: Structured output from Tax Expert (is_deductible, category, reasoning)
    
    Returns:
        Dict containing success status and transaction data
    """
    try:
        transaction_date = receipt_data.get("date", "")
        total_amount = receipt_data.get("amount", 0)
        merchant_tax_id = receipt_data.get("tax_id", "")
        merchant_name = receipt_data.get("merchant_name", "Unknown Merchant")
        
        # Validate required fields
        if not transaction_date:
            return {
                "success": False,
                "error": "Missing transaction date in receipt data"
            }
        
        if not total_amount or total_amount == 0:
            return {
                "success": False,
                "error": f"Invalid or missing amount in receipt data: {total_amount}"
            }
        
        try:
            total_amount = float(total_amount)
        except (ValueError, TypeError) as e:
            return {
                "success": False,
                "error": f"Amount is not a valid number: {total_amount}"
            }
        
        print(f"Saving transaction: merchant={merchant_name}, date={transaction_date}, amount={total_amount}, tax_id={merchant_tax_id}")
        
        # Determine deductibility and reasoning from Tax Expert result
        is_deductible = True
        ai_reasoning = None
        if tax_result and isinstance(tax_result, dict):
            is_deductible = tax_result.get("is_deductible", True)
            ai_reasoning = tax_result.get("reasoning")

        result = insert_transaction(
            user_id=user_id,
            merchant_name=merchant_name,
            merchant_tax_id=merchant_tax_id,
            transaction_date=transaction_date,
            total_amount=total_amount,
            category_name=category_name,
            receipt_image_url=receipt_image_url,
            status="verified",
            is_deductible=is_deductible,
            ai_reasoning=ai_reasoning
        )
        
        return result
        
    except Exception as e:
        print(f"Exception in save_receipt_from_inspector: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": f"Error saving receipt data: {str(e)}"
        }
