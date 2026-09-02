"""User Profile API endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from pydantic import BaseModel

from app.database.database import supabase, get_auth_client
from app.core.security import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


class ProfileResponse(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    annual_income: Optional[float] = None
    created_at: Optional[str] = None


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    annual_income: Optional[float] = None


@router.get("/me", summary="Get current user profile")
async def get_my_profile(
    authorization: Optional[str] = Header(None),
    user_id: str = Depends(get_current_user_id)
):
    """
    Retrieve current authenticated user's profile
    Requires: Authorization header with Bearer token
    """
    try:
        # Get user metadata from Supabase Auth using a fresh client
        token = authorization.replace("Bearer ", "")
        auth_client = get_auth_client()
        auth_response = auth_client.auth.get_user(token)
        
        if not auth_response or not auth_response.user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = auth_response.user
        
        # Try to get username from public.users table
        username = user.user_metadata.get("full_name")
        try:
            user_data = supabase.table("users").select("username").eq("id", user.id).execute()
            if user_data.data and len(user_data.data) > 0:
                username = user_data.data[0].get("username", username)
        except Exception as e:
            logger.warning("Could not fetch username from users table: %s", e)
        
        # Build profile response
        profile = {
            "id": user.id,
            "email": user.email,
            "username": username,
            "full_name": user.user_metadata.get("full_name"),
            "phone": user.user_metadata.get("phone"),
            "annual_income": user.user_metadata.get("annual_income"),
            "created_at": user.created_at
        }
        
        return {
            "success": True,
            "data": profile
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {str(e)}")


@router.put("/me", summary="Update current user profile")
async def update_my_profile(
    updates: ProfileUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Update current authenticated user's profile
    Requires: Authorization header with Bearer token
    """
    try:
        # Build update data
        update_data = updates.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update user metadata via Supabase Auth
        response = supabase.auth.admin.update_user_by_id(
            user_id,
            {"user_metadata": update_data}
        )
        
        if not response or not response.user:
            raise HTTPException(status_code=400, detail="Failed to update profile")
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": {
                "id": response.user.id,
                "email": response.user.email,
                **update_data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")
