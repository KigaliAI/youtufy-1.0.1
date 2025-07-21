#api/routes/oauth.py
import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


def get_google_auth_url():
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/userinfo.email",
        "access_type": "offline",
        "prompt": "consent"
    })


def exchange_code_for_token(code: str):
    res = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    })
    return res.json()


def get_user_info(access_token: str):
    response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    return response.json()


# ✅ Save refresh token to DB
def store_refresh_token(email: str, refresh_token: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.google_refresh_token = refresh_token
            db.commit()
            print(f"✅ Refresh token saved for {email}")
        else:
            print(f"❌ No user found with email: {email}")
    except Exception as e:
        print(f"⚠️ Error saving refresh token for {email}: {e}")
    finally:
        db.close()

# ✅ Get refresh token from DB
def get_refresh_token(email: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        return user.google_refresh_token if user else None
    finally:
        db.close()


# ✅ Refresh access token using refresh_token
def refresh_access_token(refresh_token: str):
    res = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    })
    return res.json()
