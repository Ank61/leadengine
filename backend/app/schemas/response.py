from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel
from fastapi.responses import JSONResponse

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    status_code: int

    class Config:
        arbitrary_types_allowed = True

def create_response(
    success: bool,
    message: str,
    data: Optional[Any] = None,
    status_code: int = 200,
) -> JSONResponse:
    content = APIResponse(
        success=success,
        message=message,
        data=data,
        status_code=status_code
    ).model_dump()
    return JSONResponse(status_code=status_code, content=content)
