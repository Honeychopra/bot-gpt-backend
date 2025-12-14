from sqlalchemy.orm import Session
from typing import Optional
from app.models.document import Document

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, filename: str, content: str) -> Document:
        document = Document(
            filename=filename,
            content=content
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get(self, document_id: int) -> Optional[Document]:
        return self.db.query(Document).filter(
            Document.id == document_id
        ).first()
