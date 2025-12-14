from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    tokens: int

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    first_message: str
    mode: str = "open_chat"
    document_id: Optional[int] = None


class MessageAdd(BaseModel):
    content: str


class ConversationResponse(BaseModel):
    id: int
    mode: str
    created_at: datetime
    messages: List[MessageResponse]


class ConversationListItem(BaseModel):
    id: int
    title: Optional[str]
    mode: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class RAGMessageAdd(BaseModel):
    content: str
    document_text: str
