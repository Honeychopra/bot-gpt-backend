"""Test conversation creation, retrieval, and deletion"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db
from app.services.llm_service import LLMService


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Ensure database tables are created once before tests.
    Uses the same SQLite database configured in .env / config.
    """
    init_db()


@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    """
    Mock LLMService.generate_response so tests don't call the real Groq API.
    """
    async def fake_generate_response(self, messages):
        # Return a fake response instead of calling Groq
        return {
            "content": "test-reply",
            "tokens": 42,
        }

    monkeypatch.setattr(LLMService, "generate_response", fake_generate_response)


client = TestClient(app)


def test_create_and_get_conversation():
    """Test creating a conversation and retrieving it"""
    # 1) Create a conversation
    payload = {
        "first_message": "Hello from test",
        "mode": "open_chat",
        "document_id": None,
    }
    response = client.post("/conversations/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "conversation_id" in data
    assert data["reply"] == "test-reply"

    conversation_id = data["conversation_id"]

    # 2) Fetch the conversation detail
    response = client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 200

    convo = response.json()
    assert convo["id"] == conversation_id
    assert convo["mode"] == "open_chat"
    assert "created_at" in convo
    assert "messages" in convo
    # Should at least contain the user message + assistant reply
    assert len(convo["messages"]) >= 2
    roles = {m["role"] for m in convo["messages"]}
    assert "user" in roles
    assert "assistant" in roles


def test_add_message_to_conversation():
    """Test continuing a conversation by adding a message"""
    # 1) Create a conversation first
    payload = {
        "first_message": "Initial message",
        "mode": "open_chat",
        "document_id": None,
    }
    response = client.post("/conversations/", json=payload)
    assert response.status_code == 201
    conversation_id = response.json()["conversation_id"]

    # 2) Add a follow-up message
    response = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"content": "Follow-up question"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message_id" in data
    assert data["reply"] == "test-reply"

    # 3) Verify the conversation now has more messages
    response = client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 200
    convo = response.json()
    # Should have: user1, assistant1, user2, assistant2 = 4 messages
    assert len(convo["messages"]) >= 4


def test_delete_conversation():
    """Test deleting a conversation"""
    # 1) Create a conversation to delete
    payload = {
        "first_message": "Conversation to delete",
        "mode": "open_chat",
        "document_id": None,
    }
    response = client.post("/conversations/", json=payload)
    assert response.status_code == 201
    conversation_id = response.json()["conversation_id"]

    # 2) Delete the conversation
    response = client.delete(f"/conversations/{conversation_id}")
    assert response.status_code == 204  # No Content

    # 3) Verify that fetching it now returns 404
    response = client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found"
