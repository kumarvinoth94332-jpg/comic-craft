"""
app/main.py - ComicCraft FastAPI Application Entry Point.
Initializes the application, mounts static assets, and configures routes.
"""

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.routes import router

settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"
CSS_DIR = STATIC_DIR / "css"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure all static directories exist
STATIC_DIR.mkdir(parents=True, exist_ok=True)
PANELS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
CSS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    description="Turn your imagination into a complete 5-panel comic with Google Gemini & AI image generation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)

# Include routes
app.include_router(router)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": "The requested comic page was not found.",
        },
        status_code=404,
    )


@app.on_event("startup")
async def startup_event():
    print("=" * 65)
    print(f"  {settings.app_name}")
    print(f"  Running at : http://{settings.host}:{settings.port}")
    print(f"  Docs API   : http://{settings.host}:{settings.port}/docs")
    print("=" * 65)