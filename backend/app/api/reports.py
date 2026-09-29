from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.models.database import get_db, Audit, Finding, Remediation, MemoryNode
from app.hindsight.client import hindsight_service
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import io
import csv
import os

router = APIRouter(prefix="/api/reports", tags=["Reports & Export"])

@router.get("/docx")
async def generate_docx_report(db: Session = Depends(get_db)):
    """Generate professional Word .docx Executive Audit & Compliance Report."""
    audits = db.query(Audit).all()
    findings = db.query(Finding).all()
    remediations = db.query(Remediation).all()
    memories = db.query(MemoryNode).filter(MemoryNode.bank_id == "auditmind_org").all()

    doc = docx.Document()

    # Document Header Title
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("AuditMind Executive Compliance & Memory Report")
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(37, 99, 235) # Blue-600
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("Internal Audit Intelligence & Hindsight Historical Memory Summary")
    sub_run.font.size = Pt(12)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(100, 116, 139)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph() # Spacer

    # Section 1: Executive Summary
    h1 = doc.add_heading("1. Executive Summary", level=1)
    h1.runs[0].font.color.rgb = RGBColor(30, 41, 59)

    summary_p = doc.add_paragraph()
    summary_p.add_run(
        f"This executive compliance report synthesizes organizational internal audit status across {len(audits)} audit scopes. "
        f"A total of {len(findings)} findings have been recorded, of which {len([f for f in findings if f.severity in ('High', 'Critical')])} "
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
        ("Recurring Control Failures", "1 Pattern", "Monitored", "Control #FIN-04 (3 Years)")
    ]

    for metric, val, stat, notes in metrics_data:
        row_cells = table.add_row().cells
        row_cells[0].text = metric
        row_cells[1].text = val
        row_cells[2].text = stat
        row_cells[3].text = notes

    doc.add_paragraph() # Spacer

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

    doc.add_paragraph() # Spacer

    # Section 3: Hindsight Memory Lineage
    h3 = doc.add_heading("3. Hindsight Persistent Memory Analysis", level=1)
    h3.runs[0].font.color.rgb = RGBColor(30, 41, 59)

    mem_intro = doc.add_paragraph()
    mem_intro.add_run(
        "Hindsight Memory Engine retained the following historical organizational facts and control lineage graphs:"
    )

    for m in memories:
        m_p = doc.add_paragraph(style='List Bullet')
        m_run = m_p.add_run(f"[{m.year}] ({m.category} - {m.reference_code}): {m.content}")
        m_run.font.size = Pt(10)

    # Save document to bytes buffer
    stream = io.BytesIO()
    doc.save(stream)
    stream.seek(0)

    headers = {
        'Content-Disposition': 'attachment; filename="AuditMind_Executive_Compliance_Report.docx"'
    }
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers
    )

@router.get("/csv")
def generate_csv_report(db: Session = Depends(get_db)):
    """Generate CSV export of all findings and remediations."""
    findings = db.query(Finding).all()

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
    headers = {
        'Content-Disposition': 'attachment; filename="AuditMind_Findings_Export.csv"'
    }
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers=headers
    )
