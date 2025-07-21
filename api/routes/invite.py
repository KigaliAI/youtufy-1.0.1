#api/routes/invite.py
from fastapi import APIRouter, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import secrets
from datetime import datetime, timedelta

from backend.database import SessionLocal
from backend.models import User
from backend.email_service import send_registration_email  # ✅ ensure this exists

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/invite")
async def invite_user(
    email: str = Form(...),
    username: str = Form(""),
    db: Session = Depends(get_db)
):
    try:
        token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(hours=1)

        user = db.query(User).filter(User.email == email).first()

        if user:
            user.username = username or email.split("@")[0]
            user.token = token
            user.token_expiry = expiry
            user.verified = False
        else:
            user = User(
                email=email,
                username=username or email.split("@")[0],
                token=token,
                token_expiry=expiry,
                verified=False,
                created_at=datetime.utcnow()
            )
            db.add(user)

        db.commit()

        verification_link = f"http://yourwebsite.com/verify?token={token}"
        send_registration_email(email, user.username, verification_link)

        return {"message": f"Verification email sent to {email}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
