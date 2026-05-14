from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    conversation_id: int
    message: str
    intent: str


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    intent: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetailResponse(ConversationResponse):
    messages: list[MessageResponse] = []
