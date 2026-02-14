import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request start
        logger.info(
            "request_start",
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)

        process_time = time.time() - start_time
        
        # Log request end with duration
        logger.info(
            "request_end",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=f"{process_time:.4f}s",
        )

        return response
