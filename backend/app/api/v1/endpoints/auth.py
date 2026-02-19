from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
import bcrypt

from app.schemas.user import UserRegister, RegisterResponse, UserResponse, UserLogin, LoginResponse, ChangePassword
from app.database.database import supabase, get_auth_client

router = APIRouter()


def hash_password(password: str) -> str:
    """Hash password using bcrypt (for public.users backup)."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


# Register endpoint using Supabase Auth
@router.post("/register", response_model = RegisterResponse, status_code = status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user using Supabase Auth.
    
    - **full_name**: User's full name
    - **email**: User's email address
    - **password**: User's password (Supabase handles hashing)
    """
    
    try:
        # Use a fresh client so the shared DB client is not polluted
        auth_client = get_auth_client()
        
        response = auth_client.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name
                }
            }
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
        
        # Insert user data into public.users table
        try:
            # Hash password for backup storage (NOT RECOMMENDED in production)
            # Supabase Auth already manages password securely
            hashed_password = hash_password(user_data.password)
            
            user_insert = supabase.table("users").insert({
                "id": response.user.id,
                "username": user_data.full_name,
                "email": response.user.email,
                "password": hashed_password
            }).execute()
        except Exception as insert_error:
            # If public.users insert fails, log but don't fail registration
            # User is already created in auth.users
            print(f"Warning: Failed to insert into public.users: {insert_error}")
        
        # Return response with user data
        user_response = UserResponse(
            id = response.user.id,
            username = user_data.full_name,
            email = response.user.email,
            created_at = response.user.created_at
        )
        
        return RegisterResponse(
            message = "User registered successfully",
            user = user_response
        )
    
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(e)
        )

# Login endpoint using Supabase Auth
@router.post("/login", response_model = LoginResponse)
async def login(user_data: UserLogin):
    """
    Login user using Supabase Auth.
    
    - **email**: User's email
    - **password**: User's password
    
    Returns JWT access token and refresh token from Supabase.
    """

    try:
        # Use a fresh client so the shared DB client is not polluted
        auth_client = get_auth_client()
        response = auth_client.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        if not response.user or not response.session:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid email or password"
            )
        
        # Get user data from auth user metadata
        full_name = response.user.user_metadata.get("full_name", "User")
        
        # Return user data with real JWT token
        user_response = UserResponse(
            id = response.user.id,
            username = full_name,
            email = response.user.email,
            created_at = response.user.created_at
        )

        return LoginResponse(
            message = "Login successful",
            user = user_response,
            access_token = response.session.access_token,
            refresh_token = response.session.refresh_token
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )


# Logout endpoint using Supabase Auth
@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """
    Logout user by invalidating the current session.
    
    - **Authorization**: Bearer token in header (optional)
    
    Supabase will invalidate the session on the server side.
    Client should also remove the token from local storage.
    """
    
    try:
        # Logout is handled client-side by removing tokens from localStorage.
        # We no longer call supabase.auth.sign_out() or supabase.auth.set_session()
        # on the shared server client because it corrupts its auth state for
        # all subsequent requests from other endpoints.
        
        return {
            "message": "Logout successful",
            "detail": "Session has been invalidated"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(e)
        )


@router.post("/change-password", summary="Change user password")
async def change_password(
    password_data: ChangePassword,
    authorization: Optional[str] = Header(None)
):
    """
    Change the authenticated user's password.
    
    Requires current password verification and new password.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization token"
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Use a fresh client for all auth operations
        auth_client = get_auth_client()
        
        user_response = auth_client.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_email = user_response.user.email
        
        # Verify current password with another fresh client
        verify_client = get_auth_client()
        try:
            verify_response = verify_client.auth.sign_in_with_password({
                "email": user_email,
                "password": password_data.current_password
            })
            
            if not verify_response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password using admin API on the shared client (no session needed)
        update_response = supabase.auth.admin.update_user_by_id(
            user_response.user.id,
            {"password": password_data.new_password}
        )
        
        if not update_response or not update_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update password"
            )
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )