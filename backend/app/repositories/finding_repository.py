from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import Finding

class FindingRepository:
    def get_all(self, db: Session, org_id: Optional[int] = None) -> List[Finding]:
        query = db.query(Finding)
        if org_id:
            query = query.filter(Finding.organization_id == org_id)
        return query.order_by(Finding.id.desc()).all()

    def get_by_id(self, db: Session, finding_id: int, org_id: Optional[int] = None) -> Optional[Finding]:
        query = db.query(Finding).filter(Finding.id == finding_id)
        if org_id:
            query = query.filter(Finding.organization_id == org_id)
        return query.first()

    def get_count(self, db: Session, org_id: Optional[int] = None) -> int:
        query = db.query(Finding)
        if org_id:
            query = query.filter(Finding.organization_id == org_id)
        return query.count()

    def create(self, db: Session, finding: Finding) -> Finding:
        db.add(finding)
        db.commit()
        db.refresh(finding)
        return finding

    def update(self, db: Session, finding: Finding) -> Finding:
        db.commit()
        db.refresh(finding)
        return finding

finding_repository = FindingRepository()
