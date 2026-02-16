from fastapi import APIRouter, HTTPException, status
import bcrypt
from datetime import datetime
import uuid

from app.schemas.user import UserRegister, RegisterResponse, UserResponse
from app.database.database import supabase

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user.
    
    - **full_name**: User's full name
    - **email**: User's email address
    - **password**: User's password (will be hashed)
    """
    
    # Check if email already exists
    existing_user = supabase.table("users").select("email").eq("email", user_data.email).execute()
    
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = bcrypt.hashpw(
        user_data.password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Generate UUID for user
    user_id = str(uuid.uuid4())
    
    # Prepare user data
    new_user = {
        "id": user_id,
        "username": user_data.full_name,
        "email": user_data.email,
        "password": hashed_password,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Insert user into database
    try:
        result = supabase.table("users").insert(new_user).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        created_user = result.data[0]
        
        # Return response without password
        user_response = UserResponse(
            id=created_user["id"],
            username=created_user["username"],
            email=created_user["email"],
            created_at=created_user["created_at"]
        )
        
        return RegisterResponse(
            message="User registered successfully",
            user=user_response
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
