"""
API v1 package

Contains all v1 API route handlers.
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.characters import router as characters_router
from app.api.v1.discussions import router as discussions_router
from app.api.v1.topics import router as topics_router
from app.api.v1.users import router as users_router

# Create main v1 router
router = APIRouter()

# Include all sub-routers
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(topics_router)
router.include_router(characters_router)
router.include_router(discussions_router)

__all__ = ["router"]
