from fastapi import Request
from starlette.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY

from app.schemas.response import APIResponse, create_response
from app.core.logging import logger

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle generic HTTP exceptions (404, 403, 401, etc.)
    """
    logger.error(
        "http_exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
    )
    return create_response(
        success=False,
        message=str(exc.detail),
        data=None,
        status_code=exc.status_code,
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors (pydantic/fastapi specific)
    """
    logger.error(
        "validation_error",
        errors=exc.errors(),
        path=request.url.path,
    )
    # Simplify validation errors into list of strings or keep generic
    details = exc.errors()
    
    return create_response(
        success=False,
        message="Validation error",
        data=details,
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
    )

async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle unhandled exceptions (500)
    """
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        exc_info=exc,
    )
    return create_response(
        success=False,
        message="Internal server error",
        data=None,
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )
