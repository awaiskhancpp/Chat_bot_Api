from sqlalchemy.orm import Session
from app.models import Message as MessageModel

def get_conversation_history(conversation_id: int, db: Session, limit: int = 10):
    """Fetch last N messages from conversation"""
    messages = db.query(MessageModel).filter(
        MessageModel.conversation_id == conversation_id
    ).order_by(MessageModel.created_at.desc()).limit(limit).all()
    
    return list(reversed(messages))