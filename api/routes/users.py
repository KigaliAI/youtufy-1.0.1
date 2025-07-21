#api/routes/users.py
from fastapi import APIRouter, HTTPException, Depends, Form
from pydantic import EmailStr
from sqlalchemy.orm import Session
from backend.auth import get_password_hash
from backend.database import SessionLocal
from backend.models import User
from datetime import datetime

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register_user(
    email: EmailStr = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=email,
        username=email.split("@")[0],
        hashed_password=get_password_hash(password),
        verified=True,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Registration successful"}
