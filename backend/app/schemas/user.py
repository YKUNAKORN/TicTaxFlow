from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Register schema
class UserRegister(BaseModel):
    """Schema for user registration."""
    full_name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class RegisterResponse(BaseModel):
    """Schema for registration response."""
    message: str
    user: UserResponse


# Log-in schema
class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    """Schema for user login response with JWT tokens from Supabase"""
    message: str
    user: UserResponse
    access_token: str
    refresh_token: str