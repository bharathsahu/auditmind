import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///./auditmind.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="Auditor")

class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True, index=True)
    audit_code = Column(String, unique=True, index=True) # e.g. AUD-2026-001
    name = Column(String, index=True)
    department = Column(String)
    audit_type = Column(String) # Business Audit, IT Audit, Compliance, Financial
    risk_level = Column(String) # High, Medium, Low
    status = Column(String) # Planned, In Progress, Completed, Review
    start_date = Column(String)
    end_date = Column(String)
    auditor = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    findings = relationship("Finding", back_populates="audit", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="audit", cascade="all, delete-orphan")

class Finding(Base):
    __tablename__ = "findings"
    id = Column(Integer, primary_key=True, index=True)
    finding_code = Column(String, unique=True, index=True) # e.g. FND-001
    audit_id = Column(Integer, ForeignKey("audits.id"))
    title = Column(String, index=True)
    description = Column(Text)
    severity = Column(String) # Low, Medium, High, Critical
    control_involved = Column(String)
    root_cause = Column(Text)
    business_impact = Column(Text)
    recommendation = Column(Text)
    management_response = Column(Text)
    remediation_owner = Column(String)
    due_date = Column(String)
    status = Column(String) # Open, In Progress, Resolved, Overdue
    evidence = Column(Text)
    created_date = Column(String)
    resolved_date = Column(String, nullable=True)

    audit = relationship("Audit", back_populates="findings")
    remediations = relationship("Remediation", back_populates="finding", cascade="all, delete-orphan")

class Remediation(Base):
    __tablename__ = "remediations"
    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id"))
    action = Column(Text)
    owner = Column(String)
    status = Column(String) # Pending, In Progress, Resolved, Overdue
    due_date = Column(String)
    completion_date = Column(String, nullable=True)
    evidence = Column(Text)
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    finding = relationship("Finding", back_populates="remediations")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    file_type = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=True)
    processed = Column(Boolean, default=False)
    facts_extracted = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    audit = relationship("Audit", back_populates="documents")

class MemoryNode(Base):
    __tablename__ = "memory_nodes"
    id = Column(Integer, primary_key=True, index=True)
    bank_id = Column(String, index=True, default="auditmind_org")
    content = Column(Text)
    category = Column(String) # Audit History, Finding History, Remediation History, Control History, Evidence
    reference_type = Column(String) # Audit, Finding, Document, General
    reference_code = Column(String, nullable=True)
    tags = Column(String) # comma-separated tags
    year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
