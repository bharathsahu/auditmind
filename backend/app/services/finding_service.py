from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.database import Finding, Remediation
from app.models.schemas import FindingCreate
from app.repositories.finding_repository import finding_repository
from app.repositories.remediation_repository import remediation_repository
from app.hindsight.client import hindsight_service

class FindingService:
    def get_findings(self, db: Session, org_id: Optional[int] = None) -> List[Finding]:
        return finding_repository.get_all(db, org_id=org_id)

    def get_finding(self, db: Session, finding_id: int, org_id: Optional[int] = None) -> Optional[Finding]:
        return finding_repository.get_by_id(db, finding_id=finding_id, org_id=org_id)

    async def create_finding(self, db: Session, data: FindingCreate, org_id: Optional[int] = None) -> Finding:
        count = finding_repository.get_count(db, org_id=org_id) + 1
        finding_code = f"FND-2026-{count:03d}"

        finding = Finding(
            finding_code=finding_code,
            audit_id=data.audit_id,
            title=data.title,
            description=data.description,
            severity=data.severity,
            control_involved=data.control_involved,
            root_cause=data.root_cause,
            business_impact=data.business_impact,
            recommendation=data.recommendation,
            management_response=data.management_response,
            remediation_owner=data.remediation_owner,
            due_date=data.due_date,
            status=data.status,
            evidence=data.evidence,
            created_date=data.created_date,
            fiscal_year=2026,
            organization_id=org_id
        )
        saved_finding = finding_repository.create(db, finding)

        # Create initial Remediation record
        remediation = Remediation(
            finding_id=saved_finding.id,
            action=data.recommendation,
            owner=data.remediation_owner,
            status="Pending",
            due_date=data.due_date,
            evidence=data.evidence,
            comments="Initial remediation logged upon finding creation.",
            organization_id=org_id
        )
        remediation_repository.create(db, remediation)

        # Retain memory node in Hindsight
        await hindsight_service.retain(
            db=db,
            content=f"Finding {saved_finding.finding_code}: {saved_finding.title}. Severity: {saved_finding.severity}. Control Involved: {saved_finding.control_involved}. Root Cause: {saved_finding.root_cause}. Remediation Owner: {saved_finding.remediation_owner}.",
            category="Finding History",
            reference_type="Finding",
            reference_code=saved_finding.finding_code,
            tags=["finding", saved_finding.severity.lower(), saved_finding.control_involved.lower()],
            year=2026
        )

        return saved_finding

    async def find_similar_findings(self, db: Session, finding_id: int, bank_id: Optional[str] = "auditmind_org", org_id: Optional[int] = None) -> Dict[str, Any]:
        finding = finding_repository.get_by_id(db, finding_id=finding_id, org_id=org_id)
        if not finding:
            return None

        query_str = f"{finding.title} {finding.control_involved} {finding.root_cause}"
        memories = await hindsight_service.recall(db, query_str, limit=5, bank_id=bank_id)

        # Exclude self reference
        relevant_memories = [m for m in memories if m.get("reference_code") != finding.finding_code]

        explanation = f"Analyzed finding **{finding.finding_code} ({finding.title})** against historical organizational memory in Hindsight.\n\n"
        if relevant_memories:
            explanation += f"Found **{len(relevant_memories)} relevant historical findings/memories**:"
        else:
            explanation += "No prior identical findings were found in Hindsight memory."

        return {
            "finding_id": finding.id,
            "finding_code": finding.finding_code,
            "title": finding.title,
            "control_involved": finding.control_involved,
            "similar_memories": relevant_memories,
            "relevance_explanation": explanation
        }

    def get_recurring_findings(self, db: Session, org_id: Optional[int] = None) -> Dict[str, Any]:
        findings = finding_repository.get_all(db, org_id=org_id)
        controls_map: Dict[str, List[Finding]] = {}
        
        for f in findings:
            ctrl = f.control_involved or "Unspecified Control"
            if ctrl not in controls_map:
                controls_map[ctrl] = []
            controls_map[ctrl].append(f)

        recurring_issues = []
        for ctrl, items in controls_map.items():
            if len(items) >= 2:
                occurrences = []
                for item in items:
                    audit_name = item.audit.name if item.audit else "Historical Audit"
                    year = str(item.fiscal_year) if item.fiscal_year else (item.created_date.split("-")[0] if item.created_date else "N/A")
                    occurrences.append({
                        "finding_code": item.finding_code,
                        "audit_name": audit_name,
                        "year": year,
                        "title": item.title,
                        "severity": item.severity,
                        "status": item.status
                    })

                recurring_issues.append({
                    "control_involved": ctrl,
                    "count": len(items),
                    "pattern": f"Similar control weakness detected across {len(items)} audit cycles.",
                    "occurrences": sorted(occurrences, key=lambda x: x["year"])
                })

        return {
            "total_recurring_patterns": len(recurring_issues),
            "recurring_issues": recurring_issues
        }

finding_service = FindingService()
