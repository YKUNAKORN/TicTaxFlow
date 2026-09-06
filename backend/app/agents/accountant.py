"""Accountant Agent for managing transactions and tax calculations."""
import logging
from typing import Dict, Any, Optional

from app.core.config import settings
from app.database.database import supabase

logger = logging.getLogger(__name__)


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
            logger.warning("Using tax rule without year filter for %s", category_name)
            return response.data[0]

        return None
    except Exception as e:
        logger.error("Error fetching tax rule: %s", e)
        return None


def get_active_tax_rules(tax_year: int = None) -> list:
    """List every active tax rule for `tax_year` (DEFAULT_TAX_YEAR if
    omitted). Used by the deduction advisor to enumerate categories --
    the cap math itself stays in calculate_deductible_amount /
    get_used_deductible_amount below, not duplicated here.

    Falls back to every active rule regardless of year when nothing
    matches `tax_year` exactly -- same fallback as get_tax_rule_by_category,
    needed because DEFAULT_TAX_YEAR tracks the current calendar year while
    the seeded tax_rules rows are pinned to whichever year they were last
    entered for.
    """
    if tax_year is None:
        tax_year = settings.DEFAULT_TAX_YEAR

    try:
        response = supabase.table("tax_rules").select("*").eq(
            "tax_year", tax_year
        ).eq("is_active", True).execute()

        if response.data:
            return response.data

        logger.warning("No tax rules found for tax_year=%s, using all active rules regardless of year", tax_year)
        response = supabase.table("tax_rules").select("*").eq("is_active", True).execute()
        return response.data or []
    except Exception as e:
        logger.error("Error fetching active tax rules: %s", e)
        return []


def get_used_deductible_amount(
    user_id: str,
    rule_id: str,
    exclude_transaction_id: Optional[str] = None,
) -> float:
    """Sum deductible amounts already verified for this user's category.

    `rule_id` already encodes both category and tax_year, so this is the
    cumulative total to cap the NEXT receipt against (per CLAUDE.md:
    "Deduction caps are cumulative per user + category + tax_year. Never
    cap a single receipt in isolation.").

    `exclude_transaction_id` drops one transaction from the sum. The edit
    path passes the row being edited so its own current amount is not
    double-counted when recalculating its deductible against the cap.
    """
    try:
        query = supabase.table("transactions").select("deductible_amount").eq(
            "user_id", user_id
        ).eq("rule_id", rule_id).eq("status", "verified")

        if exclude_transaction_id is not None:
            query = query.neq("id", exclude_transaction_id)

        response = query.execute()

        return sum(float(t.get("deductible_amount", 0) or 0) for t in (response.data or []))
    except Exception as e:
        logger.error("Error fetching used deductible amount: %s", e)
        return 0.0


