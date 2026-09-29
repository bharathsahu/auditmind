import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request
from app.models.database import AuditLog, User

class AuditLogService:
    def log(
        self,
        db: Session,
        action_type: str,
        user: Optional[User] = None,
        entity_name: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Create an immutable compliance audit log entry."""
        user_id = user.id if user else None
        org_id = user.organization_id if user else None
        
        ip_address = None
        if request and request.client:
            ip_address = request.client.host

        details_str = json.dumps(details) if details else None

        log_entry = AuditLog(
            user_id=user_id,
            organization_id=org_id,
            action_type=action_type,
            entity_name=entity_name,
            entity_id=str(entity_id) if entity_id else None,
            details=details_str,
            ip_address=ip_address
        )
        
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    def get_logs(self, db: Session, limit: int = 100, org_id: Optional[int] = None):
        """Retrieve recent audit logs."""
        query = db.query(AuditLog)
        if org_id:
            query = query.filter(AuditLog.organization_id == org_id)
        return query.order_by(AuditLog.id.desc()).limit(limit).all()

audit_log_service = AuditLogService()
