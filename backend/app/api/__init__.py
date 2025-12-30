"""API routes"""
from fastapi import APIRouter
from .auth import router as auth_router
from .inference import router as inference_router
from .deployments import router as deployments_router
from .models import router as models_router
from .monitoring import router as monitoring_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(inference_router, prefix="/inference", tags=["Inference"])
api_router.include_router(deployments_router, prefix="/deployments", tags=["Deployments"])
api_router.include_router(models_router, prefix="/models", tags=["Models"])
api_router.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])

