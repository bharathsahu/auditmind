from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import get_db, User
from app.services.document_service import document_service
from app.services.auth_service import get_current_user, require_roles
from app.services.audit_log_service import audit_log_service

router = APIRouter(prefix="/api/documents", tags=["Documents & Ingestion"])

@router.get("")
def get_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return document_service.get_documents(db, org_id=current_user.organization_id)

@router.get("/{doc_id}")
def get_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = document_service.get_document(db, doc_id, org_id=current_user.organization_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    audit_id: Optional[int] = Form(None),
    current_user: User = Depends(require_roles(["Admin", "Lead Auditor", "Auditor"])),
    db: Session = Depends(get_db)
):
    result = await document_service.upload_and_process(db, file, audit_id=audit_id, org_id=current_user.organization_id)
    
    doc = result.get("document")
    audit_log_service.log(
        db=db,
        action_type="DOCUMENT_UPLOAD",
        user=current_user,
        entity_name="Document",
        entity_id=str(doc.id) if doc else None,
        details={
            "filename": doc.name if doc else file.filename,
            "file_size": doc.file_size if doc else None,
            "document_hash": doc.document_hash if doc else None
        },
        request=request
    )

    return result
