from sqlalchemy import Column, Integer, DateTime
from datetime import datetime
from app.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )