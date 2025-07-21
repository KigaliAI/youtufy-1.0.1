#api/routes/google_oauth.py
#api/routes/google_oauth.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from backend.oauth import (
    get_google_auth_url,
    exchange_code_for_token,
    get_user_info,
    store_refresh_token,
    get_refresh_token,
    refresh_access_token
)
from jose import jwt
import os
import time

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", "3600"))
FRONTEND_REDIRECT = os.getenv("FRONTEND_REDIRECT_URL", "/youtube/subscriptions")

@router.get("/login")
def google_login():
    return RedirectResponse(get_google_auth_url(), status_code=302)

@router.get("/callback")
def google_callback(request: Request, code: str):
    try:
        print("🔐 Received code from Google:", code)

        token_data = exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        id_token = token_data.get("id_token")

        if not access_token:
            print("❌ No access token received")
            raise HTTPException(status_code=400, detail="Access token not found")

        user = get_user_info(access_token)
        email = user.get("email")
        if not email:
            print("❌ Email not found in user profile:", user)
            raise HTTPException(status_code=400, detail="Email not found in user info")

        if refresh_token:
            store_refresh_token(email, refresh_token)
        else:
            refresh_token = get_refresh_token(email)
            if not refresh_token:
                print("❌ No refresh token available for user:", email)
                raise HTTPException(status_code=400, detail="Missing refresh token for user")

        # Store Google-specific tokens in session
        request.session["user_email"] = email
        request.session["google_access_token"] = access_token
        request.session["google_refresh_token"] = refresh_token
        if id_token:
            request.session["google_id_token"] = id_token  # Optional enhancement

        # Issue your app’s stateless JWT
        payload = {
            "sub": email,
            "exp": int(time.time()) + JWT_EXP_SECONDS
        }
        jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        print(f"✅ Login successful for {email}, redirecting with JWT")

        return RedirectResponse(url=f"{FRONTEND_REDIRECT}?token={jwt_token}", status_code=302)

    except Exception as e:
        print("⚠️ OAuth callback error:", repr(e))
        raise HTTPException(status_code=500, detail="Google login failed")

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/auth/login-form.html", status_code=302)

@router.get("/refresh-token")
def refresh_token_endpoint(request: Request):
    try:
        refresh_token = request.session.get("google_refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token found")

        token_data = refresh_access_token(refresh_token)
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to refresh token")

        request.session["google_access_token"] = access_token
        return {"message": "Token refreshed successfully"}

    except Exception as e:
        print("🔁 Refresh error:", e)
        raise HTTPException(status_code=500, detail="Token refresh failed")