#api/routes/reset.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from utils.emailer import send_email
from utils.tokens import generate_token
from backend.database import SessionLocal
from backend.models import User
import os

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")

class ResetRequest(BaseModel):
    email: EmailStr

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/reset-password")
def request_password_reset(req: ResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()

    # Optional: always return success to avoid leaking user existence
    if not user:
        print(f"🔍 Password reset requested for non-existing user: {req.email}")
        return {"message": "If this email is registered, a reset link has been sent."}

    token = generate_token(req.email)
    reset_link = f"{FRONTEND_URL}/auth/verify-token.html?token={token}"

    send_email(
        to_email=req.email,
        subject="YouTufy Password Reset",
        content=f"Click to reset your password: <a href='{reset_link}'>Reset Password</a>"
    )

    return {"message": "If this email is registered, a reset link has been sent."}
