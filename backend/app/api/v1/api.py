from fastapi import APIRouter
from app.api.v1.endpoints import mq, health, scrape_jobs

api_router = APIRouter()
api_router.include_router(health.router, prefix='/health', tags=['health'])
api_router.include_router(mq.router, prefix='/mq', tags=['mq'])
api_router.include_router(scrape_jobs.router, prefix='/jobs', tags=['scrape-jobs'])
