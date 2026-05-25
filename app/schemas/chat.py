from pydantic import BaseModel

class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: int
    bot_reply: str