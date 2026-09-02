"""Agent Chat API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime

from app.agents.tax_expert import ask_tax_question
from app.core.security import get_current_user_id


router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Chat with AI tax expert agent.

    The agent uses RAG to answer questions about Thai tax deductions.
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        response_text = ask_tax_question(request.message)
        
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
