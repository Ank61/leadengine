"""
API endpoints for scrape job management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.db.session import get_db
from app.models import ScrapeJob
from app.schemas.scrape_job import ScrapeJobCreate, ScrapeJobResponse, ScrapeJobStatusResponse
from app.schemas.response import create_response
from app.mq.publisher import publish_scrape_job
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


@router.post("/scrape", response_model=ScrapeJobResponse, status_code=201)
async def create_scrape_job(
    job_request: ScrapeJobCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new scrape job and send it to the message queue
    
    This endpoint:
    1. Creates a new scrape job in the database with status 'queued'
    2. Sends the job details to RabbitMQ for processing
    3. Returns the created job details
    
    The worker will pick up the job from the queue and process it.
    """
    try:
        # Generate job ID
        job_id = uuid4()
        
        # Create job in database with status 'queued'
        scrape_job = ScrapeJob(
            id=job_id,
            user_id=job_request.user_id,
            status="queued",
            industry=job_request.industry,
            geography=job_request.geography,
            keywords=job_request.keywords,
            source_types=job_request.source_types,
            search_query=job_request.search_query,
            filters=job_request.filters,
            total_found=0,
            total_processed=0,
            created_at=datetime.utcnow()
        )
        
        db.add(scrape_job)
        db.commit()
        db.refresh(scrape_job)
        
        logger.info(
            "scrape_job_created",
            job_id=str(job_id),
            user_id=str(job_request.user_id),
            industry=job_request.industry,
            geography=job_request.geography,
            source_types=job_request.source_types
        )
        
        # Prepare message for queue
        message_payload = {
            "job_id": str(job_id),
            "user_id": str(job_request.user_id),
            "industry": job_request.industry,
            "geography": job_request.geography,
            "keywords": job_request.keywords or [],
            "source_types": job_request.source_types or [],
            "search_query": job_request.search_query,
            "filters": job_request.filters or {}
        }
        
        # Publish to RabbitMQ
        await publish_scrape_job(message_payload)
        
        logger.info(
            "scrape_job_queued",
            job_id=str(job_id)
        )
        
        # Return response
        return ScrapeJobResponse(
            job_id=scrape_job.id,
            user_id=scrape_job.user_id,
            status=scrape_job.status,
            industry=scrape_job.industry,
            geography=scrape_job.geography,
            keywords=scrape_job.keywords,
            source_types=scrape_job.source_types,
            search_query=scrape_job.search_query,
            filters=scrape_job.filters,
            total_found=scrape_job.total_found,
            total_processed=scrape_job.total_processed,
            created_at=scrape_job.created_at,
            started_at=scrape_job.started_at,
            completed_at=scrape_job.completed_at
        )
        
    except Exception as e:
        db.rollback()
        logger.error(
            "scrape_job_creation_failed",
            error=str(e),
            user_id=str(job_request.user_id)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create scrape job: {str(e)}"
        )


@router.get("/scrape/{job_id}", response_model=ScrapeJobStatusResponse)
def get_scrape_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the status of a scrape job by ID
    
    Returns the current status and progress of the scrape job.
    """
    try:
        job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Scrape job with ID {job_id} not found"
            )
        
        return ScrapeJobStatusResponse(
            job_id=job.id,
            status=job.status,
            total_found=job.total_found,
            total_processed=job.total_processed,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "get_job_status_failed",
            job_id=job_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/scrape/user/{user_id}")
def get_user_scrape_jobs(
    user_id: str,
    db: Session = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    """
    Get all scrape jobs for a specific user
    
    Returns a paginated list of scrape jobs for the user.
    """
    try:
        jobs = db.query(ScrapeJob).filter(
            ScrapeJob.user_id == user_id
        ).order_by(
            ScrapeJob.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        return {
            "user_id": user_id,
            "total": len(jobs),
            "jobs": [
                ScrapeJobStatusResponse(
                    job_id=job.id,
                    status=job.status,
                    total_found=job.total_found,
                    total_processed=job.total_processed,
                    created_at=job.created_at,
                    started_at=job.started_at,
                    completed_at=job.completed_at
                )
                for job in jobs
            ]
        }
        
    except Exception as e:
        logger.error(
            "get_user_jobs_failed",
            user_id=user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user jobs: {str(e)}"
        )
