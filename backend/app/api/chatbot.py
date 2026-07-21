# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.api import auth as router_auth
from app.models import models
from app.core import database
from app.services.llm_service import ask_chatbot

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ChatQuery(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: Optional[str] = None

@router.post("/ask", response_model=ChatResponse)
def ask(
    chat_query: ChatQuery,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(router_auth.get_current_active_user)
):
    """
    Ask a business, analytics, or operational question.
    The response will be strictly filtered based on the caller's RBAC role.
    """
    if not chat_query.query or not chat_query.query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty")
        
    try:
        answer = ask_chatbot(current_user, chat_query.query.strip(), db)
        return ChatResponse(answer=answer)
    except Exception as e:
        logger.error(f"Failed to process chatbot request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"The AI service encountered an error: {str(e)}")
