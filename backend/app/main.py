"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import get_settings
from .database import init_db, close_db
from .utils.logging import setup_logging
from .utils.encryption import get_encryption_service
from .middleware.isolation import RequestIsolationMiddleware
from .api import api_router

# Get settings
settings = get_settings()

# Setup logging
setup_logging(level=settings.LOG_LEVEL, format_type=settings.LOG_FORMAT)

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise LLM Deployment Platform with Security and Privacy",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiting
if settings.RATE_LIMIT_ENABLED:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestIsolationMiddleware)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    # Initialize database
    await init_db()
    
    # Initialize encryption service
    get_encryption_service(settings.ENCRYPTION_KEY)
    
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🔒 Security: JWT + API Keys, Encryption enabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await close_db()
    print(f"👋 {settings.APP_NAME} shut down")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


# Rate limiting examples (if enabled)
if settings.RATE_LIMIT_ENABLED:
    @app.get("/rate-limited")
    @limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
    async def rate_limited_endpoint():
        """Example rate-limited endpoint"""
        return {"message": "This endpoint is rate limited"}

