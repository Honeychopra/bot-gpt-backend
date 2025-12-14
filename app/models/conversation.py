"""Conversation model"""
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class ConversationMode(str, enum.Enum):
    OPEN_CHAT = "open_chat"
    RAG = "rag"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # no FK for now
    title = Column(String, nullable=True)
    mode = Column(SQLEnum(ConversationMode), default=ConversationMode.OPEN_CHAT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_tokens = Column(Integer, default=0)
    document_id = Column(Integer, nullable=True)

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
