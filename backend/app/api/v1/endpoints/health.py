from fastapi import APIRouter
from app.schemas.response import APIResponse, create_response

router = APIRouter()

@router.get("", response_model=APIResponse)
async def health_check():
    return create_response(
        success=True,
        message="System is healthy",
        data={"api": "alive"},
        status_code=200
    )
