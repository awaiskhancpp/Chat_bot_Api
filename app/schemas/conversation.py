from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ConversationCreate(BaseModel):
    user_id: str
    title: Optional[str] = "New Conversation"

class ConversationResponse(BaseModel):
    id: int
    user_id: str
    title: str
    created_at: datetime
    
    class Config:
        from_attributes = True