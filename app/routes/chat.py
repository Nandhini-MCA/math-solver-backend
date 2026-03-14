from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, ChatSession, ChatMessage
from app.schemas import ChatMessageRequest, ChatMessageResponse
from app.dependencies import get_current_user
from app.services.ai_service import chat_with_tutor
import os

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatMessageResponse)
async def chat_interaction(req: ChatMessageRequest, session_id: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Find active session or create new one
    chat_session = None
    if session_id:
        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    
    if not chat_session:
        chat_session = ChatSession(user_id=current_user.id)
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
    
    # Save user message
    user_msg = ChatMessage(session_id=chat_session.id, message=req.message, role="user")
    db.add(user_msg)
    db.commit()

    # Get context history
    history = db.query(ChatMessage).filter(ChatMessage.session_id == chat_session.id).order_by(ChatMessage.timestamp).limit(10).all()
    messages_payload = [{"role": msg.role.value, "content": msg.message} for msg in history]

    # Generate response from AI Tutor
    ai_response_text = await chat_with_tutor(messages_payload)
    
    # Save AI response
    ai_msg = ChatMessage(session_id=chat_session.id, message=ai_response_text, role="ai")
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return ai_msg
