from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models.database import get_db, User
from app.models.schemas import FindingCreate, FindingResponse, SimilarFindingsRequest
from app.services.finding_service import finding_service
from app.services.auth_service import get_current_user, require_roles
from app.services.audit_log_service import audit_log_service

router = APIRouter(prefix="/api/findings", tags=["Findings"])

@router.get("", response_model=List[FindingResponse])
def get_findings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    findings = finding_service.get_findings(db, org_id=current_user.organization_id)
    results = []
    for f in findings:
        resp = FindingResponse.model_validate(f)
        if f.audit:
            resp.audit_name = f.audit.name
        results.append(resp)
    return results

@router.get("/{finding_id}", response_model=FindingResponse)
def get_finding(finding_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    f = finding_service.get_finding(db, finding_id, org_id=current_user.organization_id)
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
    resp = FindingResponse.model_validate(f)
    if f.audit:
        resp.audit_name = f.audit.name
    return resp

@router.post("", response_model=FindingResponse)
async def create_finding(
    data: FindingCreate, 
    request: Request,
    current_user: User = Depends(require_roles(["Admin", "Lead Auditor", "Auditor"])), 
    db: Session = Depends(get_db)
):
    finding = await finding_service.create_finding(db, data, org_id=current_user.organization_id)
    
    audit_log_service.log(
        db=db,
        action_type="FINDING_CREATE",
        user=current_user,
        entity_name="Finding",
        entity_id=finding.finding_code,
        details={"title": finding.title, "severity": finding.severity},
        request=request
    )

    resp = FindingResponse.model_validate(finding)
    if finding.audit:
        resp.audit_name = finding.audit.name
    return resp

@router.post("/similar")
async def find_similar_findings(
    payload: SimilarFindingsRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = await finding_service.find_similar_findings(db, payload.finding_id, bank_id=payload.bank_id, org_id=current_user.organization_id)
    if not result:
        raise HTTPException(status_code=404, detail="Finding not found")
    return result

@router.get("/analysis/recurring")
def get_recurring_findings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return finding_service.get_recurring_findings(db, org_id=current_user.organization_id)
