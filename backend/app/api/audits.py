from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db, User
from app.models.schemas import AuditCreate, AuditResponse
from app.services.audit_service import audit_service
from app.services.auth_service import get_current_user, require_roles
from app.services.audit_log_service import audit_log_service

router = APIRouter(prefix="/api/audits", tags=["Audits"])

@router.get("", response_model=List[AuditResponse])
def get_audits(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return audit_service.get_audits(db, org_id=current_user.organization_id)

@router.get("/{audit_id}", response_model=AuditResponse)
def get_audit(audit_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    audit = audit_service.get_audit(db, audit_id, org_id=current_user.organization_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit

@router.post("", response_model=AuditResponse)
async def create_audit(
    audit_data: AuditCreate, 
    request: Request,
    current_user: User = Depends(require_roles(["Admin", "Lead Auditor", "Auditor"])), 
    db: Session = Depends(get_db)
):
    saved_audit = await audit_service.create_audit(db, audit_data, org_id=current_user.organization_id)
    
    # Immutable Audit Log
    audit_log_service.log(
        db=db,
        action_type="AUDIT_CREATE",
        user=current_user,
        entity_name="Audit",
        entity_id=saved_audit.audit_code,
        details={"name": saved_audit.name, "department": saved_audit.department},
        request=request
    )
    
    return saved_audit

@router.put("/{audit_id}", response_model=AuditResponse)
def update_audit(
    audit_id: int, 
    audit_data: AuditCreate, 
    request: Request,
    current_user: User = Depends(require_roles(["Admin", "Lead Auditor"])), 
    db: Session = Depends(get_db)
):
    audit = audit_service.update_audit(db, audit_id, audit_data, org_id=current_user.organization_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    audit_log_service.log(
        db=db,
        action_type="AUDIT_UPDATE",
        user=current_user,
        entity_name="Audit",
        entity_id=audit.audit_code,
        details={"name": audit.name},
        request=request
    )

    return audit
