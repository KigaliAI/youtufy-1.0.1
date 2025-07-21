#api/routes/verify.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from utils.tokens import confirm_token
from backend.auth import get_password_hash
from backend.database import SessionLocal
from backend.models import User

router = APIRouter()

class PasswordReset(BaseModel):
    token: str
    new_password: str

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/verify-token")
def verify_token_and_reset(data: PasswordReset, db: Session = Depends(get_db)):
    email = confirm_token(data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
