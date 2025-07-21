#api/routes/auth.py
from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta

from backend.auth import authenticate_user, create_access_token
from backend.database import get_db, SessionLocal

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/login-form.html", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("auth/login-form.html", {"request": request})


@router.post("/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        user = authenticate_user(db, email, password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token({"sub": user.email}, expires_delta=timedelta(days=1))

        request.session["user_email"] = user.email
        request.session["app_token"] = token

        print(f"🛠️ Session Data Before Redirect: {dict(request.session)}")

        redirect_url = request.url_for("subscriptions_view")
        return RedirectResponse(
            url=f"{redirect_url}?token={token}",
            status_code=302
        )

    except Exception as e:
        import traceback
        print("🔥 LOGIN ROUTE ERROR:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Login failed")

@router.get("/welcome.html", response_class=HTMLResponse)
async def welcome(request: Request):
    return templates.TemplateResponse("auth/welcome.html", {"request": request})


@router.get("/reset-password.html", response_class=HTMLResponse)
async def reset_password_form(request: Request):
    return templates.TemplateResponse("auth/reset-password.html", {"request": request})


@router.get("/register-form.html", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("auth/register-form.html", {"request": request})


@router.get("/privacy.html", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    return templates.TemplateResponse("auth/privacy.html", {"request": request})


@router.get("/terms.html", response_class=HTMLResponse)
async def terms_of_service(request: Request):
    return templates.TemplateResponse("auth/terms.html", {"request": request})


@router.get("/cookie.html", response_class=HTMLResponse)
async def cookie_policy(request: Request):
    return templates.TemplateResponse("auth/cookie.html", {"request": request})


@router.get("/logout")
async def logout_user(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login-form.html")
