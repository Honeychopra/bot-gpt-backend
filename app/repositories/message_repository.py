"""Message repository - Data access layer"""
from sqlalchemy.orm import Session
from typing import List
from app.models.message import Message, MessageRole

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        conversation_id: int,
        role: MessageRole,
        content: str,
        tokens: int = 0
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens=tokens
        )
        self.db.add(message)
        self.db.commit()              # ✅ REQUIRED
        self.db.refresh(message)      # ✅ GOOD PRACTICE
        return message

    
    def get_by_conversation(self, conversation_id: int) -> List[Message]:
        """Get all messages for a conversation"""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
    
    def count_by_conversation(self, conversation_id: int) -> int:
        """Count messages in a conversation"""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).count()