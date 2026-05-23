from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])


class UserMessage(BaseModel):
    message: str


@router.post("/send")
def send_message(body: UserMessage):
    return {
        "user_message": body.message,
        "bot_reply": "Hi"
    }