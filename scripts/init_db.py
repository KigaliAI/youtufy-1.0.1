#scripts/init_db.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, create_tables
from backend import models  

print("🚨 Connected DB URL:", engine.url)
print("📦 Creating database tables...")

if __name__ == "__main__":
    create_tables()
    print("✅ Tables created successfully.")

