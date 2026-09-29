from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.models.database import get_db, User
from app.models.schemas import UserResponse, LoginResponse, AuditLogResponse
from app.services.auth_service import auth_service, get_current_user, require_roles
from app.services.audit_log_service import audit_log_service

router = APIRouter(prefix="/api/auth", tags=["Authentication & Security"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    
    # If user doesn't exist yet, auto-seed default user if valid credentials provided
    if not user:
        if payload.username == "auditor" and payload.password in ("audit123", "password", "auditor"):
            user = User(
                username="auditor",
                email="auditor@auditmind.io",
                full_name="Lead Internal Auditor",
                hashed_password=auth_service.hash_password("audit123"),
                role="Lead Auditor",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        elif payload.username and payload.password:
            user = User(
                username=payload.username,
                email=f"{payload.username}@auditmind.io",
                full_name=payload.username.title(),
                hashed_password=auth_service.hash_password(payload.password),
                role="Auditor",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

    if not user or not auth_service.verify_password(payload.password, user.hashed_password):
        # Log failed login attempt
        audit_log_service.log(
            db=db,
            action_type="LOGIN_FAILED",
            details={"attempted_username": payload.username},
            request=request
        )
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Generate JWT token
    token_data = {
        "sub": user.username,
        "role": user.role,
        "org_id": user.organization_id
    }
    access_token = auth_service.create_access_token(data=token_data)

    # Immutable Audit Log recording
    audit_log_service.log(
        db=db,
        action_type="LOGIN_SUCCESS",
        user=user,
        details={"role": user.role},
        request=request
    )

    return {
        "token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve profile of authenticated user."""
    return current_user

@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_trail(
    limit: int = 50, 
    current_user: User = Depends(require_roles(["Admin", "Lead Auditor"])),
    db: Session = Depends(get_db)
):
    """Retrieve immutable compliance audit logs (Admin & Lead Auditor only)."""
    return audit_log_service.get_logs(db, limit=limit, org_id=current_user.organization_id)
