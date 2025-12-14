# BOT GPT - Conversational AI Backend

A production-grade FastAPI backend for conversational AI supporting multi-turn chat, document-based Q&A (RAG), and LLM integration via Groq.

**Case Study Assignment - BOT Consulting**


## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Data Model](#data-model)
- [API Specification](#api-specification)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Design Rationale](#design-rationale)
- [Future Improvements](#future-improvements)

---

## Overview

BOT GPT is a conversational AI platform that supports:

- **Open Chat Mode**: General-purpose conversations with LLM
- **RAG Mode**: Document-grounded conversations (chat with PDFs)
- **Conversation Management**: Full CRUD operations on conversations and messages
- **LLM Integration**: Real-time integration with Groq API (Llama 3.3)
- **Document Processing**: PDF upload and text extraction for RAG

### Core Features

- Multi-turn conversations with full history tracking  
- Retrieval-Augmented Generation (RAG) over uploaded documents  
- RESTful API with automatic OpenAPI documentation  
- Token usage tracking for cost monitoring  
- Clean layered architecture (API → Service → Repository → DB)  
- 80% test coverage with mocked LLM calls  

---

## Architecture

### High-Level Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP/JSON
       ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌───────────────────────────────┐  │
│  │   API Layer (Routes)          │  │
│  │  - /conversations             │  │
│  │  - /documents                 │  │
│  │  - /health                    │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │   Service Layer               │  │
│  │  - ConversationService        │  │
│  │  - DocumentService            │  │
│  │  - LLMService (Groq)          │  │
│  │  - RAGService                 │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │   Repository Layer            │  │
│  │  - ConversationRepository     │  │
│  │  - MessageRepository          │  │
│  │  - DocumentRepository         │  │
│  └───────────┬───────────────────┘  │
│              │                       │
└──────────────┼───────────────────────┘
               │
       ┌───────▼────────┐
       │  SQLite DB     │
       │  (SQLAlchemy)  │
       └────────────────┘
               
       ┌────────────────┐
       │   Groq API     │
       │ (Llama 3.3)    │
       └────────────────┘
```

### Layer Responsibilities

| Layer | Purpose | Example |
|-------|---------|---------|
| **API (Routes)** | HTTP request/response handling | Parse JSON, validate, return status codes |
| **Service** | Business logic orchestration | Manage conversation flow, call LLM, coordinate RAG |
| **Repository** | Data access abstraction | CRUD operations on DB entities |
| **Models** | Database schema definitions | SQLAlchemy ORM models |
| **Schemas** | Request/response validation | Pydantic models for API contracts |

---

## Tech Stack

### Backend Framework
- **FastAPI 0.104+** - Modern async web framework with automatic API docs
- **Uvicorn** - ASGI server for production deployment

### Database & ORM
- **SQLAlchemy 2.0+** - Python ORM for database operations
- **SQLite** - File-based database (easily portable to PostgreSQL)

### Data Validation
- **Pydantic 2.0+** - Request/response validation and settings management
- **Pydantic Settings** - Environment configuration

### LLM Integration
- **Groq 0.4+** - Fast LLM inference API (Llama 3.3-70b-versatile)

### Document Processing
- **PyPDF2 3.0+** - PDF text extraction
- **python-multipart** - File upload handling

### Testing
- **pytest** - Unit testing framework
- **pytest-cov** - Coverage reporting

### Why This Stack?

**FastAPI**: Chosen for its async support, automatic OpenAPI docs, and type safety via Pydantic.

**SQLite**: Simple file-based DB for easy setup and portability. Architecture supports easy migration to PostgreSQL by changing `DATABASE_URL`.

**Groq**: Free-tier LLM API with fast inference. Service layer abstraction allows easy swap to OpenAI/Claude.

**SQLAlchemy**: Industry-standard ORM with excellent relationship management and migration support.

---

## Data Model

### Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│    User     │         │  Conversation    │         │  Document   │
├─────────────┤         ├──────────────────┤         ├─────────────┤
│ id (PK)     │────┐    │ id (PK)          │    ┌────│ id (PK)     │
│ email       │    │    │ user_id (FK)     │◄───┘    │ filename    │
│ name        │    └───►│ document_id (FK) │         │ content     │
│ created_at  │         │ mode             │         │ created_at  │
└─────────────┘         │ title            │         └─────────────┘
                        │ created_at       │
                        │ updated_at       │
                        │ total_tokens     │
                        └────────┬─────────┘
                                 │
                                 │ 1:N
                                 ▼
                        ┌──────────────────┐
                        │    Message       │
                        ├──────────────────┤
                        │ id (PK)          │
                        │ conversation_id  │
                        │ role (enum)      │
                        │ content          │
                        │ tokens           │
                        │ created_at       │
                        └──────────────────┘
```

### Schema Details

#### User
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE,
    name VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Conversation
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    document_id INTEGER REFERENCES documents(id),
    mode VARCHAR CHECK(mode IN ('open_chat', 'rag')),
    title VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_tokens INTEGER DEFAULT 0
);
```

#### Message
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Document
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename VARCHAR NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Key Design Decisions

- **Cascade Delete**: Messages are automatically deleted when a conversation is deleted
- **Ordering**: Messages ordered by `created_at` to maintain conversation flow
- **Token Tracking**: Both message-level and conversation-level token counts for cost monitoring
- **Mode Enum**: Explicit conversation modes (`open_chat` vs `rag`) for different workflows

---

## API Specification

Base URL: `http://localhost:8000`

### Health Check

#### `GET /`
Check if the API is running.

**Response**: `200 OK`
```json
{
  "status": "ok"
}
```

---

### Conversations

#### `POST /conversations`
Create a new conversation with the first message.

**Request Body**:
```json
{
  "first_message": "Hello, how can you help me?",
  "mode": "open_chat",
  "document_id": null
}
```

**Response**: `201 Created`
```json
{
  "conversation_id": 1,
  "reply": "Hello! I'm an AI assistant. I can help you with..."
}
```

---

#### `GET /conversations`
List all conversations for the current user.

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "mode": "open_chat",
    "created_at": "2025-12-14T08:00:00",
    "message_count": 4
  },
  {
    "id": 2,
    "mode": "rag",
    "created_at": "2025-12-14T09:00:00",
    "message_count": 6
  }
]
```

---

#### `GET /conversations/{conversation_id}`
Get a single conversation with full message history.

**Response**: `200 OK`
```json
{
  "id": 1,
  "mode": "open_chat",
  "created_at": "2025-12-14T08:00:00",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Hello, how can you help me?",
      "created_at": "2025-12-14T08:00:01"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Hello! I'm an AI assistant...",
      "created_at": "2025-12-14T08:00:02"
    }
  ]
}
```

**Error**: `404 Not Found` if conversation doesn't exist

---

#### `POST /conversations/{conversation_id}/messages`
Continue a conversation by adding a new message.

**Request Body**:
```json
{
  "content": "Tell me more about that."
}
```

**Response**: `200 OK`
```json
{
  "message_id": 3,
  "reply": "Of course! Let me elaborate..."
}
```

---

#### `DELETE /conversations/{conversation_id}`
Delete a conversation and all its messages.

**Response**: `204 No Content`

**Error**: `404 Not Found` if conversation doesn't exist

---

#### `POST /conversations/{conversation_id}/rag`
Ask a question grounded in an uploaded document (RAG mode).

**Request Body**:
```json
{
  "content": "What are the main points in the document?",
  "document_text": "Full text of the document..."
}
```

**Response**: `200 OK`
```json
{
  "reply": "Based on the document, the main points are...",
  "sources": [
    "chunk 1 text...",
    "chunk 2 text...",
    "chunk 3 text..."
  ]
}
```

---

### Documents

#### `POST /documents/upload`
Upload a PDF document for RAG processing.

**Request**: `multipart/form-data`
- `file`: PDF file

**Response**: `200 OK`
```json
{
  "document_id": 1,
  "filename": "example.pdf"
}
```

**Error**: `400 Bad Request` if file is not a PDF

---

## Setup & Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Groq API key (get free at [console.groq.com](https://console.groq.com))

### Installation Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd bot-gpt-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**

Windows (PowerShell):
```powershell
venv\Scripts\Activate.ps1
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables**

