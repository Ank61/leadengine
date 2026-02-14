from fastapi import APIRouter, HTTPException
from app.mq.connection import get_rabbitmq_connection
from app.schemas.response import APIResponse, create_response
from app.core.logging import logger

router = APIRouter()

@router.get("/mq-check", response_model=APIResponse)
async def mq_check():
    try:
        connection = await get_rabbitmq_connection()
        await connection.close()
        return create_response(
            success=True,
            message="RabbitMQ connection successful",
            data={"mq_status": "connected"},
            status_code=200
        )
    except Exception as e:
        logger.error("mq_check_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"RabbitMQ connection failed: {str(e)}")
