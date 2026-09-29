from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import Audit
from app.models.schemas import AuditCreate
from app.repositories.audit_repository import audit_repository
from app.hindsight.client import hindsight_service

class AuditService:
    def get_audits(self, db: Session, org_id: Optional[int] = None) -> List[Audit]:
        return audit_repository.get_all(db, org_id=org_id)

    def get_audit(self, db: Session, audit_id: int, org_id: Optional[int] = None) -> Optional[Audit]:
        return audit_repository.get_by_id(db, audit_id=audit_id, org_id=org_id)

    async def create_audit(self, db: Session, audit_data: AuditCreate, org_id: Optional[int] = None) -> Audit:
        count = audit_repository.get_count(db, org_id=org_id) + 1
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
            description=audit_data.description,
            fiscal_year=2026,
            organization_id=org_id
        )
        saved_audit = audit_repository.create(db, audit)

        # Retain memory node in Hindsight
        await hindsight_service.retain(
            db=db,
            content=f"Audit Created: {saved_audit.name} ({saved_audit.audit_code}) in {saved_audit.department} department. Risk: {saved_audit.risk_level}. Auditor: {saved_audit.auditor}.",
            category="Audit History",
            reference_type="Audit",
            reference_code=saved_audit.audit_code,
            tags=["audit_creation", saved_audit.department.lower(), saved_audit.risk_level.lower()],
            year=2026
        )

        return saved_audit

    def update_audit(self, db: Session, audit_id: int, audit_data: AuditCreate, org_id: Optional[int] = None) -> Optional[Audit]:
        audit = audit_repository.get_by_id(db, audit_id=audit_id, org_id=org_id)
        if not audit:
            return None

        audit.name = audit_data.name
        audit.department = audit_data.department
        audit.audit_type = audit_data.audit_type
        audit.risk_level = audit_data.risk_level
        audit.status = audit_data.status
        audit.start_date = audit_data.start_date
        audit.end_date = audit_data.end_date
        audit.auditor = audit_data.auditor
        audit.description = audit_data.description

        return audit_repository.update(db, audit)

audit_service = AuditService()
