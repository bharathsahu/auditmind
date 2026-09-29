from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.schemas import AIChatRequest
from app.agents.audit_agent import audit_agent

router = APIRouter(prefix="/api/ai", tags=["AI Audit Assistant"])

@router.post("/chat")
async def ai_chat(payload: AIChatRequest, db: Session = Depends(get_db)):
    """AI Audit Assistant combining current DB data, Hindsight historical memory, and reasoning."""
    res = await audit_agent.process_user_query(db, payload.query, bank_id=payload.bank_id)
    return res
