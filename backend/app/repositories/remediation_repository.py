from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import Remediation

class RemediationRepository:
    def get_all(self, db: Session, org_id: Optional[int] = None) -> List[Remediation]:
        query = db.query(Remediation)
        if org_id:
            query = query.filter(Remediation.organization_id == org_id)
        return query.order_by(Remediation.id.desc()).all()

    def get_by_id(self, db: Session, remediation_id: int, org_id: Optional[int] = None) -> Optional[Remediation]:
        query = db.query(Remediation).filter(Remediation.id == remediation_id)
        if org_id:
            query = query.filter(Remediation.organization_id == org_id)
        return query.first()

    def create(self, db: Session, remediation: Remediation) -> Remediation:
        db.add(remediation)
        db.commit()
        db.refresh(remediation)
        return remediation

    def update(self, db: Session, remediation: Remediation) -> Remediation:
        db.commit()
        db.refresh(remediation)
        return remediation

remediation_repository = RemediationRepository()