Create a `.env` file in the project root:
```env
DATABASE_URL=sqlite:///./bot_gpt.db
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
LLM_MAX_TOKENS=1024
```

6. **Initialize the database**
```bash
python init_db.py
```

---

## Running the Application

### Start the server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Using the Interactive Docs

1. Open http://localhost:8000/docs in your browser
2. Try the endpoints:
   - `POST /conversations` to start a chat
   - `POST /conversations/{id}/messages` to continue
   - `GET /conversations/{id}` to view history
   - `DELETE /conversations/{id}` to delete

---

## Testing

### Run all tests

```bash
pytest
```

### Run with coverage report

```bash
pytest --cov=app --cov-report=term-missing
```

### Current Test Coverage

**Overall: 80%**

- Health endpoint: 100%
- Conversation CRUD flow: Complete
- RAG service logic: 100%
- All models and schemas: 100%

### Test Structure

```
tests/
├── test_health.py              # Health endpoint test
├── test_conversations_flow.py  # Conversation CRUD tests (3 tests)
└── test_rag_service.py         # RAG chunking/retrieval tests (3 tests)
```

Tests use mocking for LLM service to avoid external API calls and ensure fast, reliable execution.

---

## Design Rationale

### Architecture Decisions

#### Layered Architecture
**Why**: Separation of concerns makes the codebase:
- Easier to test (can test service logic without HTTP)
- Easier to maintain (changes to DB don't affect API contracts)
- Easier to scale (can add caching, queues at service layer)

#### Repository Pattern
**Why**: Abstracts data access from business logic
- Services don't know SQL details
- Easy to swap DB implementations
- Cleaner testing with mock repositories

#### Service Layer for LLM
**Why**: Encapsulates LLM provider details
- Can swap Groq → OpenAI by changing one class
- Consistent interface for conversation service
- Easy to add retry logic, fallbacks, caching

---

### Context & Cost Management

#### Current Implementation
- Full conversation history sent to LLM on each turn
- Token usage tracked per message
- `total_tokens` field on Conversation for aggregate tracking

#### Production Improvements
1. **Sliding Window**: Only send last N messages to LLM
2. **Summarization**: Periodically summarize old messages
3. **Token Limits**: Reject conversations exceeding a threshold
4. **Caching**: Cache responses for identical prompts

**Example Sliding Window**:
```python
# Instead of sending all messages
messages_history = messages[-10:]  # Last 10 messages only
```

---

### RAG Strategy

#### Current Implementation
**Simple keyword-based retrieval**:
1. Chunk document into ~500 char pieces
2. Score chunks by keyword overlap with query
3. Send top 3 chunks as context to LLM

**Why this approach**:
- No vector DB required (faster prototype)
- Deterministic and explainable
- Works well for keyword-heavy queries

#### Production Improvements
1. **Semantic Search**: Use embeddings + vector DB (Pinecone, Chroma)
2. **Hybrid Retrieval**: Combine keyword + semantic
3. **Re-ranking**: Score retrieved chunks with cross-encoder
4. **Metadata Filtering**: Filter by document type, date, etc.

---

### Error Handling

#### Current Strategy
- **LLM failures**: Raise exception with clear message
- **DB errors**: Let SQLAlchemy handle (rollback on error)
- **Validation**: Pydantic raises 422 for invalid inputs
- **Not found**: 404 with descriptive message

#### Production Improvements
1. **Retry Logic**: Exponential backoff for LLM API calls
2. **Circuit Breaker**: Stop calling failing LLM after N failures
3. **Graceful Degradation**: Return cached/default response on error
4. **Logging**: Structured logging (JSON) for error tracking

---

### Scalability Considerations

#### Current Bottlenecks at Scale

| Component | Bottleneck | Solution |
|-----------|-----------|----------|
| **LLM API** | Rate limits, latency | Queue requests, use batch API, add caching |
| **SQLite** | Single-writer limitation | Migrate to PostgreSQL |
| **API Server** | Single uvicorn worker | Run multiple workers, use load balancer |
| **Message History** | Large conversations → memory issues | Implement sliding window, summarization |

#### Scaling Strategy

**Phase 1 (100-1K users)**:
- Multiple uvicorn workers
- PostgreSQL instead of SQLite
- Redis for caching LLM responses

**Phase 2 (1K-100K users)**:
- Async task queue (Celery/RQ) for LLM calls
- Horizontal scaling with load balancer
- Database read replicas
- CDN for static assets

**Phase 3 (100K+ users)**:
- Microservices (split LLM, RAG, API)
- Vector DB for semantic RAG
- Database sharding by user_id
- Kubernetes for orchestration

---

## Future Improvements

### Short Term
- [ ] Persist conversation summaries for long chats
- [ ] Add user authentication (JWT)
- [ ] Conversation search/filter API
- [ ] Rate limiting per user
- [ ] WebSocket support for streaming responses

### Medium Term
- [ ] Vector database for semantic RAG
- [ ] Multi-document conversations
- [ ] Export conversation as PDF/TXT
- [ ] Conversation sharing/permissions
- [ ] Analytics dashboard (token usage, popular queries)

### Long Term
- [ ] Fine-tuned models for domain-specific tasks
- [ ] Multi-modal support (images, audio)
- [ ] Agent framework (function calling, tools)
- [ ] Multi-language support
- [ ] Federated learning on user feedback

---

## License

This project is created for the BOT Consulting case study assignment.

---

## Author

**[Your Name]**  
Email: [Your Email]  
Links: [LinkedIn/GitHub]

---

## Acknowledgments

- FastAPI documentation and community
- Groq for free-tier LLM access
- SQLAlchemy team for excellent ORM
- Pydantic for making validation elegant
