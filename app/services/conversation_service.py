from sqlalchemy.orm import Session
from typing import Optional, List

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.llm_service import LLMService
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.rag_service import RAGService
from app.models.message import MessageRole

class ConversationService:
    def __init__(self, db: Session):
        self.db = db
        self.conversation_repo = ConversationRepository(db)
        self.message_repo = MessageRepository(db)
        self.llm_service = LLMService()
        self.rag_service = RAGService()


    async def create_conversation(
        self,
        user_id: int,
        first_message: str,
        mode,
        document_id: int = None
    ) -> dict:
        # 1. Create conversation
        conversation = self.conversation_repo.create(
            user_id=user_id,
            mode=mode,
            document_id=document_id
        )

        # 2. Save user message
        self.message_repo.create(
            conversation_id=conversation.id,
            role="user",
            content=first_message
        )

        # 3. Call LLM
        ai_response = await self.llm_service.generate_response(
            [{"role": "user", "content": first_message}]
        )

        # 4. Save AI message
        self.message_repo.create(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response["content"],
            tokens=ai_response.get("tokens", 0)
        )

        return {
            "conversation_id": conversation.id,
            "reply": ai_response["content"]
        }
    
    async def add_message(self, conversation_id: int, message: str) -> dict:
        # 1. Check conversation exists
        conversation = self.conversation_repo.get(conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")

        # 2. Load message history
        messages = self.message_repo.get_by_conversation(conversation_id)

        messages_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # 3. Add new user message
        messages_history.append({"role": "user", "content": message})

        self.message_repo.create(
            conversation_id=conversation_id,
            role="user",
            content=message
        )

        # 4. Call LLM
        ai_response = await self.llm_service.generate_response(messages_history)

        # 5. Save AI reply
        ai_message = self.message_repo.create(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response["content"],
            tokens=ai_response.get("tokens", 0)
        )

        return {
            "message_id": ai_message.id,
            "reply": ai_response["content"]
        }

    def get_conversation(self, conversation_id: int):
        conversation = self.conversation_repo.get(conversation_id)
        if not conversation:
            return None

        messages = self.message_repo.get_by_conversation(conversation_id)

        return {
            "id": conversation.id,
            "mode": conversation.mode,
            "created_at": conversation.created_at,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at
                }
                for msg in messages
            ]
        }

    def list_conversations(self, user_id: int):
        conversations = self.conversation_repo.get_by_user(user_id)

        result = []
        for convo in conversations:
            message_count = self.message_repo.count_by_conversation(convo.id)
            result.append({
                "id": convo.id,
                "mode": convo.mode,
                "created_at": convo.created_at,
                "message_count": message_count
            })

        return result

    async def add_rag_message(
        self,
        conversation_id: int,
        question: str,
        document_text: str
    ):
        # 1. Check conversation exists
        conversation = self.conversation_repo.get(conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")

        # 2. Chunk document
        chunks = self.rag_service.chunk_document(document_text)

        # 3. Retrieve relevant chunks
        relevant_chunks = self.rag_service.retrieve_relevant_chunks(
            query=question,
            chunks=chunks,
            top_k=3
        )

        context = "\n\n".join(relevant_chunks)

        # 4. Save user question
        self.message_repo.create(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=question
        )

        # 5. Build augmented prompt
        augmented_prompt = f"""
    Use the following document context to answer the question.

    Context:
    {context}

    Question:
    {question}
    """

        # 6. Call LLM
        response = await self.llm_service.generate_response([
            {"role": "user", "content": augmented_prompt}
        ])

        # 7. Save assistant reply
        self.message_repo.create(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=response["content"]
        )

        return {
            "reply": response["content"],
            "sources": relevant_chunks
        }

    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation"""
        return self.conversation_repo.delete(conversation_id)


