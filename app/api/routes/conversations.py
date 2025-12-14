from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.conversation import (
    ConversationCreate,
    MessageAdd,
    RAGMessageAdd
)
from app.services.conversation_service import ConversationService
from app.models.user import User

router = APIRouter()

def get_default_user(db: Session) -> User:
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        user = User(id=1, email="demo@example.com", name="Demo User")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db)
):
    user = get_default_user(db)
    service = ConversationService(db)

    return await service.create_conversation(
        user_id=user.id,
        first_message=request.first_message,
        mode=request.mode,
        document_id=request.document_id
    )


@router.post("/{conversation_id}/messages")
async def add_message(
    conversation_id: int,
    request: MessageAdd,
    db: Session = Depends(get_db)
):
    service = ConversationService(db)
    return await service.add_message(conversation_id, request.content)

@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    service = ConversationService(db)
    convo = service.get_conversation(conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return convo


@router.get("/")
def list_conversations(db: Session = Depends(get_db)):
    user = get_default_user(db)
    service = ConversationService(db)
    return service.list_conversations(user.id)


@router.post("/{conversation_id}/rag")
async def add_rag_message(
    conversation_id: int,
    request: RAGMessageAdd,
    db: Session = Depends(get_db)
):
    service = ConversationService(db)
    return await service.add_rag_message(
        conversation_id=conversation_id,
        question=request.content
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    service = ConversationService(db)
    if not service.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
