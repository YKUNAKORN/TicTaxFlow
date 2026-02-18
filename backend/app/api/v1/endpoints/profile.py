"""User Profile API endpoints."""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from pydantic import BaseModel

from app.database.database import supabase

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


def extract_user_id_from_token(authorization: Optional[str]) -> str:
    """Extract user ID from JWT token via Supabase Auth."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization token")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Get user from token
        response = supabase.auth.get_user(token)
        
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return response.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


@router.get("/me", summary="Get current user profile")
async def get_my_profile(authorization: Optional[str] = Header(None)):
    """
    Retrieve current authenticated user's profile
    Requires: Authorization header with Bearer token
    """
    user_id = extract_user_id_from_token(authorization)
    
    try:
        # Get user metadata from Supabase Auth
        token = authorization.replace("Bearer ", "")
        auth_response = supabase.auth.get_user(token)
        
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
            print(f"Warning: Could not fetch username from users table: {e}")
        
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
    authorization: Optional[str] = Header(None)
):
    """
    Update current authenticated user's profile
    Requires: Authorization header with Bearer token
    """
    user_id = extract_user_id_from_token(authorization)
    
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
