from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import Audit

class AuditRepository:
    def get_all(self, db: Session, org_id: Optional[int] = None) -> List[Audit]:
        query = db.query(Audit)
        if org_id:
            query = query.filter(Audit.organization_id == org_id)
        return query.order_by(Audit.id.desc()).all()

    def get_by_id(self, db: Session, audit_id: int, org_id: Optional[int] = None) -> Optional[Audit]:
        query = db.query(Audit).filter(Audit.id == audit_id)
        if org_id:
            query = query.filter(Audit.organization_id == org_id)
        return query.first()

    def get_count(self, db: Session, org_id: Optional[int] = None) -> int:
        query = db.query(Audit)
        if org_id:
            query = query.filter(Audit.organization_id == org_id)
        return query.count()

    def create(self, db: Session, audit: Audit) -> Audit:
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    def update(self, db: Session, audit: Audit) -> Audit:
        db.commit()
        db.refresh(audit)
        return audit

audit_repository = AuditRepository()
