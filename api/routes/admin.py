#api/routes/admin.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard")
def admin_dashboard(db: Session = Depends(get_db)):
    verified_users = db.query(User).filter(User.verified == True).count()
    pending_invites = db.query(User).filter(User.verified == False).count()

    return {
        "total_users": verified_users,
        "pending_invites": pending_invites
    }
