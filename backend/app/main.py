"""
Main application file for the MFX API.
Initializes the FastAPI application and includes all versioned API routers.
"""
from fastapi import FastAPI
from .core.config import settings
from .api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A complete, professional, and multi-tenant API for Microfinance Institutions.",
    version=settings.PROJECT_VERSION,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    """Provides a simple JSON response to indicate the API is up and running."""
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}"}