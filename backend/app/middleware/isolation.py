"""Request isolation middleware"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging


class RequestIsolationMiddleware(BaseHTTPMiddleware):
    """Middleware to isolate requests with unique IDs"""
    
    async def dispatch(self, request: Request, call_next):
        """
        Add unique request ID to each request
        
        Args:
            request: Incoming request
            call_next: Next middleware/endpoint
            
        Returns:
            Response with request ID header
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Add to request state
        request.state.request_id = request_id
        
        # Add to logging context
        logger = logging.getLogger(__name__)
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.request_id = request_id
            return record
        
        logging.setLogRecordFactory(record_factory)
        
        try:
            # Process request
            response: Response = await call_next(request)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
        finally:
            # Restore original factory
            logging.setLogRecordFactory(old_factory)

