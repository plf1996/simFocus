from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from app.core.config import settings
from app.core.database import init_db
from app.core.redis import close_redis

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import API routes after logger is configured
from app.api import auth, users, api_keys, topics, characters, discussions, reports
from app.api.keycloak_auth import router as keycloak_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting simFocus backend...")
    await init_db()
    logger.info("Database initialized")

    # Initialize Keycloak service if enabled
    from app.core.keycloak_config import keycloak_config
    if keycloak_config.enabled:
        from app.services.keycloak_service import get_keycloak_service
        try:
            service = await get_keycloak_service()
            if service:
                is_healthy = await service.health_check()
                if is_healthy:
                    logger.info("Keycloak service initialized and healthy")
                else:
                    logger.warning("Keycloak service initialized but health check failed")
        except Exception as e:
            logger.error(f"Failed to initialize Keycloak service: {e}")

    yield

    # Shutdown
    logger.info("Shutting down simFocus backend...")
    await close_redis()
    logger.info("Redis connection closed")

    # Close Keycloak service
    if keycloak_config.enabled:
        from app.services.keycloak_service import close_keycloak_service
        await close_keycloak_service()
        logger.info("Keycloak service closed")


# Create FastAPI app
app = FastAPI(
    title="simFocus API",
    description="AI Virtual Focus Group Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(api_keys.router)
app.include_router(topics.router)
app.include_router(characters.router)
app.include_router(discussions.router)
app.include_router(reports.router)
app.include_router(keycloak_router)  # Keycloak SSO routes


# Root endpoint
@app.get("/")
async def root():
    """API health check"""
    return {
        "name": "simFocus API",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "request_id": request.headers.get("X-Request-ID", "unknown"),
                "timestamp": None
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "SERVER_001",
                "message": "Internal server error" if settings.ENVIRONMENT == "production" else str(exc),
                "request_id": request.headers.get("X-Request-ID", "unknown"),
                "timestamp": None
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
