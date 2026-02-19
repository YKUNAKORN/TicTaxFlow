"""Agent Chat API endpoints."""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.database.database import supabase, get_auth_client
from app.agents.tax_expert import ask_tax_expert


router = APIRouter()


def extract_user_id_from_token(authorization: Optional[str]) -> str:
    """Extract user ID from JWT token via Supabase Auth."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization token")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        auth_client = get_auth_client()
        response = auth_client.auth.get_user(token)
        
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return response.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Chat with AI tax expert agent.
    
    The agent uses RAG to answer questions about Thai tax deductions.
    """
    user_id = extract_user_id_from_token(authorization)
    
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        response_text = ask_tax_expert(request.message)
        
        timestamp = datetime.utcnow().isoformat()
        
        return ChatResponse(
            response=response_text,
            timestamp=timestamp
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat message"
        )
