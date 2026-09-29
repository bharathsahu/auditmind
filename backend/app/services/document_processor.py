import os
import io
import csv
from pypdf import PdfReader
from docx import Document as DocxDocument
from sqlalchemy.orm import Session
from app.hindsight.client import hindsight_service
from app.models.database import Document as DBDocument

class DocumentProcessorService:
    async def process_file(self, db: Session, doc_record: DBDocument, file_content: bytes) -> dict:
        """Extract text from uploaded document and store structured facts in Hindsight memory."""
        file_name = doc_record.name.lower()
        extracted_text = ""

        try:
            if file_name.endswith(".pdf"):
                reader = PdfReader(io.BytesIO(file_content))
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            elif file_name.endswith(".docx"):
                docx = DocxDocument(io.BytesIO(file_content))
                for p in docx.paragraphs:
                    if p.text:
                        extracted_text += p.text + "\n"
            elif file_name.endswith(".csv"):
                content_str = file_content.decode("utf-8", errors="ignore")
                reader = csv.reader(content_str.splitlines())
                for row in reader:
                    extracted_text += ", ".join(row) + "\n"
            else: # .txt
                extracted_text = file_content.decode("utf-8", errors="ignore")
        except Exception as e:
            extracted_text = f"Document raw text preview: {doc_record.name}"

        # Extract meaningful snippets/lines to store in Hindsight
        lines = [line.strip() for line in extracted_text.splitlines() if len(line.strip()) > 15]
        facts_retained = 0
        
        # Take key statements or chunks
        chunks = lines[:10] if len(lines) > 10 else lines
        if not chunks:
            chunks = [f"Audit document uploaded: {doc_record.name} (Type: {doc_record.file_type})"]

        for idx, chunk in enumerate(chunks):
            await hindsight_service.retain(
                db=db,
                content=f"Document '{doc_record.name}' excerpt: {chunk}",
                category="Evidence Context",
                reference_type="Document",
                reference_code=f"DOC-{doc_record.id}",
                tags=["document_upload", doc_record.file_type.lower()],
                year=2026
            )
            facts_retained += 1

        doc_record.processed = True
        doc_record.facts_extracted = facts_retained
        db.commit()

        return {
            "document_id": doc_record.id,
            "filename": doc_record.name,
            "facts_extracted": facts_retained,
            "status": "processed"
        }

document_processor = DocumentProcessorService()
