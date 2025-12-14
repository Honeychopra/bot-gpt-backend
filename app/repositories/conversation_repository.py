"""Conversation repository - Data access layer"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.conversation import Conversation, ConversationMode
from app.models.message import Message


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        title: str = None,
        mode: ConversationMode = ConversationMode.OPEN_CHAT,
        document_id: int = None
    ) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            title=title,
            mode=mode,
            document_id=document_id
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get(self, conversation_id: int) -> Optional[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )
    
    def get_by_user(self, user_id: int) -> List[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .all()
        )
    
    def delete(self, conversation_id: int) -> bool:
        """Delete a conversation and its messages (cascade)"""
        conversation = self.get(conversation_id)
        if not conversation:
            return False
        
        self.db.delete(conversation)
        self.db.commit()
        return True
