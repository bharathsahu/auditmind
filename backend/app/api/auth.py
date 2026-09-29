from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(payload: LoginRequest):
    if payload.username == "auditor" and payload.password in ("audit123", "password", "auditor"):
        return {
            "token": "demo_jwt_token_auditmind_2026",
            "user": {
                "id": 1,
                "username": "auditor",
                "full_name": "Lead Internal Auditor",
                "email": "auditor@auditmind.io",
                "role": "Lead Auditor"
            }
        }
    elif payload.username and payload.password:
        return {
            "token": f"token_{payload.username}_2026",
            "user": {
                "id": 2,
                "username": payload.username,
                "full_name": payload.username.title(),
                "email": f"{payload.username}@auditmind.io",
                "role": "Auditor"
            }
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid username or password")
