from fastapi import FastAPI
from starlette.exceptions import HTTPException

from sqlalchemy import text
from app.db.session import engine
from app.api.v1.api import api_router
from app.core import logging
from app.core import exceptions
from app.core.middleware import LoggingMiddleware
from app.schemas.response import APIResponse, create_response
from starlette.middleware.cors import CORSMiddleware

# Initialize logging
logger = logging.setup_logging()

app = FastAPI(
    title="AI Lead Gen Backend",
    version="1.0.0",
    description="API for AI Lead Generation System",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
app.add_exception_handler(HTTPException, exceptions.http_exception_handler)
app.add_exception_handler(exceptions.RequestValidationError, exceptions.validation_exception_handler)
app.add_exception_handler(Exception, exceptions.global_exception_handler)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    logger.info("Application starting up")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Application shutting down")

@app.get("/db-check", tags=["system"], response_model=APIResponse)
def db_check():
    """
    Check database connection status
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            scalar_result = result.scalar()
            return create_response(
                success=True,
                message="Database connection successful",
                data={"db_status": scalar_result},
                status_code=200
            )
    except Exception as e:
        logger.error("db_check_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Database connection failed")
