from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db, Audit
from app.models.schemas import AuditCreate, AuditResponse
from app.hindsight.client import hindsight_service

router = APIRouter(prefix="/api/audits", tags=["Audits"])

@router.get("", response_model=List[AuditResponse])
def get_audits(db: Session = Depends(get_db)):
    audits = db.query(Audit).order_by(Audit.id.desc()).all()
    return audits

@router.get("/{audit_id}", response_model=AuditResponse)
def get_audit(audit_id: int, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit

@router.post("", response_model=AuditResponse)
async def create_audit(audit_data: AuditCreate, db: Session = Depends(get_db)):
    count = db.query(Audit).count() + 1
    audit_code = f"AUD-2026-{count:03d}"
    
    audit = Audit(
        audit_code=audit_code,
        name=audit_data.name,
        department=audit_data.department,
        audit_type=audit_data.audit_type,
        risk_level=audit_data.risk_level,
        status=audit_data.status,
        start_date=audit_data.start_date,
        end_date=audit_data.end_date,
        auditor=audit_data.auditor,
        description=audit_data.description
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    # Automatically retain audit creation in Hindsight memory
    await hindsight_service.retain(
        db=db,
        content=f"Audit Created: {audit.name} ({audit.audit_code}) in {audit.department} department. Risk: {audit.risk_level}. Auditor: {audit.auditor}.",
        category="Audit History",
        reference_type="Audit",
        reference_code=audit.audit_code,
        tags=["audit_creation", audit.department.lower(), audit.risk_level.lower()],
        year=2026
    )

    return audit

@router.put("/{audit_id}", response_model=AuditResponse)
def update_audit(audit_id: int, audit_data: AuditCreate, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    audit.name = audit_data.name
    audit.department = audit_data.department
    audit.audit_type = audit_data.audit_type
    audit.risk_level = audit_data.risk_level
    audit.status = audit_data.status
    audit.start_date = audit_data.start_date
    audit.end_date = audit_data.end_date
    audit.auditor = audit_data.auditor
    audit.description = audit_data.description

    db.commit()
    db.refresh(audit)
    return audit
