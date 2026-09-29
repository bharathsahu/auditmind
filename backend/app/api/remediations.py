from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db, Remediation, Finding
from app.models.schemas import RemediationCreate, RemediationResponse
from app.hindsight.client import hindsight_service
import datetime

router = APIRouter(prefix="/api/remediations", tags=["Remediations"])

@router.get("", response_model=List[RemediationResponse])
def get_remediations(db: Session = Depends(get_db)):
    remediations = db.query(Remediation).order_by(Remediation.id.desc()).all()
    return remediations

@router.put("/{remediation_id}/status")
async def update_remediation_status(remediation_id: int, payload: dict, db: Session = Depends(get_db)):
    rem = db.query(Remediation).filter(Remediation.id == remediation_id).first()
    if not rem:
        raise HTTPException(status_code=404, detail="Remediation not found")

    new_status = payload.get("status")
    comments = payload.get("comments")
    evidence = payload.get("evidence")

    if new_status:
        rem.status = new_status
        if new_status == "Resolved":
            rem.completion_date = datetime.date.today().isoformat()

    if comments:
        rem.comments = comments
    if evidence:
        rem.evidence = evidence

    db.commit()
    db.refresh(rem)

    # Also update associated finding status if resolved
    finding = db.query(Finding).filter(Finding.id == rem.finding_id).first()
    if finding and new_status == "Resolved":
        finding.status = "Resolved"
        finding.resolved_date = datetime.date.today().isoformat()
        db.commit()

        # Retain Remediation Outcome in Hindsight
        await hindsight_service.retain(
            db=db,
            content=f"Remediation Completed for {finding.finding_code}: {rem.action}. Owner: {rem.owner}. Completion Date: {rem.completion_date}. Outcome: Resolved successfully.",
            category="Remediation History",
            reference_type="Remediation",
            reference_code=finding.finding_code,
            tags=["remediation_completed", rem.owner.lower()],
            year=2026
        )

    return rem
