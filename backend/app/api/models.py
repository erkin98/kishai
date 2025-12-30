"""Models API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import os
import aiofiles

from ..database import get_db
from ..models.user import User
from ..auth.security import get_current_active_user, get_current_admin_user
from ..services.model_service import ModelService
from ..config import get_settings

router = APIRouter()
settings = get_settings()


class ModelCreate(BaseModel):
    """Model creation schema"""
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    base_model: Optional[str] = Field(None, max_length=100)
    parameters: Optional[str] = Field(None, max_length=50)
    is_public: bool = False


class ModelUpdate(BaseModel):
    """Model update schema"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class ModelResponse(BaseModel):
    """Model response schema"""
    id: int
    name: str
    display_name: str
    description: Optional[str]
    base_model: Optional[str]
    parameters: Optional[str]
    is_public: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VersionCreate(BaseModel):
    """Model version creation schema"""
    version: str = Field(..., min_length=1, max_length=50)
    ollama_model_name: Optional[str] = Field(None, max_length=100)
    deployment_id: Optional[int] = None


class VersionResponse(BaseModel):
    """Model version response schema"""
    id: int
    model_id: int
    version: str
    file_path: Optional[str]
    file_size: Optional[int]
    checksum: Optional[str]
    ollama_model_name: Optional[str]
    deployment_id: Optional[int]
    is_deployed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    model_data: ModelCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new model (admin only)"""
    service = ModelService(db)
    
    # Check if model name already exists
    existing = await service.get_model_by_name(model_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model name already exists"
        )
    
    model = await service.create_model(**model_data.dict())
    return model


@router.get("", response_model=List[ModelResponse])
async def list_models(
    is_active: Optional[bool] = None,
    is_public: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all models"""
    service = ModelService(db)
    models = await service.list_models(is_active=is_active, is_public=is_public)
    return models


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific model"""
    service = ModelService(db)
    model = await service.get_model(model_id)
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return model


@router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: int,
    update_data: ModelUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a model (admin only)"""
    service = ModelService(db)
    
    model = await service.update_model(
        model_id,
        **update_data.dict(exclude_unset=True)
    )
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return model


@router.post("/{model_id}/versions", response_model=VersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    model_id: int,
    version_data: VersionCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new version for a model (admin only)"""
    service = ModelService(db)
    
    version = await service.create_version(
        model_id=model_id,
        **version_data.dict()
    )
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return version


@router.get("/{model_id}/versions", response_model=List[VersionResponse])
async def list_versions(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all versions of a model"""
    service = ModelService(db)
    
    # Verify model exists
    model = await service.get_model(model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    versions = await service.list_versions(model_id)
    return versions


@router.post("/{model_id}/upload")
async def upload_model_file(
    model_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a model file (admin only)"""
    service = ModelService(db)
    
    # Verify model exists
    model = await service.get_model(model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Create model storage directory
    os.makedirs(settings.MODEL_STORAGE_PATH, exist_ok=True)
    
    # Save file
    file_path = os.path.join(settings.MODEL_STORAGE_PATH, f"{model.name}_{file.filename}")
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    return {
        "model_id": model_id,
        "filename": file.filename,
        "file_path": file_path,
        "size": len(content)
    }

