# utils/tokens.py
from itsdangerous import URLSafeTimedSerializer
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
SECURITY_SALT = os.getenv("SECURITY_SALT", "youtufy-token-salt")

serializer = URLSafeTimedSerializer(SECRET_KEY)

def generate_token(email: str) -> str:
    return serializer.dumps(email, salt=SECURITY_SALT)

def confirm_token(token: str, expiration: int = 3600) -> str | None:
    try:
        return serializer.loads(token, salt=SECURITY_SALT, max_age=expiration)
    except Exception:
        return None

