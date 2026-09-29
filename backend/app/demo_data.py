from sqlalchemy.orm import Session
from app.models.database import Audit, Finding, Remediation, Document, MemoryNode, User
from app.hindsight.client import hindsight_service
import asyncio

def seed_demo_data(db: Session):
    """Seed fictional demo data for 2024, 2025, and 2026 showing recurring control issues."""
    # Check if data already exists
    if db.query(Audit).first():
        return

    print("Seeding AuditMind demo data...")

    # 1. Create Default User
    default_user = User(
        username="auditor",
        email="auditor@auditmind.io",
        full_name="Lead Internal Auditor",
        hashed_password="hashed_password_demo",
        role="Lead Auditor"
    )
    db.add(default_user)

    # 2. Create Audits
    audit1 = Audit(
        audit_code="AUD-2024-012",
        name="Finance Controls Audit 2024",
        department="Finance Controls",
        audit_type="Business Audit",
        risk_level="High",
        status="Completed",
        start_date="2024-03-01",
        end_date="2024-04-15",
        auditor="Sarah Jenkins",
        description="Annual comprehensive review of internal financial transaction authorization controls and delegation of authority matrices."
    )
    
    audit2 = Audit(
        audit_code="AUD-2025-024",
        name="Finance Controls Audit 2025",
        department="Finance Controls",
        audit_type="Business Audit",
        risk_level="High",
        status="Completed",
        start_date="2025-03-10",
        end_date="2025-04-20",
        auditor="Marcus Vance",
        description="Follow-up review of financial transaction sign-offs, high-value transfer controls, and secondary supervisor verifications."
    )

    audit3 = Audit(
        audit_code="AUD-2026-031",
        name="Finance Controls Audit 2026",
        department="Finance Controls",
        audit_type="Business Audit",
        risk_level="High",
        status="In Progress",
        start_date="2026-02-01",
        end_date="2026-04-30",
        auditor="Sarah Jenkins",
        description="Current period evaluation of transaction authorization compliance, automated ERP approval workflows, and audit trail verification."
    )

    audit4 = Audit(
        audit_code="AUD-2026-042",
        name="Fixed Income Trading Desk Audit",
        department="Global Markets",
        audit_type="Business Audit",
        risk_level="High",
        status="Completed",
        start_date="2026-01-15",
        end_date="2026-03-01",
        auditor="Elena Rostova",
        description="Review of trading limits, order sign-offs, and compliance with front-to-back risk management guidelines."
    )

    audit5 = Audit(
        audit_code="AUD-2026-055",
        name="Cloud Infrastructure & IAM Review",
        department="IT Risk & Security",
        audit_type="IT Audit",
        risk_level="Medium",
        status="Planned",
        start_date="2026-05-01",
        end_date="2026-06-15",
        auditor="David Chen",
        description="Assessment of AWS identity access management roles, privileged account access, and key rotation practices."
    )

    db.add_all([audit1, audit2, audit3, audit4, audit5])
    db.commit()

    # 3. Create Findings
    f1 = Finding(
        finding_code="FND-2024-012",
        audit_id=audit1.id,
        title="Missing transaction approval for high-value transfers",
        description="During sample testing of 50 wire transfers over $1M, 4 transactions lacked mandatory supervisory sign-off prior to execution.",
        severity="High",
        control_involved="Transaction Approval Control #FIN-04",
        root_cause="Manual override permitted in legacy wire system without automated hard-stop.",
        business_impact="Unapproved capital outflow risk and potential compliance violation.",
        recommendation="Implement automated mandatory dual-authorization hard stop in banking portal.",
        management_response="Agreed. Operations team will configure dual authorization by May 2024.",
        remediation_owner="Finance Controls Team",
        due_date="2024-05-30",
        status="Resolved",
        evidence="System authorization logs & dual sign-off workflow policy update.",
        created_date="2024-04-15",
        resolved_date="2024-06-01"
    )

    f2 = Finding(
        finding_code="FND-2025-024",
        audit_id=audit2.id,
        title="Incomplete approval for high-value transaction transfers",
        description="Sample testing revealed 3 high-value transactions ($2.5M+) were processed with only single-level approval due to emergency delegation overrides.",
        severity="High",
        control_involved="Transaction Approval Control #FIN-04",
        root_cause="Delegation of authority matrix allowed temporary single-approver status during peak trading hours.",
        business_impact="Failure of secondary oversight control leading to unmonitored risk exposure.",
        recommendation="Eliminate emergency single-approver delegation and enforce two-level approval workflow.",
        management_response="Management will revise emergency delegation rules immediately.",
        remediation_owner="Finance Controls Team",
        due_date="2025-06-30",
        status="Resolved",
        evidence="Updated Delegation of Authority Matrix v3.2 & workflow configuration.",
        created_date="2025-04-20",
        resolved_date="2025-07-15"
    )

    f3 = Finding(
        finding_code="FND-2026-031",
        audit_id=audit3.id,
        title="Incomplete approval documentation for high-value transaction",
        description="Audit testing identified 2 transactions exceeding $5M where secondary approval timestamps were missing from the audit log repository.",
        severity="High",
        control_involved="Transaction Approval Control #FIN-04",
        root_cause="API sync lag between ERP system and compliance audit logging service.",
        business_impact="Inability to substantiate compliance during external regulatory examinations.",
        recommendation="Deploy real-time synchronous audit log validation for secondary approvals.",
        management_response="IT and Controls team will patch the API sync service.",
        remediation_owner="Finance Controls & IT Team",
        due_date="2026-05-15",
        status="Open",
        evidence="ERP audit log excerpts & batch job error reports.",
        created_date="2026-03-01",
        resolved_date=None
    )

    f4 = Finding(
        finding_code="FND-2026-042",
        audit_id=audit4.id,
        title="Unverified trading counterparty limit overrides",
        description="Traders exceeded pre-set counterparty credit exposure limits on 5 derivative transactions without risk management committee sign-off.",
        severity="Critical",
        control_involved="Counterparty Risk Limit Control #TRD-02",
        root_cause="Trading system notification was marked non-blocking.",
        business_impact="Potential credit default exposure exceeding risk appetite threshold.",
        recommendation="Convert soft limit warnings to hard blocking controls in order management system.",
        management_response="Risk technology team is configuring hard blocking gates.",
        remediation_owner="Global Markets Risk Team",
        due_date="2026-03-31",
        status="Overdue",
        evidence="Order management trade execution receipts.",
        created_date="2026-03-01",
        resolved_date=None
    )

    f5 = Finding(
        finding_code="FND-2026-055",
        audit_id=audit5.id,
        title="Excessive privileged access permissions on production S3 buckets",
        description="24 user accounts possessed full administrative read/write access to production financial data buckets.",
        severity="Medium",
        control_involved="IAM Least Privilege Control #IT-09",
        root_cause="Legacy role definitions retained during cloud migration.",
        business_impact="Data leakage or unintended deletion risk.",
        recommendation="Conduct IAM role pruning and institute quarterly access certification.",
        management_response="SecOps will revoke unnecessary policy attachments.",
        remediation_owner="Cloud Security Team",
        due_date="2026-06-01",
        status="In Progress",
        evidence="AWS IAM Policy JSON definitions.",
        created_date="2026-03-10",
        resolved_date=None
    )

    db.add_all([f1, f2, f3, f4, f5])
    db.commit()

    # 4. Create Remediations
    r1 = Remediation(
        finding_id=f1.id,
        action="Implement dual-authorization hard stop in core banking portal",
        owner="Finance Controls Team",
        status="Resolved",
        due_date="2024-05-30",
        completion_date="2024-06-01",
        evidence="Portal v4.1 Release Notes & Dual Auth Verification Certificate",
        comments="Dual authorization successfully deployed."
    )

    r2 = Remediation(
        finding_id=f2.id,
        action="Revise Delegation of Authority matrix to require 2-level signoff for all transfers > $1M",
        owner="Finance Controls Team",
        status="Resolved",
        due_date="2025-06-30",
        completion_date="2025-07-15",
        evidence="Approved Delegation Policy v3.2",
        comments="Emergency delegation bypass removed."
    )

    r3 = Remediation(
        finding_id=f3.id,
        action="Implement two-level approval workflow synchronous audit logging",
        owner="Finance Controls Team",
        status="In Progress",
        due_date="2026-05-15",
        evidence="API Integration spec document",
        comments="Work in progress with IT team."
    )

    r4 = Remediation(
        finding_id=f4.id,
        action="Configure hard-stop counterparty credit limits in trading engine",
        owner="Global Markets Risk Team",
        status="Overdue",
        due_date="2026-03-31",
        evidence="Pending QA sign-off",
        comments="Action delayed due to trading engine maintenance window."
    )

    r5 = Remediation(
        finding_id=f5.id,
        action="Prune excessive IAM admin roles and enforce mandatory MFA",
        owner="Cloud Security Team",
        status="Pending",
        due_date="2026-06-01",
        evidence="Role audit spreadsheet",
        comments="Access review scheduled for next sprint."
    )

    db.add_all([r1, r2, r3, r4, r5])
    db.commit()

    # 5. Populate Hindsight Memory Nodes (Retain organizational audit memory)
    hindsight_memories = [
        MemoryNode(
            bank_id="auditmind_org",
            content="2024 Audit (AUD-2024-012): Finance Controls Audit 2024 identified Finding FND-2024-012. Missing transaction approval for high-value transfers. Control #FIN-04 failed. Root cause: Manual override in legacy wire system. Remediation: Implemented mandatory dual-authorization hard stop.",
            category="Finding History",
            reference_type="Finding",
            reference_code="FND-2024-012",
            tags="transaction_approval,finance_controls,high_value,2024",
            year=2024
        ),
        MemoryNode(
            bank_id="auditmind_org",
            content="2025 Audit (AUD-2025-024): Finance Controls Audit 2025 identified Finding FND-2025-024. Incomplete approval for high-value transaction transfers ($2.5M+). Control #FIN-04 failed again. Root cause: Delegation matrix allowed emergency single-approver status. Remediation: Implemented two-level approval workflow policy v3.2.",
            category="Finding History",
            reference_type="Finding",
            reference_code="FND-2025-024",
            tags="transaction_approval,finance_controls,high_value,2025,recurring",
            year=2025
        ),
        MemoryNode(
            bank_id="auditmind_org",
            content="2026 Audit (AUD-2026-031): Finance Controls Audit 2026 identified Finding FND-2026-031. Incomplete approval documentation for high-value transaction ($5M+). Control #FIN-04 failed for 3rd consecutive year. Root cause: API sync lag between ERP and audit log repository. Remediation pending dual signoff log patching.",
            category="Finding History",
            reference_type="Finding",
            reference_code="FND-2026-031",
            tags="transaction_approval,finance_controls,high_value,2026,recurring",
            year=2026
        ),
        MemoryNode(
            bank_id="auditmind_org",
            content="Historical Remediation Outcome (2024 & 2025): Earlier remediations involved instituting two-level approval workflows and dual sign-off rules. However, operational bypasses and API sync issues caused the approval-control problem to recur across 2024, 2025, and 2026.",
            category="Remediation History",
            reference_type="General",
            reference_code="REM-HIST",
            tags="remediation,approval_workflow,outcomes",
            year=2025
        ),
        MemoryNode(
            bank_id="auditmind_org",
            content="Control Failure Pattern #FIN-04: Transaction Approval Control has failed across 3 consecutive audit cycles (2024, 2025, 2026). Primary weakness is high-value transaction signoff documentation and emergency overrides.",
            category="Control History",
            reference_type="Control",
            reference_code="FIN-04",
            tags="control_weakness,recurring_issue,transaction_approval",
            year=2026
        )
    ]

    db.add_all(hindsight_memories)
    db.commit()

    print("AuditMind demo data successfully seeded!")
