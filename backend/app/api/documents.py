from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import get_db, Document as DBDocument
from app.services.document_processor import document_processor
import os
import shutil

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("")
def get_documents(db: Session = Depends(get_db)):
    docs = db.query(DBDocument).order_by(DBDocument.id.desc()).all()
    return docs

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    audit_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    allowed_extensions = (".pdf", ".docx", ".txt", ".csv")
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type. Supported formats: PDF, DOCX, TXT, CSV")

    file_path = os.path.join(UPLOAD_DIR, filename)
    file_content = await file.read()

    with open(file_path, "wb") as f:
        f.write(file_content)

    doc_record = DBDocument(
        name=filename,
        file_type=ext.upper().replace(".", ""),
        file_path=file_path,
        file_size=len(file_content),
        audit_id=audit_id,
        processed=False,
        facts_extracted=0
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # Process file text and store memories in Hindsight
    result = await document_processor.process_file(db, doc_record, file_content)

    return {
        "status": "success",
        "document": doc_record,
        "processing": result
    }
