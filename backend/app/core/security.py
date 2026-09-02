"""Shared authentication dependencies."""
import logging
from typing import Optional

from fastapi import Header, HTTPException

from app.database.database import get_auth_client

logger = logging.getLogger(__name__)


def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """FastAPI dependency that validates the Supabase JWT and returns the user id.

    Every endpoint that reads or writes a user's data must depend on this
    instead of trusting a client-supplied user_id.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization token")

    token = authorization.replace("Bearer ", "")

    try:
        auth_client = get_auth_client()
        response = auth_client.auth.get_user(token)

        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return response.user.id
    except HTTPException:
        raise
    except Exception:
        logger.warning("Authentication failed while validating token")
        raise HTTPException(status_code=401, detail="Authentication failed")
