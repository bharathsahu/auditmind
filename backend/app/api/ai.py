from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.models.database import get_db, User
from app.models.schemas import AIChatRequest
from app.agents.audit_agent import audit_agent
from app.services.auth_service import get_current_user
from app.services.audit_log_service import audit_log_service

router = APIRouter(prefix="/api/ai", tags=["AI Audit Assistant"])

@router.post("/chat")
async def ai_chat(
    payload: AIChatRequest, 
    request: Request,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """AI Audit Assistant combining live database facts, Hindsight memory recall, and grounded citations."""
    res = await audit_agent.process_user_query(
        db=db, 
        query=payload.query, 
        bank_id=payload.bank_id, 
        org_id=current_user.organization_id
    )

    # Log AI Query to Audit Log
    audit_log_service.log(
        db=db,
        action_type="AI_QUERY",
        user=current_user,
        entity_name="AIChat",
        details={"query": payload.query, "citations_count": len(res.get("citations", []))},
        request=request
    )

    return res

@router.post("/stream")
async def ai_chat_stream(
    payload: AIChatRequest, 
    request: Request,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Server-Sent Events (SSE) streaming endpoint for real-time AI response token rendering."""
    audit_log_service.log(
        db=db,
        action_type="AI_STREAM_QUERY",
        user=current_user,
        entity_name="AIChatStream",
        details={"query": payload.query},
        request=request
    )

    generator = audit_agent.stream_user_query(
        db=db, 
        query=payload.query, 
        bank_id=payload.bank_id, 
        org_id=current_user.organization_id
    )

    return StreamingResponse(generator, media_type="text/event-stream")
