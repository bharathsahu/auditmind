from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import Document as DBDocument

class DocumentRepository:
    def get_all(self, db: Session, org_id: Optional[int] = None) -> List[DBDocument]:
        query = db.query(DBDocument)
        if org_id:
            query = query.filter(DBDocument.organization_id == org_id)
        return query.order_by(DBDocument.id.desc()).all()

    def get_by_id(self, db: Session, doc_id: int, org_id: Optional[int] = None) -> Optional[DBDocument]:
        query = db.query(DBDocument).filter(DBDocument.id == doc_id)
        if org_id:
            query = query.filter(DBDocument.organization_id == org_id)
        return query.first()

    def get_by_hash(self, db: Session, doc_hash: str, org_id: Optional[int] = None) -> Optional[DBDocument]:
        query = db.query(DBDocument).filter(DBDocument.document_hash == doc_hash)
        if org_id:
            query = query.filter(DBDocument.organization_id == org_id)
        return query.first()

    def create(self, db: Session, doc: DBDocument) -> DBDocument:
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

document_repository = DocumentRepository()
