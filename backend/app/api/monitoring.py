"""Monitoring API routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..database import get_db
from ..models.user import User
from ..auth.security import get_current_active_user, get_current_admin_user
from ..services.monitor_service import MonitorService

router = APIRouter()


class MetricsResponse(BaseModel):
    """Metrics response schema"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    avg_latency_ms: float
    total_tokens: int
    avg_tokens_per_second: float
    start_date: str
    end_date: str


class InferenceLogResponse(BaseModel):
    """Inference log response schema"""
    id: int
    user_id: int
    deployment_id: int
    model_name: str
    status: str
    latency_ms: Optional[float]
    total_tokens: Optional[int]
    created_at: datetime
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    days: int = Query(7, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get overall metrics summary (admin only)"""
    service = MonitorService(db)
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    metrics = await service.get_metrics_summary(start_date, end_date)
    
    return metrics


@router.get("/deployments/{deployment_id}/metrics")
async def get_deployment_metrics(
    deployment_id: int,
    days: int = Query(7, ge=1, le=365),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get metrics for a specific deployment (admin only)"""
    service = MonitorService(db)
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    metrics = await service.get_deployment_metrics(deployment_id, start_date, end_date)
    
    return metrics


@router.get("/usage")
async def get_user_usage(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get usage statistics for current user"""
    service = MonitorService(db)
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    usage = await service.get_user_usage(current_user.id, start_date, end_date)
    
    return usage


@router.get("/logs", response_model=List[InferenceLogResponse])
async def get_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    deployment_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get inference logs (admin only)"""
    service = MonitorService(db)
    
    logs = await service.get_logs(
        limit=limit,
        offset=offset,
        deployment_id=deployment_id,
        status=status
    )
    
    return logs


@router.get("/my-logs", response_model=List[InferenceLogResponse])
async def get_my_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get inference logs for current user"""
    service = MonitorService(db)
    
    logs = await service.get_logs(
        limit=limit,
        offset=offset,
        user_id=current_user.id
    )
    
    return logs

