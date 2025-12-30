"""Inference API routes"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from ..database import get_db
from ..models.user import User
from ..auth.security import get_current_active_user, verify_api_key
from ..services.llm_service import LLMService

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message schema"""
    role: str = Field(..., description="Role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat completion request"""
    messages: List[ChatMessage]
    model: str = Field(..., description="Model name")
    deployment_id: Optional[int] = Field(None, description="Specific deployment to use")
    think: bool = Field(False, description="Enable thinking mode")
    stream: bool = Field(False, description="Enable streaming")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, gt=0)


class ChatResponse(BaseModel):
    """Chat completion response"""
    content: str
    model: str
    deployment_id: int
    metrics: Dict[str, any] = {}


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform chat completion
    
    Supports both JWT token and API key authentication
    """
    llm_service = LLMService(db)
    
    # Convert messages to dict format
    messages = [msg.dict() for msg in request.messages]
    
    # Additional options
    options = {}
    if request.temperature is not None:
        options['temperature'] = request.temperature
    if request.max_tokens is not None:
        options['num_predict'] = request.max_tokens
    
    try:
        response = await llm_service.chat_completion(
            messages=messages,
            model=request.model,
            user=current_user,
            deployment_id=request.deployment_id,
            think=request.think,
            stream=False,
            **options
        )
        
        # Extract deployment info
        deployment = await llm_service.get_deployment(request.deployment_id)
        
        return ChatResponse(
            content=response.message.content,
            model=request.model,
            deployment_id=deployment.id,
            metrics={
                "prompt_eval_count": getattr(response, 'prompt_eval_count', None),
                "eval_count": getattr(response, 'eval_count', None),
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")


@router.post("/chat/stream")
async def chat_completion_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform streaming chat completion
    
    Returns Server-Sent Events (SSE) stream
    """
    llm_service = LLMService(db)
    
    # Convert messages to dict format
    messages = [msg.dict() for msg in request.messages]
    
    # Additional options
    options = {}
    if request.temperature is not None:
        options['temperature'] = request.temperature
    if request.max_tokens is not None:
        options['num_predict'] = request.max_tokens
    
    async def generate():
        try:
            async for chunk in llm_service.chat_completion_stream(
                messages=messages,
                model=request.model,
                user=current_user,
                deployment_id=request.deployment_id,
                think=request.think,
                **options
            ):
                yield f"data: {chunk}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/models")
async def list_models(
    deployment_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List available models on a deployment"""
    llm_service = LLMService(db)
    
    try:
        models = await llm_service.list_models(deployment_id)
        return {"models": models}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


# Alternative endpoint with API key authentication
@router.post("/chat/api-key", response_model=ChatResponse)
async def chat_completion_api_key(
    request: ChatRequest,
    current_user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform chat completion using API key authentication
    """
    # Reuse the main chat completion logic
    return await chat_completion(request, current_user, db)

