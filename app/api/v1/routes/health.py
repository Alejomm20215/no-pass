"""Health check routes"""

from fastapi import APIRouter, Depends

from app.api.v1.schemas.response import HealthResponse
from app.config.settings import Settings
from app.config.dependencies import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)):
    """Health check endpoint"""
    return HealthResponse(status="healthy", version=settings.APP_VERSION)


@router.get("/", response_model=dict)
async def root(settings: Settings = Depends(get_settings)):
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
