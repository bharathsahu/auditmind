import io
import csv
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models.database import get_db, Audit, Finding, Remediation, MemoryNode, User
from app.services.auth_service import get_current_user, require_roles
from app.services.audit_log_service import audit_log_service

router = APIRouter(prefix="/api/reports", tags=["Reports & Executive Exports"])

@router.get("/summary")
def get_executive_summary_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve executive compliance dashboard metrics."""
    org_id = current_user.organization_id
    
    audits_query = db.query(Audit)
    findings_query = db.query(Finding)
    remediations_query = db.query(Remediation)
    
    if org_id:
        audits_query = audits_query.filter(Audit.organization_id == org_id)
        findings_query = findings_query.filter(Finding.organization_id == org_id)
        remediations_query = remediations_query.filter(Remediation.organization_id == org_id)

    audits = audits_query.all()
    findings = findings_query.all()
    remediations = remediations_query.all()

    open_findings = [f for f in findings if f.status != "Resolved"]
    resolved_findings = [f for f in findings if f.status == "Resolved"]
    high_risk_findings = [f for f in findings if f.severity in ("High", "Critical")]
    overdue_remediations = [r for r in remediations if r.status == "Overdue"]

    # Count recurring control issues
    controls_map = {}
    for f in findings:
        ctrl = f.control_involved or "Unspecified Control"
        controls_map[ctrl] = controls_map.get(ctrl, 0) + 1
    recurring_count = sum(1 for c, count in controls_map.items() if count >= 2)

    return {
        "total_audits": len(audits),
        "total_findings": len(findings),
        "open_findings": len(open_findings),
        "resolved_findings": len(resolved_findings),
        "high_risk_findings": len(high_risk_findings),
        "overdue_remediations": len(overdue_remediations),
        "recurring_control_issues": recurring_count,
        "compliance_score": round((len(resolved_findings) / len(findings) * 100), 1) if findings else 100.0
    }

@router.get("/docx")
async def generate_docx_report(
    request: Request,
    current_user: User = Depends(require_roles(["Admin", "Executive", "Lead Auditor"])),
    db: Session = Depends(get_db)
):
    """Generate professional Word .docx Executive Audit & Compliance Report."""
    org_id = current_user.organization_id
    
    audits = db.query(Audit).filter(Audit.organization_id == org_id).all() if org_id else db.query(Audit).all()
    findings = db.query(Finding).filter(Finding.organization_id == org_id).all() if org_id else db.query(Finding).all()
    remediations = db.query(Remediation).filter(Remediation.organization_id == org_id).all() if org_id else db.query(Remediation).all()
    memories = db.query(MemoryNode).filter(MemoryNode.bank_id == "auditmind_org").all()

    doc = docx.Document()

    # Title Banner
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("AuditMind Executive Compliance & Memory Report")
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(37, 99, 235)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("Internal Audit Intelligence & Hindsight Historical Memory Summary")
    sub_run.font.size = Pt(12)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(100, 116, 139)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()

    # Section 1: Executive Summary
    h1 = doc.add_heading("1. Executive Summary", level=1)
    h1.runs[0].font.color.rgb = RGBColor(30, 41, 59)

    high_risk_count = len([f for f in findings if f.severity in ('High', 'Critical')])
    summary_p = doc.add_paragraph()
    summary_p.add_run(
        f"This executive compliance report synthesizes organizational internal audit status across {len(audits)} audit scopes. "
        f"A total of {len(findings)} findings have been recorded, of which {high_risk_count} "
        f"are designated High or Critical Severity. Hindsight AI Memory layer has identified recurring control failure patterns "
        f"spanning consecutive audit cycles."
    )

    # Metrics Summary Table
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    hdr_cells = table.rows[0].cells
    headers = ["Metric Name", "Value", "Status", "Notes"]
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True

    metrics_data = [
        ("Total Audits", str(len(audits)), "Active", "2024–2026 Audit Cycles"),
        ("Active Findings", str(len([f for f in findings if f.status != 'Resolved'])), "Review Needed", "Action Items Required"),
        ("Overdue Remediations", str(len([r for r in remediations if r.status == 'Overdue'])), "High Attention", "Past Due Date"),
        ("High Risk Findings", str(high_risk_count), "Monitored", "Critical Severity Items")
    ]

    for metric, val, stat, notes in metrics_data:
        row_cells = table.add_row().cells
        row_cells[0].text = metric
        row_cells[1].text = val
        row_cells[2].text = stat
        row_cells[3].text = notes

    doc.add_paragraph()

    # Section 2: Detailed Findings
    h2 = doc.add_heading("2. Audit Findings & Remediation Tracker", level=1)
    h2.runs[0].font.color.rgb = RGBColor(30, 41, 59)

    for f in findings:
        f_p = doc.add_paragraph()
        f_run = f_p.add_run(f"[{f.finding_code}] {f.title}")
        f_run.font.bold = True
        f_run.font.size = Pt(12)

        meta_p = doc.add_paragraph()
        meta_p.add_run(f"Severity: {f.severity} | Control Involved: {f.control_involved} | Status: {f.status} | Owner: {f.remediation_owner}\n")
        meta_p.add_run(f"Description: {f.description}\n")
        meta_p.add_run(f"Root Cause: {f.root_cause}\n")
        meta_p.add_run(f"Recommendation: {f.recommendation}")
        meta_p.runs[0].font.size = Pt(10)
        meta_p.runs[0].font.color.rgb = RGBColor(71, 85, 105)

    doc.add_paragraph()

    # Section 3: Hindsight Memory Analysis
    h3 = doc.add_heading("3. Hindsight Persistent Memory Analysis", level=1)
    h3.runs[0].font.color.rgb = RGBColor(30, 41, 59)

    for m in memories:
        m_p = doc.add_paragraph(style='List Bullet')
        m_run = m_p.add_run(f"[{m.year}] ({m.category} - {m.reference_code}): {m.content}")
        m_run.font.size = Pt(10)

    stream = io.BytesIO()
    doc.save(stream)
    stream.seek(0)

    # Log Report Export in Audit Log
    audit_log_service.log(
        db=db,
        action_type="REPORT_GENERATE_DOCX",
        user=current_user,
        entity_name="ReportDOCX",
        details={"total_audits": len(audits), "total_findings": len(findings)},
        request=request
    )

    response_headers = {
        'Content-Disposition': 'attachment; filename="AuditMind_Executive_Compliance_Report.docx"'
    }
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=response_headers
    )

@router.get("/csv")
def generate_csv_report(
    request: Request,
    current_user: User = Depends(require_roles(["Admin", "Executive", "Lead Auditor", "Auditor"])),
    db: Session = Depends(get_db)
):
    """Generate CSV export of all findings and remediations."""
    org_id = current_user.organization_id
    findings = db.query(Finding).filter(Finding.organization_id == org_id).all() if org_id else db.query(Finding).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Finding Code", "Title", "Severity", "Control Involved", 
        "Status", "Root Cause", "Remediation Owner", "Due Date", "Created Date"
    ])

    for f in findings:
        writer.writerow([
            f.finding_code, f.title, f.severity, f.control_involved,
            f.status, f.root_cause, f.remediation_owner, f.due_date, f.created_date
        ])

    output.seek(0)

    audit_log_service.log(
        db=db,
        action_type="REPORT_GENERATE_CSV",
        user=current_user,
        entity_name="ReportCSV",
        details={"records_exported": len(findings)},
        request=request
    )

    response_headers = {
        'Content-Disposition': 'attachment; filename="AuditMind_Findings_Export.csv"'
    }
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers=response_headers
    )
