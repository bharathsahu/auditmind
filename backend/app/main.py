from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.database import init_db, SessionLocal
from app.demo_data import seed_demo_data
from app.api import audits, findings, remediations, documents, ai, hindsight_api, auth, reports

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Compliance & Audit Memory Agent Backend powered by Hindsight Memory Layer",
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth.router)
app.include_router(audits.router)
app.include_router(findings.router)
app.include_router(remediations.router)
app.include_router(documents.router)
app.include_router(ai.router)
app.include_router(hindsight_api.router)
app.include_router(reports.router)

@app.on_event("startup")
def startup_event():
    init_db()
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "message": "Welcome to AuditMind API - Persistent AI Memory for Internal Audit & Compliance",
        "hindsight_layer": "Active",
        "status": "online"
    }
