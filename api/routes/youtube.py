#api/routes/youtube.py
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from google.oauth2.credentials import Credentials
from backend.youtube import fetch_subscriptions
from backend.oauth import refresh_access_token, get_refresh_token
from jose import jwt, JWTError
import os
import logging

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)

# Environment Variables
SECRET_KEY = os.getenv("SECRET_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URI = "https://oauth2.googleapis.com/token"

if not SECRET_KEY:
    raise RuntimeError("❌ SECRET_KEY must be set in environment")


@router.get("/subscriptions", response_class=HTMLResponse, name="subscriptions_view")
async def subscriptions_view(request: Request, token: str = Query(None)):
    session = request.session
    email = session.get("user_email")
    access_token = session.get("google_access_token")
    refresh_token = session.get("google_refresh_token")

    # Fallback: JWT if session is missing or expired
    if (not email or not access_token or not refresh_token) and token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            email = payload.get("sub")
            refresh_token = get_refresh_token(email)

            if not refresh_token:
                raise HTTPException(status_code=401, detail="No refresh token available")

            refreshed = refresh_access_token(refresh_token)
            access_token = refreshed.get("access_token")
            if not access_token:
                raise HTTPException(status_code=401, detail="Could not refresh access token")

            # Restore session
            session["user_email"] = email
            session["google_access_token"] = access_token
            session["google_refresh_token"] = refresh_token

        except JWTError as e:
            logger.warning(f"🔐 Invalid JWT: {e}")
            raise HTTPException(status_code=401, detail="Invalid or expired token")

    if not email or not access_token or not refresh_token:
        raise HTTPException(status_code=401, detail="Session expired or missing. Please log in.")

    # Validate access token
    if not isinstance(access_token, str) or not access_token.strip():
        raise HTTPException(status_code=401, detail="Access token is invalid or missing.")

    try:
        # Construct credentials
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri=TOKEN_URI,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )

        # Fetch subscriptions
        subscriptions = fetch_subscriptions(creds, email)

        return templates.TemplateResponse("subscriptions.html", {
            "request": request,
            "subscriptions": subscriptions,
            "user_email": email
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"🚨 Subscription fetch error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch YouTube data")
