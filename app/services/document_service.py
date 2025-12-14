from PyPDF2 import PdfReader
from sqlalchemy.orm import Session
from app.repositories.document_repository import DocumentRepository

class DocumentService:
    def __init__(self, db: Session):
        self.repo = DocumentRepository(db)

    def upload_pdf(self, file) -> dict:
        file.file.seek(0)
        reader = PdfReader(file.file)

        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        if not text.strip():
            raise ValueError("No text could be extracted from PDF")

        document = self.repo.create(
            filename=file.filename,
            content=text
        )

        return {
            "document_id": document.id,
            "filename": document.filename
        }
