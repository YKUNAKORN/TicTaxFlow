"""Agent Chat API endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime

from app.core.security import get_current_user_id
from app.services.workflow import run_tax_question_workflow

logger = logging.getLogger(__name__)

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

        # Route through the compiled LangGraph (Router -> Tax Q&A) rather
        # than calling the agent directly, per CLAUDE.md's orchestration rule.
        state = run_tax_question_workflow(request.message)
        response_text = state.get("tax_advice") or "No answer was generated."

        timestamp = datetime.utcnow().isoformat()
        
        return ChatResponse(
            response=response_text,
            timestamp=timestamp
        )
    
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error in chat endpoint")
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat message"
        )
