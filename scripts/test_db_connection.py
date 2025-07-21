#scripts/test_db_connection.py
from backend.database import SessionLocal
from backend.models import User
from datetime import datetime

try:
    db = SessionLocal()
    user = User(
        email="tester@example.com",
        username="test",
        verified=True,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print("✅ User created:", user.email)
except Exception as e:
    print("❌ Error:", e)
finally:
    db.close()
