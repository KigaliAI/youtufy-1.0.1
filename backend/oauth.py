#backend/oauth.py
import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import User

# Load .env just once, only when accessed
def get_env_variable(key: str) -> str:
    load_dotenv(dotenv_path="/app/.env")
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"❌ Missing required environment variable: {key}")
    return value


def get_google_auth_url() -> str:
    client_id = get_env_variable("CLIENT_ID")
    redirect_uri = get_env_variable("REDIRECT_URI")

    scope = [
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]

    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scope),
        "access_type": "offline",
        "prompt": "consent"
    })


def encrypt_token(token: str) -> str:
    key = get_env_variable("ENCRYPTION_KEY").encode()
    cipher = Fernet(key)
    return cipher.encrypt(token.encode()).decode()


def decrypt_token(token: str) -> str:
    key = get_env_variable("ENCRYPTION_KEY").encode()
    cipher = Fernet(key)
    return cipher.decrypt(token.encode()).decode()


def exchange_code_for_token(code: str) -> dict:
    payload = {
        "client_id": get_env_variable("CLIENT_ID"),
        "client_secret": get_env_variable("CLIENT_SECRET"),
        "code": code,
        "redirect_uri": get_env_variable("REDIRECT_URI"),
        "grant_type": "authorization_code"
    }

    print("📡 Sending token request to Google with payload:", payload)

    res = requests.post("https://oauth2.googleapis.com/token", data=payload)
    try:
        res.raise_for_status()
    except requests.HTTPError as e:
        print("❌ Token exchange failed:", e)
        print("🔍 Response body:", res.text)
        raise Exception("Google token exchange failed") from e

    print("✅ Token exchange successful:", res.json())
    return res.json()


def get_user_info(access_token: str) -> dict:
    res = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if res.status_code != 200:
        raise Exception(f"User info fetch failed: {res.text}")
    return res.json()


def store_refresh_token(email: str, refresh_token: str):
    encrypted = encrypt_token(refresh_token)
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.google_refresh_token = encrypted
            db.commit()
    finally:
        db.close()


def get_refresh_token(email: str) -> str | None:
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user and user.google_refresh_token:
            return decrypt_token(user.google_refresh_token)
        return None
    finally:
        db.close()


def refresh_access_token(refresh_token: str) -> dict:
    res = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": get_env_variable("CLIENT_ID"),
        "client_secret": get_env_variable("CLIENT_SECRET"),
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    })
    if res.status_code != 200:
        raise Exception(f"Access token refresh failed: {res.text}")
    return res.json()
