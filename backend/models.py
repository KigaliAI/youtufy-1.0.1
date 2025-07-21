#backend/models.py
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from datetime import datetime
from backend.database import Base  # 🔥 IMPORTANT: use the shared Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    verified = Column(Boolean, default=False)
    token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    google_refresh_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)



