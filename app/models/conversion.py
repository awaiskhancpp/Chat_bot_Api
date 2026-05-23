from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime
from app.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    title= Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)