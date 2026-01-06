"""LLM service for inference"""
from typing import List, Dict, Any, AsyncGenerator
import httpx
from ollama import AsyncClient


class LLMService:
    """Service for LLM inference"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.client = AsyncClient(host=host)
    
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Chat with LLM
        
        Args:
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream responses
            **kwargs: Additional parameters
            
        Returns:
            Response dict or async generator for streaming
        """
        if stream:
            return self._stream_chat(model, messages, **kwargs)
        else:
            response = await self.client.chat(
                model=model,
                messages=messages,
                **kwargs
            )
            return response
    
    async def _stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat responses"""
        async for chunk in await self.client.chat(
            model=model,
            messages=messages,
            stream=True,
            **kwargs
        ):
            yield chunk
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        try:
            response = await self.client.list()
            return response.get("models", [])
        except Exception:
            return []
    
    async def health_check(self) -> bool:
        """Check if Ollama service is healthy"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.host}/api/tags", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False

