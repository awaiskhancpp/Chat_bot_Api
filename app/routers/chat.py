from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from groq import RateLimitError, AuthenticationError, APIError

from app.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import generate_ai_response
from app.services.context_builder import build_context

router = APIRouter(prefix="/chat", tags=["Chat"])

HISTORY_LIMIT = 10


@router.post("/send", response_model=ChatResponse)
async def chat(data: ChatRequest, db: Session = Depends(get_db)):
    # Resolve or create conversation
    if data.conversation_id is None:
        conversation = Conversation()
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    else:
        conversation = db.query(Conversation).filter(
            Conversation.id == data.conversation_id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # Persist user message
    db.add(Message(conversation_id=conversation.id, role="user", content=data.message))
    db.commit()

    # Fetch recent history for conversation memory (oldest → newest)
    history = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
    ai_messages = [{"role": m.role, "content": m.content} for m in reversed(history)]

    # Fetch relevant live CMS context based on user intent
    company_name, context = await build_context(data.message)

    # Generate AI response
    try:
        ai_response = await generate_ai_response(ai_messages, company_name, context)
    except RateLimitError:
        raise HTTPException(status_code=429, detail="AI service quota exceeded. Please try again later.")
    except AuthenticationError:
        raise HTTPException(status_code=503, detail="AI service authentication failed. Check the API key.")
    except APIError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")

    # Persist assistant message
    db.add(Message(conversation_id=conversation.id, role="assistant", content=ai_response))
    db.commit()

    return {"conversation_id": conversation.id, "bot_reply": ai_response}
