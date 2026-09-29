from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AuditBase(BaseModel):
    name: str
    department: str
    audit_type: str
    risk_level: str
    status: str
    start_date: str
    end_date: str
    auditor: str
    description: str

class AuditCreate(AuditBase):
    pass

class AuditResponse(AuditBase):
    id: int
    audit_code: str
    created_at: datetime

    class Config:
        from_attributes = True

class FindingBase(BaseModel):
    audit_id: int
    title: str
    description: str
    severity: str
    control_involved: str
    root_cause: str
    business_impact: str
    recommendation: str
    management_response: str
    remediation_owner: str
    due_date: str
    status: str
    evidence: str
    created_date: str

class FindingCreate(FindingBase):
    pass

class FindingResponse(FindingBase):
    id: int
    finding_code: str
    resolved_date: Optional[str] = None
    audit_name: Optional[str] = None

    class Config:
        from_attributes = True

class RemediationBase(BaseModel):
    finding_id: int
    action: str
    owner: str
    status: str
    due_date: str
    evidence: str
    comments: Optional[str] = None

class RemediationCreate(RemediationBase):
    pass

class RemediationResponse(RemediationBase):
    id: int
    completion_date: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class MemoryNodeResponse(BaseModel):
    id: int
    bank_id: str
    content: str
    category: str
    reference_type: str
    reference_code: Optional[str]
    tags: str
    year: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class AIChatRequest(BaseModel):
    query: str
    bank_id: Optional[str] = "auditmind_org"

class SimilarFindingsRequest(BaseModel):
    finding_id: int
    bank_id: Optional[str] = "auditmind_org"
