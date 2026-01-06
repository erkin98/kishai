"""Deployment service for managing LLM deployments"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.deployment import Deployment, DeploymentType, DeploymentStatus


class DeploymentService:
    """Service for managing deployments"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(self) -> List[Deployment]:
        """Get all deployments"""
        result = await self.db.execute(select(Deployment))
        return list(result.scalars().all())
    
    async def get_by_id(self, deployment_id: int) -> Optional[Deployment]:
        """Get deployment by ID"""
        result = await self.db.execute(
            select(Deployment).where(Deployment.id == deployment_id)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        name: str,
        host: str,
        port: int,
        deployment_type: DeploymentType,
        description: Optional[str] = None,
    ) -> Deployment:
        """Create a new deployment"""
        deployment = Deployment(
            name=name,
            host=host,
            port=port,
            deployment_type=deployment_type,
            description=description,
        )
        self.db.add(deployment)
        await self.db.commit()
        await self.db.refresh(deployment)
        return deployment
    
    async def update_status(
        self, deployment_id: int, status: DeploymentStatus
    ) -> Optional[Deployment]:
        """Update deployment status"""
        deployment = await self.get_by_id(deployment_id)
        if deployment:
            deployment.status = status
            await self.db.commit()
            await self.db.refresh(deployment)
        return deployment
    
    async def delete(self, deployment_id: int) -> bool:
        """Delete a deployment"""
        deployment = await self.get_by_id(deployment_id)
        if deployment:
            await self.db.delete(deployment)
            await self.db.commit()
            return True
        return False

