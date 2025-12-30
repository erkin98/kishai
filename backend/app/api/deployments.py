"""Deployments API routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..models.deployment import DeploymentType, DeploymentStatus
from ..auth.security import get_current_active_user, get_current_admin_user
from ..services.deployment_service import DeploymentService

router = APIRouter()


class DeploymentCreate(BaseModel):
    """Deployment creation schema"""
    name: str = Field(..., min_length=1, max_length=100)
    host: str = Field(..., description="Host URL")
    port: int = Field(11434, ge=1, le=65535)
    deployment_type: DeploymentType
    description: Optional[str] = Field(None, max_length=500)
    config: Optional[dict] = Field(default_factory=dict)


class DeploymentUpdate(BaseModel):
    """Deployment update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    host: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[DeploymentStatus] = None
    config: Optional[dict] = None


class DeploymentResponse(BaseModel):
    """Deployment response schema"""
    id: int
    name: str
    host: str
    port: int
    deployment_type: DeploymentType
    status: DeploymentStatus
    description: Optional[str]
    is_healthy: bool
    last_health_check: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.post("", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(
    deployment_data: DeploymentCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new deployment (admin only)"""
    service = DeploymentService(db)
    
    try:
        deployment = await service.create_deployment(
            name=deployment_data.name,
            host=deployment_data.host,
            port=deployment_data.port,
            deployment_type=deployment_data.deployment_type,
            description=deployment_data.description,
            config=deployment_data.config,
        )
        return deployment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create deployment: {str(e)}"
        )


@router.get("", response_model=List[DeploymentResponse])
async def list_deployments(
    deployment_type: Optional[DeploymentType] = None,
    status_filter: Optional[DeploymentStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all deployments"""
    service = DeploymentService(db)
    deployments = await service.list_deployments(
        deployment_type=deployment_type,
        status=status_filter
    )
    return deployments


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific deployment"""
    service = DeploymentService(db)
    deployment = await service.get_deployment(deployment_id)
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    return deployment


@router.put("/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(
    deployment_id: int,
    update_data: DeploymentUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a deployment (admin only)"""
    service = DeploymentService(db)
    
    deployment = await service.update_deployment(
        deployment_id,
        **update_data.dict(exclude_unset=True)
    )
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    return deployment


@router.delete("/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deployment(
    deployment_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a deployment (admin only)"""
    service = DeploymentService(db)
    
    success = await service.delete_deployment(deployment_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    return None


@router.get("/{deployment_id}/health")
async def check_deployment_health(
    deployment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Check health status of a deployment"""
    service = DeploymentService(db)
    
    is_healthy = await service.update_health_status(deployment_id)
    
    return {
        "deployment_id": deployment_id,
        "is_healthy": is_healthy,
        "checked_at": datetime.utcnow().isoformat()
    }

