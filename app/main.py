from fastapi import FastAPI
from app.api.routes import health, conversations, documents
from app.database import init_db

app = FastAPI(title="BOT GPT API", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(health.router, tags=["health"])
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
