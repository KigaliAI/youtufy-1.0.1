#main.py
import os
from dotenv import load_dotenv
# Load environment variables before anything else
load_dotenv(dotenv_path="/app/.env")  

import uvicorn
import secrets
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
logging.basicConfig(level=logging.DEBUG)

# DB tables are created on startup
from backend.database import create_tables
create_tables()

# Determine environment
ENV = os.getenv("ENV", "development")

# Initialize FastAPI
app = FastAPI(title="YouTufy API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")

# Load or generate secret key
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session_id",
    max_age=86400,
    same_site="Strict" if ENV == "production" else "Lax",
    https_only=(ENV == "production")
)

# Static files and templates
templates = Jinja2Templates(directory=os.path.abspath("templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join("static", "favicon.ico"))

# Import and register routes
from api.routes import auth, users, youtube, google_oauth, reset, verify, admin

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(youtube.router, prefix="/youtube", tags=["YouTube"])
app.include_router(google_oauth.router, prefix="/oauth", tags=["Google OAuth"])
app.include_router(reset.router, prefix="/auth", tags=["Reset"])
app.include_router(verify.router, prefix="/auth", tags=["Verify"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Welcome to YouTufy API",
        "description": "A YouTube subscription manager powered by FastAPI."
    })

@app.on_event("startup")
async def startup_event():
    from backend.database import create_tables
    create_tables()
    print(f"🚀 Starting YouTufy in {ENV} environment.")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
