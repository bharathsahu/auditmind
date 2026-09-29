from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db, User
from app.models.schemas import RemediationResponse
from app.services.remediation_service import remediation_service
from app.services.auth_service import get_current_user, require_roles
from app.services.audit_log_service import audit_log_service

router = APIRouter(prefix="/api/remediations", tags=["Remediations"])

@router.get("", response_model=List[RemediationResponse])
def get_remediations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return remediation_service.get_remediations(db, org_id=current_user.organization_id)

@router.put("/{remediation_id}/status")
async def update_remediation_status(
    remediation_id: int, 
    payload: dict, 
    request: Request,
    current_user: User = Depends(require_roles(["Admin", "Lead Auditor", "Auditor"])), 
    db: Session = Depends(get_db)
):
    updated_rem = await remediation_service.update_remediation_status(db, remediation_id, payload, org_id=current_user.organization_id)
    if not updated_rem:
        raise HTTPException(status_code=404, detail="Remediation not found")

    audit_log_service.log(
        db=db,
        action_type="REMEDIATION_UPDATE",
        user=current_user,
        entity_name="Remediation",
        entity_id=str(remediation_id),
        details={"status": updated_rem.status, "action": updated_rem.action},
        request=request
    )

    return updated_rem
