import datetime
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.database import Remediation
from app.repositories.remediation_repository import remediation_repository
from app.repositories.finding_repository import finding_repository
from app.hindsight.client import hindsight_service

class RemediationService:
    def get_remediations(self, db: Session, org_id: Optional[int] = None) -> List[Remediation]:
        return remediation_repository.get_all(db, org_id=org_id)

    async def update_remediation_status(
        self, 
        db: Session, 
        remediation_id: int, 
        payload: dict, 
        org_id: Optional[int] = None
    ) -> Optional[Remediation]:
        rem = remediation_repository.get_by_id(db, remediation_id=remediation_id, org_id=org_id)
        if not rem:
            return None

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

        updated_rem = remediation_repository.update(db, rem)

        # Sync associated finding if status is Resolved
        finding = finding_repository.get_by_id(db, finding_id=rem.finding_id, org_id=org_id)
        if finding and new_status == "Resolved":
            finding.status = "Resolved"
            finding.resolved_date = datetime.date.today().isoformat()
            finding_repository.update(db, finding)

            # Retain remediation outcome in Hindsight
            await hindsight_service.retain(
                db=db,
                content=f"Remediation Completed for {finding.finding_code}: {rem.action}. Owner: {rem.owner}. Completion Date: {rem.completion_date}. Outcome: Resolved successfully.",
                category="Remediation History",
                reference_type="Remediation",
                reference_code=finding.finding_code,
                tags=["remediation_completed", rem.owner.lower()],
                year=2026
            )

        return updated_rem

remediation_service = RemediationService()