def calculate_deductible_amount(
    total_amount: float,
    category_name: str,
    already_used: float = 0.0
) -> Dict[str, Any]:
    """Calculate deductible amount based on tax rules.

    Args:
        total_amount: Amount of the receipt being evaluated now.
        category_name: Tax category to look up the rule for.
        already_used: Deductible total already verified for this user +
            category + tax_year (see `get_used_deductible_amount`). The cap
            is applied cumulatively against this running total, not against
            `total_amount` alone.

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

    # max_limit == 0 means "income-based cap" (donations): the amount-based
    # path below, not a fixed ceiling.
    #
    # KNOWN GAP (see DEMO.md "Known limits", supabase/seed_tax_rules.sql):
    # Thai law caps total donations at 10% of net-of-deductions income (and
    # the 2x education/sports amount counts toward that same 10%). This
    # function has no income in scope, so it cannot enforce that ceiling --
    # it returns the raw (or doubled) amount. Callers that know the user's
    # income must clamp the result. Logged so it is never a silent
    # over-statement.
    if max_limit == 0:
        category = tax_rule.get("category_name", "")
        if "Education" in category or "Sports" in category:
            deductible = total_amount * 2  # e-Donation education/sports: 2x
        else:
            deductible = total_amount  # general donation: actual amount
        logger.warning(
            "calculate_deductible_amount: '%s' uses the income-based path "
            "(deductible=%.2f from amount=%.2f); the statutory 10%%-of-income "
            "donation ceiling is NOT applied here -- clamp upstream if income is known.",
            category or category_name, deductible, total_amount,
        )
        return {
            "amount": deductible,
            "is_capped": False,
            "max_limit": max_limit
        }

    remaining_limit = max(0.0, max_limit - already_used)
    deductible = min(total_amount, remaining_limit)
    is_capped = (already_used + total_amount) > max_limit

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
        logger.debug("insert_transaction called: category=%s, amount=%s", category_name, total_amount)

        # If Tax Expert says not deductible, save with zero deduction
        if not is_deductible:
            logger.debug("Tax Expert: not deductible, saving with deductible_amount=0")
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
            logger.warning("Tax rule not found for category: %s, saving as needs_review", category_name)
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
        logger.debug("Tax rule found: id=%s, category=%s", rule_id, category_name)

        already_used = get_used_deductible_amount(user_id, rule_id)
        calc_result = calculate_deductible_amount(total_amount, category_name, already_used=already_used)
        deductible_amount = calc_result["amount"]
        is_capped = calc_result["is_capped"]
        max_limit = calc_result["max_limit"]

        logger.debug("Calculated deductible: %s THB (capped: %s)", deductible_amount, is_capped)
        
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
        
        logger.debug("Inserting transaction: %s", transaction_data)

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
            logger.error("Supabase insert returned no data")
            return {
                "success": False,
                "error": "Failed to insert transaction - no data returned"
            }

    except Exception as e:
        error_msg = f"Error inserting transaction: {str(e)}"
        logger.exception("Exception in insert_transaction")
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

        # Recompute the capped deductible when EITHER the amount is edited OR
        # the row is being promoted to "verified". The second case matters
        # because get_used_deductible_amount only sums verified rows: several
        # needs_review rows each computed their deductible against a
        # verified-only total at insert time, so verifying them one by one
        # without this re-check could push the category's cumulative total
        # past its cap (CLAUDE.md: caps are cumulative, never per receipt).
        amount_changed = "total_amount" in updates
        being_verified = updates.get("status") == "verified"

        if amount_changed or being_verified:
            current = supabase.table("transactions").select(
                "user_id, rule_id, total_amount"
            ).eq("id", transaction_id).execute()

            if current.data and current.data[0].get("rule_id"):
                row = current.data[0]
                rule_id = row["rule_id"]
                user_id = row["user_id"]
                effective_amount = updates["total_amount"] if amount_changed else row.get("total_amount", 0)
                rule = supabase.table("tax_rules").select("category_name").eq("id", rule_id).execute()

                if rule.data:
                    category_name = rule.data[0]["category_name"]
                    # Cap against the category's REMAINING headroom, same as
                    # the upload path. Exclude this row so its own current
                    # deductible is not double-counted in already_used.
                    already_used = get_used_deductible_amount(
                        user_id, rule_id, exclude_transaction_id=transaction_id
                    )
                    calc_result = calculate_deductible_amount(
                        effective_amount,
                        category_name,
                        already_used=already_used,
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
        
        logger.debug(
            "Saving transaction: merchant=%s, date=%s, amount=%s",
            merchant_name, transaction_date, total_amount,
        )

        # Determine deductibility and reasoning from Tax Expert result
        is_deductible = True
        ai_reasoning = None
        if tax_result and isinstance(tax_result, dict):
            is_deductible = tax_result.get("is_deductible", True)
            ai_reasoning = tax_result.get("reasoning")

        # Auto-verify only when the Tax Expert is confident: is_deductible
        # True AND a concrete category (not "None"). is_deductible=False is
        # already routed to status="not_deductible" by insert_transaction
        # regardless of what we pass here; a "None" category is handled
        # explicitly rather than relying on get_tax_rule_by_category simply
        # failing to find a "None" row, since that would silently break if
        # such a row were ever added. Both cases stay out of
        # total_deductible_amount until a human confirms them.
        status = "needs_review" if category_name in (None, "None", "") else "verified"

        result = insert_transaction(
            user_id=user_id,
            merchant_name=merchant_name,
            merchant_tax_id=merchant_tax_id,
            transaction_date=transaction_date,
            total_amount=total_amount,
            category_name=category_name,
            receipt_image_url=receipt_image_url,
            status=status,
            is_deductible=is_deductible,
            ai_reasoning=ai_reasoning
        )

        return result

    except Exception as e:
        logger.exception("Exception in save_receipt_from_inspector")
        return {
            "success": False,
            "error": f"Error saving receipt data: {str(e)}"
        }
