import os
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from app.models.database import Document as DBDocument
from app.repositories.document_repository import document_repository
from app.services.document_processor import document_processor

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class DocumentService:
    def get_documents(self, db: Session, org_id: Optional[int] = None) -> List[DBDocument]:
        return document_repository.get_all(db, org_id=org_id)

    def get_document(self, db: Session, doc_id: int, org_id: Optional[int] = None) -> Optional[DBDocument]:
        return document_repository.get_by_id(db, doc_id=doc_id, org_id=org_id)

    async def upload_and_process(
        self, 
        db: Session, 
        file: UploadFile, 
        audit_id: Optional[int] = None, 
        org_id: Optional[int] = None
    ) -> Dict[str, Any]:
        filename = document_processor.sanitize_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in document_processor.allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid file type. Supported formats: PDF, DOCX, TXT, CSV")

        file_content = await file.read()
        if len(file_content) > document_processor.max_file_size:
            raise HTTPException(status_code=400, detail="File size exceeds maximum limit of 50MB")

        doc_hash = document_processor.compute_sha256(file_content)
        unique_storage_name = f"{uuid.uuid4().hex[:8]}_{filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_storage_name)

        with open(file_path, "wb") as f:
            f.write(file_content)

        doc_record = DBDocument(
            name=filename,
            file_type=ext.upper().replace(".", ""),
            file_path=file_path,
            file_size=len(file_content),
            audit_id=audit_id,
            processed=False,
            facts_extracted=0,
            document_hash=doc_hash,
            organization_id=org_id
        )
        saved_doc = document_repository.create(db, doc_record)

        # Execute semantic window chunking & retention
        processing_result = await document_processor.process_file(db, saved_doc, file_content)

        return {
            "status": "success",
            "document": saved_doc,
            "processing": processing_result
        }

document_service = DocumentService()
