from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models.database import get_db, Finding, Audit, Remediation
from app.models.schemas import FindingCreate, FindingResponse, SimilarFindingsRequest
from app.hindsight.client import hindsight_service

router = APIRouter(prefix="/api/findings", tags=["Findings"])

@router.get("", response_model=List[FindingResponse])
def get_findings(db: Session = Depends(get_db)):
    findings = db.query(Finding).order_by(Finding.id.desc()).all()
    results = []
    for f in findings:
        resp = FindingResponse.model_validate(f)
        if f.audit:
            resp.audit_name = f.audit.name
        results.append(resp)
    return results

@router.get("/{finding_id}", response_model=FindingResponse)
def get_finding(finding_id: int, db: Session = Depends(get_db)):
    f = db.query(Finding).filter(Finding.id == finding_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
    resp = FindingResponse.model_validate(f)
    if f.audit:
        resp.audit_name = f.audit.name
    return resp

@router.post("", response_model=FindingResponse)
async def create_finding(data: FindingCreate, db: Session = Depends(get_db)):
    count = db.query(Finding).count() + 1
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
        created_date=data.created_date
    )
    db.add(finding)
    db.commit()
    db.refresh(finding)

    # Automatically create initial Remediation entry
    remediation = Remediation(
        finding_id=finding.id,
        action=data.recommendation,
        owner=data.remediation_owner,
        status="Pending",
        due_date=data.due_date,
        evidence=data.evidence,
        comments="Initial remediation logged upon finding creation."
    )
    db.add(remediation)
    db.commit()

    # Retain Finding in Hindsight Memory Bank
    await hindsight_service.retain(
        db=db,
        content=f"Finding {finding.finding_code}: {finding.title}. Severity: {finding.severity}. Control Involved: {finding.control_involved}. Root Cause: {finding.root_cause}. Remediation Owner: {finding.remediation_owner}.",
        category="Finding History",
        reference_type="Finding",
        reference_code=finding.finding_code,
        tags=["finding", finding.severity.lower(), finding.control_involved.lower()],
        year=2026
    )

    resp = FindingResponse.model_validate(finding)
    if finding.audit:
        resp.audit_name = finding.audit.name
    return resp

@router.post("/similar")
async def find_similar_findings(payload: SimilarFindingsRequest, db: Session = Depends(get_db)):
    """Search Hindsight memory for similar historical findings and explain why they are relevant."""
    finding = db.query(Finding).filter(Finding.id == payload.finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    query_str = f"{finding.title} {finding.control_involved} {finding.root_cause}"
    memories = await hindsight_service.recall(db, query_str, limit=5, bank_id=payload.bank_id)

    # Filter out exact self reference if any
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

@router.get("/analysis/recurring")
def get_recurring_findings(db: Session = Depends(get_db)):
    """Detect recurring control issues across audit years."""
    findings = db.query(Finding).all()
    
    # Group by control_involved
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
                year = item.created_date.split("-")[0] if item.created_date else "N/A"
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
